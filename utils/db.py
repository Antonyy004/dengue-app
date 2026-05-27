"""
utils/db.py — Koneksi Supabase & preprocessing data
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text


@st.cache_resource(show_spinner="Menghubungkan ke Supabase...")
def get_engine():
    try:
        cfg = st.secrets["supabase"]
        url = (
            f"postgresql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['db']}"
        )
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine, None
    except Exception as e:
        return None, str(e)


@st.cache_data(show_spinner="Memuat data dari Supabase...", ttl=3600)
def load_data():
    """
    Ambil semua tabel dari Supabase, lakukan preprocessing & merge.
    Return: (df_merge, error_string | None)
    """
    engine, err = get_engine()
    if err:
        return None, err

    tabel_list = [
        "tabel_penduduk",
        "tabel_sanitasi",
        "tabel_mobilitas",
        "tabel_dbd",
        "tabel_cuaca",
    ]

    data = {}
    try:
        for tbl in tabel_list:
            data[tbl] = pd.read_sql(f"SELECT * FROM {tbl}", engine)
    except Exception as e:
        return None, str(e)

    # Standardisasi kolom
    for df in data.values():
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    # Standardisasi nama provinsi
    for df in data.values():
        if "provinsi" in df.columns:
            df["provinsi"] = df["provinsi"].astype(str).str.title().str.strip()

    # Cleaning DBD
    df_dbd = data["tabel_dbd"].dropna(subset=["jumlah_kasus_bulat"])

    # Cleaning & agregasi cuaca
    df_cuaca = data["tabel_cuaca"].copy()
    for col in ["suhu", "kelembaban", "curah_hujan"]:
        df_cuaca[col] = df_cuaca.groupby("provinsi")[col].transform(
            lambda x: x.fillna(x.mean())
        )
    df_cuaca_tahun = (
        df_cuaca.groupby(["provinsi", "tahun"])
        .agg({"suhu": "mean", "kelembaban": "mean", "curah_hujan": "mean"})
        .reset_index()
    )

    # Merge semua tabel
    df = df_dbd.copy()
    for tbl, on in [
        ("tabel_penduduk", ["provinsi", "tahun"]),
        ("tabel_sanitasi",  ["provinsi", "tahun"]),
        ("tabel_mobilitas", ["provinsi", "tahun"]),
    ]:
        df = pd.merge(df, data[tbl], on=on, how="left")
    df = pd.merge(df, df_cuaca_tahun, on=["provinsi", "tahun"], how="left")

    # Handle missing value
    sanitasi_cols = [
        "persentase_akses_sanitasi_layak",
        "persentase_akses_air_layak",
        "persentase_layanan_sanitasi",
    ]
    for col in sanitasi_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    for col in ["persentase_mobilitas", "suhu", "kelembaban", "curah_hujan"]:
        if col in df.columns:
            df[col] = df.groupby("provinsi")[col].transform(
                lambda x: x.fillna(x.mean())
            )
            df[col] = df[col].fillna(df[col].mean())

    return df, None


def get_provinsi_list(df):
    return sorted(df["provinsi"].unique().tolist())


def get_tahun_list(df):
    return sorted(df["tahun"].unique().tolist())
