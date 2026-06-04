"""
app.py — Entry point DBD Disease Forecasting · Kelompok 4 DSGA
Jalankan: streamlit run app.py
"""

import warnings
import streamlit as st
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DBD Forecasting — Indonesia",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460; border-radius: 12px;
    padding: 20px; text-align: center; color: white;
}
.metric-card .label {
    font-size: 12px; color: #8892b0;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;
}
.metric-card .value {
    font-size: 28px; font-weight: 800;
    font-family: 'Syne', sans-serif; color: #64ffda;
}
.metric-card .sub { font-size: 11px; color: #8892b0; margin-top: 4px; }
.insight-box {
    border-left: 4px solid #64ffda; background: #0a192f;
    padding: 16px 20px; border-radius: 0 8px 8px 0;
    margin: 12px 0; color: #ccd6f6;
}
section[data-testid="stSidebar"] { background: #0a192f; }
section[data-testid="stSidebar"] * { color: #ccd6f6 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data & model (cached — load sekali, pakai di semua page) ─────────────
from utils.db import load_data
from utils.model import load_model_bundle

df_merge, data_error      = load_data()
model_bundle, model_error = load_model_bundle()

# =====================================
# NORMALISASI NAMA PROVINSI
# =====================================

if df_merge is not None and not df_merge.empty:

    province_mapping = {
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "DI Yogyakarta",
        "Daerah Istimewa Yogyakarta": "DI Yogyakarta"
    }

    df_merge["provinsi"] = (
        df_merge["provinsi"]
        .astype(str)
        .str.strip()
        .replace(province_mapping)
    )

has_data  = df_merge is not None and not df_merge.empty
has_model = model_bundle is not None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## DBD Forecasting")
    st.markdown("**Indonesia · 2020–2025**")

    if has_data:
        st.success("✅ Supabase terhubung")
    else:
        st.error("❌ Supabase tidak terhubung")

    if has_model:
        st.success("✅ Model dimuat")
    else:
        st.warning("⚠️ Model belum dimuat")

    st.divider()
    pages = [
        "Beranda",
        "Tren DBD",
        "Prediksi",
        "Faktor Eksternal",
        "Simulasi",
        "Analisis Provinsi",
        "Tentang Aplikasi"
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Beranda"

    page = st.radio(
        "Navigasi",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
    )

    st.session_state.page = page

    st.divider()

    if has_data and st.button("Refresh Data Supabase"):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        "<small style='color:#8892b0'>Kelompok 4 · DSGA<br>"
        "Dengue Disease Forecasting</small>",
        unsafe_allow_html=True,
    )

# ── Error banners ─────────────────────────────────────────────────────────────
if data_error:
    st.error(f"❌ **Gagal memuat data dari Supabase**: {data_error}")
    st.info("Pastikan kredensial Supabase sudah ada di `.streamlit/secrets.toml`.")

if model_error:
    st.warning(f"⚠️ **Model tidak dimuat**: {model_error}. "
               "Fitur prediksi tidak aktif.")


# ── Router ────────────────────────────────────────────────────────────────────
if not has_data:
    st.warning("⏳ Data belum tersedia — cek debug info di atas untuk detail error.")
    st.stop()

# Import app_pages hanya saat dibutuhkan (lazy import)
if page == "Beranda":
    from app_pages.beranda import show
    show(df_merge)

elif page == "Tren DBD":
    from app_pages.tren_dbd import show
    show(df_merge)

elif page == "Prediksi":
    if not has_model:
        st.warning("Model belum dimuat. Ikuti panduan export dari Colab.")
        st.stop()
    from app_pages.prediksi import show
    show(df_merge)

elif page == "Faktor Eksternal":
    if not has_model:
        st.warning("Model belum dimuat.")
        st.stop()
    from app_pages.faktor_eksternal import show
    show(df_merge)

elif page == "Simulasi":
    if not has_model:
        st.warning("Data atau model belum tersedia.")
        st.stop()
    from app_pages.simulasi import show
    show(df_merge)

elif page == "Analisis Provinsi":
    from app_pages.analisis_provinsi import show
    show(df_merge)

elif page == "Tentang Aplikasi":
    from app_pages.about import show
    show()