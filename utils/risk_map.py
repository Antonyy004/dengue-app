import json
import pandas as pd
import folium

from utils.capital_map import CAPITAL_MAP


# =====================================
# KATEGORI RISIKO
# =====================================

def classify_risk(cases):

    if cases < 1000:
        return "Aman"

    elif cases < 3000:
        return "Waspada"

    elif cases < 6000:
        return "Tinggi"

    else:
        return "Bahaya"


# =====================================
# WARNA RISIKO
# =====================================

def risk_color(risk):

    colors = {
        "Aman": "#22C55E",
        "Waspada": "#EAB308",
        "Tinggi": "#F97316",
        "Bahaya": "#DC2626"
    }

    return colors.get(risk, "#94A3B8")


# =====================================
# DATA RISIKO
# =====================================

def build_risk_dataframe(df_merge):

    latest_year = df_merge["tahun"].max()

    latest_df = df_merge[
        df_merge["tahun"] == latest_year
    ].copy()

    rows = []

    for _, row in latest_df.iterrows():

        provinsi = str(
            row["provinsi"]
        ).strip()

        province_mapping = {
            "Dki Jakarta": "DKI Jakarta",

            "Di Yogyakarta": "Daerah Istimewa Yogyakarta",
            "DI Yogyakarta": "Daerah Istimewa Yogyakarta",

            "Daerah Istimewa Yogyakarta": "Daerah Istimewa Yogyakarta"
        }

        provinsi = province_mapping.get(
            provinsi,
            provinsi
        )

        kasus = float(
            row["jumlah_kasus_bulat"]
        )

        rows.append({
            "provinsi": provinsi,
            "ibukota": CAPITAL_MAP.get(
                provinsi,
                "-"
            ),
            "prediksi_2026": kasus,
            "risiko": classify_risk(
                kasus
            )
        })

    return pd.DataFrame(rows)


# =====================================
# PETA RISIKO
# =====================================

def show_risk_map(
    df_merge,
    geojson_path
):

    risk_df = build_risk_dataframe(
        df_merge
    )

    with open(
        geojson_path,
        encoding="utf-8"
    ) as f:

        geojson_data = json.load(f)

    risk_lookup = {}

    for _, row in risk_df.iterrows():

        risk_lookup[
            row["provinsi"]
        ] = row

    m = folium.Map(
        location=[-2.5, 118],
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )

    def style_function(feature):

        province = feature[
            "properties"
        ]["PROVINSI"]

        if province in risk_lookup:

            risk = risk_lookup[
                province
            ]["risiko"]

            return {
                "fillColor": risk_color(
                    risk
                ),
                "color": "#111827",
                "weight": 1,
                "fillOpacity": 0.8
            }

        return {
            "fillColor": "#64748B",
            "color": "#111827",
            "weight": 1,
            "fillOpacity": 0.4
        }

    tooltip = folium.GeoJsonTooltip(
        fields=["PROVINSI"],
        aliases=["Provinsi"],
        sticky=True
    )

    geojson_layer = folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=tooltip,
        name="Risiko DBD"
    )

    geojson_layer.add_to(m)

    return m, risk_df