"""
utils/db.py — Koneksi Supabase SDK & preprocessing data
"""

import warnings
import streamlit as st
import pandas as pd
from supabase import create_client, Client

warnings.filterwarnings("ignore")


@st.cache_resource(show_spinner="Menghubungkan ke Supabase API...")
def get_supabase_client():
    """Inisialisasi Client Supabase SDK tanpa password DB"""
    try:
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        return supabase, None
    except Exception as e:
        return None, str(e)


@st.cache_data(show_spinner="Memuat data dari Supabase via API...", ttl=3600)
def load_data():
    """
    Ambil semua tabel dari Supabase SDK, lakukan preprocessing & merge.
    Return: (df_merge, error_string | None)
    """
    supabase, err = get_supabase_client()
    if err:
        return None, f"Gagal inisialisasi Client: {err}"

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
            # Mengambil data menggunakan SDK (.execute())
            response = supabase.table(tbl).select("*").execute()
            
            # Mengubah hasil JSON/List of Dict menjadi Pandas DataFrame
            data[tbl] = pd.DataFrame(response.data)
            
            # Validasi jika tabel ternyata kosong di database
            if data[tbl].empty:
                return None, f"Tabel '{tbl}' kosong di Supabase."
                
    except Exception as e:
        return None, f"Gagal mengambil tabel {tbl}: {str(e)}"

    # ── Logika Preprocessing & Cleaning (Tetap Sama dengan Kode Lamamu) ───────
    
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