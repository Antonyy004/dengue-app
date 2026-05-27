"""
utils/model.py — Load model bundle & semua fungsi prediksi
"""

import streamlit as st
import pandas as pd
import pickle


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


def predict_province(df_merge, provinsi, tahun_prediksi):
    from statsmodels.tsa.arima.model import ARIMA

    rf_models      = get_bundle("rf_models")
    xgb_models     = get_bundle("xgb_models")
    arima_models   = get_bundle("arima_models")
    sarima_models  = get_bundle("sarima_models")
    prophet_models = get_bundle("prophet_models")
    best_model_map = get_bundle("best_model_map")
    fitur_cols     = get_bundle("fitur_cols", [])
    prov_to_kode   = get_bundle("prov_to_kode")
    df_modeling    = get_bundle("df_modeling", pd.DataFrame())

    if provinsi not in best_model_map:
        return {"error": f"Provinsi '{provinsi}' tidak ada di model."}

    model_name = best_model_map[provinsi]
    series     = get_province_series(df_merge, provinsi)
    last_year  = series.index.max()
    steps      = tahun_prediksi - last_year

    if steps <= 0:
        return {"error": "Tahun prediksi harus lebih besar dari data terakhir."}

    try:
        if "ARIMA" in model_name and "Prophet" not in model_name:
            use_models = arima_models if "d=1" not in model_name else sarima_models
            m = use_models.get(provinsi)
            if m is None:
                return {"error": "Model ARIMA tidak tersedia."}
            p, d, q = m.order
            if len(series) < max(p, 1) + d + 1:
                return {"error": f"Data historis {provinsi} terlalu sedikit untuk ARIMA."}
            try:
                fitted = ARIMA(series, order=(p, d, q)).fit()
                pred   = max(0, fitted.forecast(steps=steps).iloc[-1])
            except Exception:
                pred = max(0, float(series.mean()) * 1.05)

        elif model_name == "Prophet":
            m = prophet_models.get(provinsi)
            if m is None:
                return {"error": "Model Prophet tidak tersedia."}
            future = m.make_future_dataframe(periods=steps, freq="YS")
            fc     = m.predict(future)
            pred   = max(0, fc[fc["ds"].dt.year == tahun_prediksi]["yhat"].values[0])

        elif model_name == "Random Forest":
            m    = rf_models.get(provinsi)
            if m is None:
                return {"error": "Model RF tidak tersedia."}
            kode = prov_to_kode[provinsi]
            df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
            X    = df_p[fitur_cols].values[-1].reshape(1, -1)
            pred = max(0, m.predict(X)[0])

        elif model_name == "XGBoost":
            m    = xgb_models.get(provinsi)
            if m is None:
                return {"error": "Model XGBoost tidak tersedia."}
            kode = prov_to_kode[provinsi]
            df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
            X    = df_p[fitur_cols].values[-1].reshape(1, -1)
            pred = max(0, m.predict(X)[0])

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
