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
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-app: #0a0f1e;
    --bg-app-2: #0d1424;
    --bg-surface: #121a2e;
    --bg-surface-2: #1a2438;
    --border-c: rgba(148,163,184,0.10);
    --border-c-strong: rgba(148,163,184,0.20);
    --text-primary: #e8edf5;
    --text-secondary: #9aa8c2;
    --text-muted: #5f6f8e;
    --accent: #22d3ee;
    --accent-2: #818cf8;
    --accent-soft: rgba(34,211,238,0.12);
    --success: #34d399;
    --success-soft: rgba(52,211,153,0.12);
    --warning: #fbbf24;
    --warning-soft: rgba(251,191,36,0.12);
    --orange: #fb923c;
    --orange-soft: rgba(251,146,60,0.12);
    --danger: #f87171;
    --danger-soft: rgba(248,113,113,0.12);
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, h5 { font-family: 'Sora', sans-serif; letter-spacing: -0.01em; color: var(--text-primary) !important; }
h1 { font-weight: 800; font-size: 2.05rem; }

/* ── App background ─────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 15% -10%, #14213d 0%, var(--bg-app) 55%);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1300px; }

[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] label,
[data-testid="stMarkdownContainer"] { color: var(--text-secondary); }

hr { border-color: var(--border-c) !important; margin: 1.5rem 0 !important; }

/* ── Metric cards ───────────────────────────────────────────────── */
.metric-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-c);
    border-radius: var(--radius-lg);
    padding: 22px 20px;
    position: relative;
    overflow: hidden;
    transition: transform .2s ease, border-color .2s ease;
}
.metric-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
.metric-card:hover { transform: translateY(-3px); border-color: var(--border-c-strong); }
.metric-card .label {
    font-size: 11px; color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 600; margin-bottom: 8px;
}
.metric-card .value {
    font-size: 28px; font-weight: 800; font-family: 'Sora', sans-serif;
    color: var(--text-primary); line-height: 1.15;
}
.metric-card .sub { font-size: 12px; color: var(--text-secondary); margin-top: 6px; }

/* ── Insight box ────────────────────────────────────────────────── */
.insight-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-c);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 18px 22px; margin: 14px 0;
    color: var(--text-secondary); line-height: 1.7; font-size: 14.5px;
}

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton button, .stDownloadButton button {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #0a0f1e !important; font-weight: 700; border: none;
    border-radius: var(--radius-sm); padding: 0.55rem 1.2rem;
    transition: opacity .15s ease, transform .15s ease;
}
.stButton button:hover, .stDownloadButton button:hover { opacity: .88; transform: translateY(-1px); }

/* ── Selectbox / inputs ─────────────────────────────────────────── */
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    background: var(--bg-surface) !important;
    border-color: var(--border-c) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Alerts (st.success/info/warning/error) ────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-md);
    background: var(--bg-surface);
    border: 1px solid var(--border-c);
}
[data-testid="stAlert"] p { color: var(--text-secondary) !important; }

/* ── Tabs ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--border-c); }
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    color: var(--text-secondary); padding: 10px 18px;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important; border-bottom: 2px solid var(--accent);
}

/* ── Sidebar ────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-app-2);
    border-right: 1px solid var(--border-c);
}
section[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }

.brand-box {
    display: flex; align-items: center; gap: 12px;
    padding: 4px 0 18px 0; margin-bottom: 14px;
    border-bottom: 1px solid var(--border-c);
}
.brand-icon {
    font-size: 26px; width: 44px; height: 44px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: var(--accent-soft); border-radius: var(--radius-md);
}
.brand-title { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 17px; color: var(--text-primary) !important; }
.brand-sub { font-size: 12px; color: var(--text-muted) !important; }

.status-pill {
    display: flex; align-items: center; gap: 6px;
    font-size: 12.5px; font-weight: 500;
    padding: 8px 12px; border-radius: var(--radius-sm);
    margin-bottom: 6px; border: 1px solid var(--border-c);
}
.status-ok    { background: var(--success-soft); color: var(--success) !important; }
.status-warn  { background: var(--warning-soft); color: var(--warning) !important; }
.status-error { background: var(--danger-soft);  color: var(--danger) !important; }

.sidebar-section-label {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; color: var(--text-muted) !important;
    margin: 18px 0 8px 2px;
}

section[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 2px !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    gap: 10px;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    margin: 0 !important;
    border: 1px solid transparent;
    transition: background .15s ease, border-color .15s ease;
    cursor: pointer;
}
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    margin: 0 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    font-size: 14.5px;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: var(--bg-surface-2);
}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: var(--accent-soft); border-color: var(--accent);
}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: var(--accent) !important; font-weight: 700 !important;
}

.sidebar-footer {
    font-size: 11.5px; color: var(--text-muted) !important;
    line-height: 1.6; padding-top: 14px;
}
            
/* ── Section header (reusable) ─────────────────────────────────── */
.section-header {
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.25rem;
    color: var(--text-primary); margin: 28px 0 4px 0;
    display: flex; align-items: center; gap: 10px;
}
.section-header .icon-badge {
    display: flex; align-items: center; justify-content: center;
    width: 34px; height: 34px; border-radius: var(--radius-sm);
    background: var(--accent-soft); font-size: 16px; flex-shrink: 0;
}
.section-sub { color: var(--text-muted) !important; font-size: 13px; margin: 0 0 16px 0; }

/* ── Bordered containers (st.container(border=True)) ─────────────── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-c) !important;
    border-radius: var(--radius-lg) !important;
    padding: 18px !important;
}

/* ── Risk legend cards ─────────────────────────────────────────── */
.risk-card {
    border-radius: var(--radius-md);
    border: 1px solid var(--border-c);
    padding: 16px 18px;
    height: 100%;
}
.risk-card .risk-title {
    font-weight: 700; font-size: 14px; margin-bottom: 6px;
    display: flex; align-items: center; gap: 8px;
}
.risk-card .risk-desc { font-size: 12.5px; color: var(--text-secondary) !important; line-height: 1.6; }
.risk-card.risk-safe   { background: var(--success-soft); border-color: rgba(52,211,153,0.3); }
.risk-card.risk-safe   .risk-title { color: var(--success) !important; }
.risk-card.risk-watch  { background: var(--warning-soft); border-color: rgba(251,191,36,0.3); }
.risk-card.risk-watch  .risk-title { color: var(--warning) !important; }
.risk-card.risk-high   { background: var(--orange-soft); border-color: rgba(251,146,60,0.3); }
.risk-card.risk-high   .risk-title { color: var(--orange) !important; }
.risk-card.risk-danger { background: var(--danger-soft); border-color: rgba(248,113,113,0.3); }
.risk-card.risk-danger .risk-title { color: var(--danger) !important; }

/* ── Export panel ─────────────────────────────────────────────── */
.export-panel {
    padding: 24px; border-radius: var(--radius-lg);
    background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-surface-2) 100%);
    border: 1px solid var(--border-c);
    margin: 8px 0 20px 0;
}
.export-panel h3 { margin: 0 0 6px 0 !important; font-size: 19px; }
.export-panel p { margin: 0 !important; font-size: 13.5px; }

.export-card {
    border: 1px solid var(--border-c); border-radius: var(--radius-md);
    padding: 12px 16px; margin-bottom: 10px; text-align: center;
    font-weight: 700; font-size: 13.5px;
}
.export-card.export-csv   { background: var(--success-soft); color: var(--success) !important; }
.export-card.export-excel { background: var(--accent-soft);  color: var(--accent) !important; }
.export-card.export-pdf   { background: var(--warning-soft); color: var(--warning) !important; }
.stButton button p,
.stButton button div,
.stDownloadButton button p,
.stDownloadButton button div {
    color: #0a0f1e !important;
    font-weight: 700 !important;
}
            
.province-header {
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.05rem;
    color: var(--text-primary) !important; margin: 4px 0 14px 0;
    display: flex; align-items: center; gap: 8px;
}
.province-header .icon-badge-sm {
    display: flex; align-items: center; justify-content: center;
    width: 28px; height: 28px; border-radius: var(--radius-sm);
    background: var(--accent-soft); font-size: 13px; flex-shrink: 0;
}

</style>
""", unsafe_allow_html=True)

# ── Cek Login ─────────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    from app_pages.login import show as show_login
    show_login()
    st.stop()

user = st.session_state["user"]
role = user.get("role", "viewer")

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
    role_badge = {"admin": ("🔴","Admin"), "researcher": ("🟡","Researcher"), "viewer": ("🔵","Viewer")}.get(role, ("⚪", role))
    st.markdown(f"""
    <div class="status-pill status-ok" style="margin-bottom:14px;">
        <span>{role_badge[0]} {user['nama']} · <b>{role_badge[1]}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Navigasi</div>', unsafe_allow_html=True)

    all_pages = {
        "Beranda":           ["admin", "researcher", "viewer"],
        "Tren DBD":          ["admin", "researcher", "viewer"],
        "Prediksi":          ["admin", "researcher"],
        "Faktor Eksternal":  ["admin", "researcher"],
        "Simulasi":          ["admin", "researcher"],
        "Analisis Provinsi": ["admin", "researcher", "viewer"],
        "Tentang Aplikasi":  ["admin", "researcher", "viewer"],
        "Kelola User":       ["admin"],
    }
    pages = [p for p, roles in all_pages.items() if role in roles]

    if "page" not in st.session_state or st.session_state.page not in pages:
        st.session_state.page = "Beranda"

    page = st.radio("Navigasi", pages,
                    index=pages.index(st.session_state.page),
                    label_visibility="collapsed")
    st.session_state.page = page

    st.markdown('<div class="sidebar-section-label">Data</div>', unsafe_allow_html=True)
    if has_data and st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="sidebar-section-label">Akun</div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Error banners ─────────────────────────────────────────────────────────────
if data_error:
    st.error(f"❌ **Gagal memuat data**: {data_error}")
    st.info("Pastikan dataset sudah tersedia.")

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

elif page == "Kelola User":
    from app_pages.admin_users import show
    show()