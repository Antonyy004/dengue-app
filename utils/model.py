"""
utils/model.py — Load model bundle & semua fungsi prediksi
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import re


def normalize_province_name(provinsi):
    mapping = {
        "DKI Jakarta": "Dki Jakarta",
        "DI Yogyakarta": "Di Yogyakarta",
        "Daerah Istimewa Yogyakarta": "Di Yogyakarta"
    }
    return mapping.get(str(provinsi).strip(), str(provinsi).strip())


@st.cache_resource(show_spinner="Memuat model...")
def load_model_bundle():
    try:
        with open("models/model_bundle.pkl", "rb") as f:
            bundle = pickle.load(f)
        return bundle, None
    except FileNotFoundError:
        return None, "model_bundle.pkl tidak ditemukan."
    except Exception as e:
        return None, str(e)


def get_bundle(key, default={}):
    bundle, _ = load_model_bundle()
    if bundle is None:
        return default
    return bundle.get(key, default)


def get_province_series(df_merge, provinsi):
    return (
        df_merge[df_merge["provinsi"] == provinsi]
        .groupby("tahun")["jumlah_kasus_bulat"]
        .sum()
        .sort_index()
    )


def parse_arima_order(model_name):
    match = re.search(r'\((\d+),\s*(\d+),\s*(\d+)\)', model_name)
    if match:
        return tuple(int(x) for x in match.groups())
    return None


def predict_province(df_merge, provinsi, tahun_prediksi):
    from statsmodels.tsa.arima.model import ARIMA
    from prophet import Prophet

    provinsi = normalize_province_name(provinsi)

    rf_models      = get_bundle("rf_models")
    xgb_models     = get_bundle("xgb_models")
    arima_models   = get_bundle("arima_models")
    sarima_models  = get_bundle("sarima_models")
    prophet_models = get_bundle("prophet_models")
    mlp_models     = get_bundle("mlp_models")
    mlp_scalers    = get_bundle("mlp_scalers")
    best_model_map = get_bundle("best_model_map")
    fitur_cols     = list(get_bundle("fitur_cols", []))
    prov_to_kode   = get_bundle("prov_to_kode")
    df_modeling    = get_bundle("df_modeling", pd.DataFrame())

    if provinsi not in best_model_map:
        return {"error": f"Provinsi '{provinsi}' tidak ada di model."}

    model_name = best_model_map[provinsi]
    series     = get_province_series(df_merge, provinsi)
    train      = series[series.index <= 2024]
    last_train_year = int(train.index.max())
    steps = tahun_prediksi - last_train_year

    if steps <= 0:
        return {"error": f"Tahun prediksi ({tahun_prediksi}) harus > {last_train_year}."}

    train_vals = train.values.astype(float)

    is_sarima  = model_name.startswith('ARIMA(d=1)')
    is_arima   = model_name.startswith('ARIMA') and not is_sarima and 'Prophet' not in model_name
    is_prophet = model_name == 'Prophet'
    is_rf      = model_name == 'Random Forest'
    is_xgb     = model_name == 'XGBoost'
    is_mlp     = 'MLP' in model_name or 'ANN' in model_name

    try:
        # ── ARIMA ────────────────────────────────────────────────
        if is_arima:
            order = parse_arima_order(model_name)
            if order is None:
                return {"error": f"Tidak bisa parse order dari '{model_name}'."}
            if order == (0, 0, 0):
                x      = np.arange(len(train_vals), dtype=float)
                coeffs = np.polyfit(x, train_vals, 1)
                pred   = max(0.0, float(np.polyval(coeffs, len(train_vals) - 1 + steps)))
            else:
                fitted = ARIMA(train_vals, order=order).fit()
                fc     = fitted.forecast(steps=steps)
                pred   = max(0.0, float(fc.iloc[-1] if hasattr(fc, 'iloc') else fc[-1]))

        # ── SARIMA ───────────────────────────────────────────────
        elif is_sarima:
            order = parse_arima_order(model_name)
            if order is None:
                return {"error": f"Tidak bisa parse order dari '{model_name}'."}
            fitted = ARIMA(train_vals, order=order).fit()
            fc     = fitted.forecast(steps=steps)
            pred   = max(0.0, float(fc.iloc[-1] if hasattr(fc, 'iloc') else fc[-1]))

        # ── Prophet ──────────────────────────────────────────────
        elif is_prophet:
            m = prophet_models.get(provinsi)
            if m is None:
                return {"error": "Model Prophet tidak tersedia."}
            future = m.make_future_dataframe(periods=steps, freq="YS")
            fc     = m.predict(future)
            row    = fc[fc["ds"].dt.year == tahun_prediksi]
            if len(row) == 0:
                return {"error": f"Prophet tidak bisa prediksi tahun {tahun_prediksi}."}
            pred = max(0.0, float(row["yhat"].values[0]))

        # ── Random Forest / XGBoost — ITERATIVE + TREND BLEND ───
        elif is_rf or is_xgb:
            m = rf_models.get(provinsi) if is_rf else xgb_models.get(provinsi)
            if m is None:
                return {"error": f"Model {'RF' if is_rf else 'XGBoost'} tidak tersedia."}

            kode = prov_to_kode.get(provinsi)
            if kode is None:
                return {"error": "Kode provinsi tidak ditemukan."}

            df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
            if len(df_p) == 0:
                return {"error": "Tidak ada data untuk provinsi ini."}

            historical    = list(df_p["jumlah_kasus_bulat"].values.astype(float))
            last_tahun    = int(df_p["tahun"].iloc[-1])
            steps_ml      = tahun_prediksi - last_tahun

            if steps_ml <= 0:
                return {"error": f"Tahun prediksi ({tahun_prediksi}) harus > {last_tahun}."}

            x_hist       = np.arange(len(historical), dtype=float)
            trend_coeffs = np.polyfit(x_hist, historical, 1)

            pred = 0.0
            current_tahun = last_tahun

            for step_i in range(steps_ml):
                current_tahun += 1
                last_row = df_p[fitur_cols].iloc[-1].copy().astype(float)

                last_row["tahun"]  = float(current_tahun)
                last_row["lag_t1"] = historical[-1]
                last_row["lag_t2"] = historical[-2] if len(historical) >= 2 else historical[-1]
                last_row["lag_t3"] = historical[-3] if len(historical) >= 3 else historical[-1]

                if "rolling_mean_2" in fitur_cols:
                    last_row["rolling_mean_2"] = (float(np.mean(historical[-2:]))
                                                  if len(historical) >= 2 else historical[-1])
                if "rolling_mean_3" in fitur_cols:
                    last_row["rolling_mean_3"] = (float(np.mean(historical[-3:]))
                                                  if len(historical) >= 3 else historical[-1])
                if "growth_rate" in fitur_cols:
                    l1 = historical[-1]
                    l2 = historical[-2] if len(historical) >= 2 else historical[-1]
                    last_row["growth_rate"] = (l1 - l2) / l2 if l2 != 0 else 0.0
                if "growth_accel" in fitur_cols:
                    l1  = historical[-1]
                    l2  = historical[-2] if len(historical) >= 2 else historical[-1]
                    l3  = historical[-3] if len(historical) >= 3 else historical[-1]
                    gr1 = (l1 - l2) / l2 if l2 != 0 else 0.0
                    gr2 = (l2 - l3) / l3 if l3 != 0 else 0.0
                    last_row["growth_accel"] = gr1 - gr2

                X = last_row.values.reshape(1, -1)
                ml_pred = max(0.0, float(m.predict(X)[0]))

                future_idx  = len(historical) + step_i
                trend_pred  = max(0.0, float(np.polyval(trend_coeffs, future_idx)))
                step_pred   = 0.70 * ml_pred + 0.30 * trend_pred

                historical.append(step_pred)
                pred = step_pred

        # ── MLP — ITERATIVE ──────────────────────────────────────
        elif is_mlp:
            m      = mlp_models.get(provinsi)
            scaler = mlp_scalers.get(provinsi)
            if m is None or scaler is None:
                return {"error": "Model MLP tidak tersedia."}

            kode = prov_to_kode.get(provinsi)
            if kode is None:
                return {"error": "Kode provinsi tidak ditemukan."}

            df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
            if len(df_p) == 0:
                return {"error": "Tidak ada data untuk provinsi ini."}

            hist_vals  = list(df_p["jumlah_kasus_bulat"].values.astype(float))
            last_tahun = int(df_p["tahun"].iloc[-1])
            steps_ml   = tahun_prediksi - last_tahun

            if steps_ml <= 0:
                return {"error": f"Tahun prediksi ({tahun_prediksi}) harus > {last_tahun}."}

            pred = 0.0
            current_tahun = last_tahun

            for _ in range(steps_ml):
                current_tahun += 1
                row = df_p[fitur_cols].iloc[-1].copy().astype(float)

                row["tahun"]  = float(current_tahun)
                row["lag_t1"] = hist_vals[-1]
                row["lag_t2"] = hist_vals[-2] if len(hist_vals) >= 2 else hist_vals[-1]
                row["lag_t3"] = hist_vals[-3] if len(hist_vals) >= 3 else hist_vals[-1]

                if "rolling_mean_2" in fitur_cols:
                    row["rolling_mean_2"] = (float(np.mean(hist_vals[-2:]))
                                             if len(hist_vals) >= 2 else hist_vals[-1])
                if "rolling_mean_3" in fitur_cols:
                    row["rolling_mean_3"] = (float(np.mean(hist_vals[-3:]))
                                             if len(hist_vals) >= 3 else hist_vals[-1])
                if "growth_rate" in fitur_cols:
                    l1 = hist_vals[-1]
                    l2 = hist_vals[-2] if len(hist_vals) >= 2 else hist_vals[-1]
                    row["growth_rate"] = (l1 - l2) / l2 if l2 != 0 else 0.0
                if "growth_accel" in fitur_cols:
                    l1  = hist_vals[-1]
                    l2  = hist_vals[-2] if len(hist_vals) >= 2 else hist_vals[-1]
                    l3  = hist_vals[-3] if len(hist_vals) >= 3 else hist_vals[-1]
                    gr1 = (l1 - l2) / l2 if l2 != 0 else 0.0
                    gr2 = (l2 - l3) / l3 if l3 != 0 else 0.0
                    row["growth_accel"] = gr1 - gr2

                X_scaled  = scaler.transform(row.values.reshape(1, -1))
                step_pred = max(0.0, float(m.predict(X_scaled)[0]))

                hist_vals.append(step_pred)
                pred = step_pred

        else:
            return {"error": f"Model '{model_name}' tidak dikenali."}

    except Exception as e:
        return {"error": str(e)}

    return {
        "provinsi"       : provinsi,
        "tahun_prediksi" : tahun_prediksi,
        "prediksi_kasus" : int(round(pred)),
        "model_digunakan": model_name,
    }


def generate_insight(df_merge, provinsi, tahun_prediksi):
    series          = get_province_series(df_merge, provinsi)
    aktual_terakhir = int(series.iloc[-1])
    tahun_terakhir  = int(series.index[-1])
    result          = predict_province(df_merge, provinsi, tahun_prediksi)

    if "error" in result:
        return result

    prediksi = result["prediksi_kasus"]
    selisih  = prediksi - aktual_terakhir
    persen   = (selisih / aktual_terakhir * 100) if aktual_terakhir > 0 else 0

    if persen > 10:
        status, color = "🔴 NAIK SIGNIFIKAN", "#ff4444"
        saran = "Waspadai peningkatan kasus. Perlu penguatan pencegahan dan kesiapan fasilitas kesehatan."
    elif persen > 0:
        status, color = "🟡 NAIK SEDIKIT", "#ffaa00"
        saran = "Tren kasus sedikit meningkat. Monitor kondisi cuaca dan sanitasi."
    elif persen > -10:
        status, color = "🟢 STABIL / TURUN SEDIKIT", "#00cc88"
        saran = "Kasus relatif stabil. Pertahankan program pencegahan yang berjalan."
    else:
        status, color = "🟢 TURUN SIGNIFIKAN", "#00cc88"
        saran = "Tren positif — kasus diprediksi menurun. Evaluasi faktor keberhasilan untuk direplikasi."

    return dict(
        provinsi=provinsi, tahun_acuan=tahun_terakhir, tahun_prediksi=tahun_prediksi,
        aktual=aktual_terakhir, prediksi=prediksi, selisih=selisih,
        persen=persen, status=status, color=color, saran=saran,
        model=result["model_digunakan"],
    )


def simulasi_prediksi(provinsi, **kwargs):
    provinsi = normalize_province_name(provinsi)
    rf_models    = get_bundle("rf_models")
    xgb_models   = get_bundle("xgb_models")
    fitur_cols   = list(get_bundle("fitur_cols", []))
    prov_to_kode = get_bundle("prov_to_kode")
    df_modeling  = get_bundle("df_modeling", pd.DataFrame())

    if provinsi in rf_models:
        model, model_name = rf_models[provinsi], "Random Forest"
    elif provinsi in xgb_models:
        model, model_name = xgb_models[provinsi], "XGBoost"
    else:
        return {"error": f"Model RF/XGB tidak tersedia untuk {provinsi}."}

    kode = prov_to_kode.get(provinsi)
    if kode is None:
        return {"error": f"Provinsi '{provinsi}' tidak ditemukan."}

    df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
    if df_p.empty:
        return {"error": f"Data modeling tidak tersedia untuk {provinsi}."}

    X_base = df_p[fitur_cols].values[-1].astype(float).copy()
    X_sim  = X_base.copy()

    perubahan_log = []
    for var, val in kwargs.items():
        if var in fitur_cols:
            idx        = fitur_cols.index(var)
            nilai_lama = X_base[idx]
            X_sim[idx] = float(val)
            perubahan_log.append(f"{var}: {nilai_lama:.2f} → {float(val):.2f}")

    try:
        pred_base = max(0, float(model.predict(X_base.reshape(1, -1))[0]))
        pred_sim  = max(0, float(model.predict(X_sim.reshape(1, -1))[0]))
    except Exception as e:
        return {"error": str(e)}

    selisih = pred_sim - pred_base
    persen  = (selisih / pred_base * 100) if pred_base > 0 else 0

    return dict(
        baseline=int(round(pred_base)),
        simulasi=int(round(pred_sim)),
        selisih=int(round(selisih)),
        persen=round(persen, 2),
        model=model_name,
        log=perubahan_log,
    )