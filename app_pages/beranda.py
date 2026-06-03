"""
pages/beranda.py — Halaman Beranda: ringkasan statistik nasional
"""

import streamlit as st
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, GRID_COL, TEXT_COL, DARK_BG
from utils.risk_map import show_risk_map
from streamlit_folium import st_folium

def show(df_merge):
    st.title("🦟 Sistem Prediksi Kasus DBD Indonesia")

    st.markdown(
        "### 🗺️ Peta Risiko DBD Indonesia 2026"
    )

    map_obj, risk_df = show_risk_map(
        df_merge,
        "assets\indonesia_provinces.geojson.json"
    )

    st_folium(
        map_obj,
        width=1200,
        height=650
    )
    st.info("""
    💡 **Interpretasi Peta Risiko**

    Peta ini menampilkan tingkat risiko DBD setiap provinsi berdasarkan hasil analisis dan prediksi sistem untuk tahun 2026.

    Warna provinsi menunjukkan tingkat risiko relatif yang dapat digunakan sebagai dasar pemantauan, perencanaan intervensi, dan pengambilan keputusan dalam pengendalian DBD di Indonesia.
    """)
    st.markdown("### 📖 Keterangan Tingkat Risiko")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.success(
            """
    🟢 **AMAN**

    Risiko DBD rendah.

    Wilayah relatif terkendali dan tidak menunjukkan potensi peningkatan kasus yang signifikan.
    """
        )

    with col2:
        st.warning(
            """
    🟡 **WASPADA**

    Risiko DBD sedang.

    Perlu peningkatan kewaspadaan karena terdapat potensi kenaikan kasus.
    """
        )

    with col3:
        st.warning(
            """
    🟠 **TINGGI**

    Risiko DBD tinggi.

    Diperlukan pemantauan intensif dan upaya pencegahan yang lebih aktif.
    """
        )

    with col4:
        st.error(
            """
    🔴 **BAHAYA**

    Risiko DBD sangat tinggi.

    Wilayah memiliki potensi kejadian luar biasa (KLB) dan memerlukan tindakan segera.
    """
        )
    selected_province = st.selectbox(
        "📍 Pilih provinsi untuk dianalisis lebih lanjut",
        sorted(risk_df["provinsi"].unique())
    )

    if st.button(
        "🔍 Lihat Analisis Provinsi"
    ):

        st.session_state[
            "selected_province"
        ] = selected_province

        st.session_state[
            "page"
        ] = "Analisis Provinsi"

        st.rerun()

    st.markdown(
        "Ringkasan statistik nasional berdasarkan data real-time dari Supabase."
    )
    # ── Hitung statistik ─────────────────────────────────────────────────────
    total_kasus  = int(df_merge["jumlah_kasus_bulat"].sum())
    top_provinsi = df_merge.groupby("provinsi")["jumlah_kasus_bulat"].sum().idxmax()
    tahun_max    = int(df_merge["tahun"].max())
    kasus_max    = int(df_merge[df_merge["tahun"] == tahun_max]["jumlah_kasus_bulat"].sum())
    kasus_prev   = int(df_merge[df_merge["tahun"] == tahun_max - 1]["jumlah_kasus_bulat"].sum())
    pct          = ((kasus_max - kasus_prev) / kasus_prev * 100) if kasus_prev > 0 else 0
    tren_label   = f"{'▲' if pct > 0 else '▼'} {abs(pct):.1f}%"

    # ── 4 Metric Cards ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub in [
        (c1, "Total Kasus Nasional", f"{total_kasus:,}",  "2020–2025"),
        (c2, "Provinsi Tertinggi",   top_provinsi,         "akumulasi"),
        (c3, "Tahun Terakhir",       str(tahun_max),       f"{kasus_max:,} kasus"),
        (c4, "Tren YoY",             tren_label,           "vs tahun sebelumnya"),
    ]:
        col.markdown(
            f"""<div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="sub">{sub}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

# ── AI National Summary ───────────────────────────────────────────────────
    st.subheader("🤖 AI National Summary")

    # Hitung provinsi naik/turun
    prov_naik, prov_turun = [], []
    for prov in df_merge["provinsi"].unique():
        df_p            = df_merge[df_merge["provinsi"] == prov].sort_values("tahun")
        tahun_list_prov = df_p["tahun"].unique()
        if len(tahun_list_prov) >= 2:
            k_last = df_p[df_p["tahun"] == tahun_list_prov[-1]]["jumlah_kasus_bulat"].sum()
            k_prev = df_p[df_p["tahun"] == tahun_list_prov[-2]]["jumlah_kasus_bulat"].sum()
            if k_prev > 0:
                delta = (k_last - k_prev) / k_prev * 100
                if delta > 10:
                    prov_naik.append((prov, round(delta, 1)))
                elif delta < -10:
                    prov_turun.append((prov, round(delta, 1)))

    prov_naik.sort(key=lambda x: x[1], reverse=True)
    prov_turun.sort(key=lambda x: x[1])

    prov_naik_str  = ", ".join([f"{p} (+{d}%)" for p, d in prov_naik[:5]])  or "tidak ada"
    prov_turun_str = ", ".join([f"{p} ({d}%)"  for p, d in prov_turun[:5]]) or "tidak ada"

    # Baca API key di luar fungsi cache
    from dotenv import load_dotenv
    import os

    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_ai_summary(tahun_max, kasus_max, pct,
                            prov_naik_str, prov_turun_str,
                            top_provinsi, api_key):
        try:
            import google.generativeai as genai

            if not api_key:
                return None, "GEMINI_API_KEY tidak ditemukan di secrets.toml"

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""Kamu adalah sistem analisis kesehatan masyarakat Indonesia
yang fokus pada penyakit DBD (Demam Berdarah Dengue).

Buat ringkasan analisis nasional dalam Bahasa Indonesia yang singkat dan informatif
(3-4 kalimat). Langsung ke isi tanpa pembuka seperti "Berdasarkan data".

DATA:
- Tahun analisis: {tahun_max}
- Total kasus nasional: {kasus_max:,} kasus
- Perubahan vs tahun lalu: {pct:+.1f}%
- Provinsi kasus tertinggi: {top_provinsi}
- Provinsi kenaikan signifikan (>10%): {prov_naik_str}
- Provinsi penurunan signifikan (>10%): {prov_turun_str}

FORMAT OUTPUT (ikuti persis):
- Kalimat 1: kondisi nasional secara umum (naik/turun/stabil + angka)
- Kalimat 2: provinsi yang perlu perhatian khusus
- Kalimat 3: provinsi dengan tren positif jika ada, kalau tidak ada skip
- Kalimat 4: rekomendasi singkat untuk pengambil keputusan

PENTING: jangan gunakan markdown seperti ** atau ##, tulis teks biasa saja."""

            response = model.generate_content(prompt)
            return response.text, None

        except Exception as e:
            return None, str(e)

    # Panggil AI
    with st.spinner("🤖 AI sedang menganalisis data..."):
        ai_text, ai_error = generate_ai_summary(
            tahun_max, kasus_max, pct,
            prov_naik_str, prov_turun_str,
            top_provinsi, gemini_api_key
        )

    # Tentukan warna border berdasarkan tren
    if pct > 10:
        trend_color = "#c8502a"
    elif pct < -10:
        trend_color = "#2a8c5a"
    else:
        trend_color = "#c8960a"

    if ai_error:
        # Fallback ke teks otomatis kalau AI gagal
        if pct > 10:
            trend_teks = f"📈 meningkat {pct:.1f}%"
        elif pct < -10:
            trend_teks = f"📉 menurun {abs(pct):.1f}%"
        else:
            trend_teks = f"➡️ relatif stabil ({pct:+.1f}%)"

        ai_text = (
            f"Secara nasional, kasus DBD pada {tahun_max} {trend_teks} "
            f"dibandingkan tahun sebelumnya dengan total {kasus_max:,} kasus. "
            f"Terdapat {len(prov_naik)} provinsi dengan peningkatan signifikan, "
            f"tertinggi di {prov_naik_str.split(',')[0]}."
        )
        st.caption(f"⚠️ AI tidak tersedia: {ai_error}")

    st.markdown(
        f"""<div class="insight-box" style="border-left-color:{trend_color}">
        {ai_text}
        </div>""",
        unsafe_allow_html=True,
    )

    # Provinsi risiko tinggi
    if prov_naik:
        st.markdown("**⚠️ Provinsi dengan peningkatan kasus tertinggi:**")
        cols = st.columns(min(len(prov_naik), 4))
        for i, (prov, delta) in enumerate(prov_naik[:4]):
            cols[i].markdown(
                f"""<div class="metric-card">
                    <div class="label">{prov}</div>
                    <div class="value" style="color:#c8502a">+{delta:.1f}%</div>
                    <div class="sub">vs tahun sebelumnya</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Grafik tren nasional & Top 10 ─────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Tren Nasional")
        trend = df_merge.groupby("tahun")["jumlah_kasus_bulat"].sum()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.fill_between(trend.index, trend.values, alpha=0.15, color=ACCENT)
        ax.plot(trend.index, trend.values, marker="o", linewidth=2.5,
                color=ACCENT, markersize=8)
        style_ax(ax, fig, "Kasus DBD Nasional per Tahun")
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Jumlah Kasus")
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.subheader("Top 10 Provinsi")
        top10 = (
            df_merge.groupby("provinsi")["jumlah_kasus_bulat"]
            .sum().sort_values(ascending=False).head(10)
        )
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        bar_colors = [ACCENT if i == 0 else GRID_COL for i in range(len(top10))]
        ax2.bar(top10.index, top10.values, color=bar_colors)
        style_ax(ax2, fig2, "10 Provinsi Kasus Tertinggi")
        ax2.set_ylabel("Total Kasus")
        plt.xticks(rotation=40, ha="right", color=TEXT_COL, fontsize=8)
        st.pyplot(fig2)
        plt.close()
