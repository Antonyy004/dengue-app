"""
pages/faktor_eksternal.py — Analisis Feature Importance & AI Narrative
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, GRID_COL, TEXT_COL, DARK_BG
from utils.db import get_provinsi_list
from utils.model import (
    get_bundle,
    normalize_province_name
)

FITUR_LABEL = {
    "lag_t1"                         : "kasus tahun lalu",
    "lag_t2"                         : "kasus 2 tahun lalu",
    "lag_t3"                         : "kasus 3 tahun lalu",
    "rolling_mean_2"                 : "rata-rata 2 tahun terakhir",
    "rolling_mean_3"                 : "rata-rata 3 tahun terakhir",
    "growth_rate"                    : "laju pertumbuhan kasus",
    "curah_hujan"                    : "curah hujan",
    "suhu"                           : "suhu udara",
    "kelembaban"                     : "kelembaban udara",
    "persentase_mobilitas"           : "mobilitas penduduk",
    "persentase_akses_sanitasi_layak": "akses sanitasi layak",
    "persentase_akses_air_layak"     : "akses air bersih",
    "jumlah_penduduk"                : "kepadatan penduduk",
    "provinsi_encoded"               : "lokasi provinsi",
    "tahun"                          : "faktor waktu",
}

REKOMENDASI_MAP = {
    "curah_hujan"                    : "Tingkatkan kewaspadaan saat musim hujan dan pastikan drainase berfungsi baik.",
    "suhu"                           : "Monitor perubahan suhu dan korelasinya dengan siklus nyamuk Aedes aegypti.",
    "kelembaban"                     : "Kurangi area lembab yang berpotensi menjadi tempat berkembang biak nyamuk.",
    "persentase_mobilitas"           : "Pantau mobilitas penduduk antar wilayah terutama saat musim penularan tinggi.",
    "persentase_akses_sanitasi_layak": "Tingkatkan akses sanitasi layak untuk mengurangi risiko penyebaran DBD.",
    "persentase_akses_air_layak"     : "Perbaiki infrastruktur air bersih untuk mengurangi penampungan air terbuka.",
    "lag_t1"                         : "Lakukan evaluasi program pencegahan tahun lalu dan perkuat yang berhasil.",
    "jumlah_penduduk"                : "Fokuskan program pencegahan di area dengan kepadatan penduduk tinggi.",
}


def show(df_merge):
    st.title("🔬 Faktor yang Mempengaruhi Kasus DBD")
    st.caption("Analisis feature importance untuk memahami faktor-faktor utama yang mempengaruhi prediksi kasus DBD per provinsi.")

    st.markdown("""
    <div class="section-header"><div class="icon-badge">🔬</div> Pilih Provinsi & Parameter</div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        prov_opts = get_provinsi_list(df_merge)
        col1, col2 = st.columns([2, 1])
        with col1:
            prov_fi = st.selectbox("Provinsi", prov_opts)
            prov_fi_model = normalize_province_name(prov_fi)
            if st.session_state.get("last_faktor_prov") != prov_fi:
                st.session_state["last_faktor_prov"] = prov_fi
                st.session_state["show_faktor"] = False
        with col2:
            top_n = st.slider(
                "Jumlah faktor yang ditampilkan",
                3,
                15,
                10
            )

        if st.button("📊 Lihat Hasil Analisis", type="primary", use_container_width=True):
            st.session_state["show_faktor"] = True

    if not st.session_state.get("show_faktor", False):
        return

    rf_models      = get_bundle("rf_models")
    xgb_models     = get_bundle("xgb_models")
    best_model_map = get_bundle("best_model_map")
    fitur_cols     = get_bundle("fitur_cols", [])

    mn   = best_model_map.get(prov_fi_model, "")
    m_fi = None
    t_sfx = ""

    if mn == "Random Forest" and prov_fi_model in rf_models:
        m_fi, t_sfx = rf_models[prov_fi_model], "Random Forest"
    elif mn == "XGBoost" and prov_fi_model in xgb_models:
        m_fi, t_sfx = xgb_models[prov_fi_model], "XGBoost"
    elif prov_fi_model in rf_models:
        m_fi, t_sfx = rf_models[prov_fi_model], "Random Forest"
    elif prov_fi_model in xgb_models:
        m_fi, t_sfx = xgb_models[prov_fi_model], "XGBoost"

    if m_fi is None:
        st.warning("Data faktor yang mempengaruhi kasus DBD belum tersedia untuk provinsi ini.")
        return

    imp   = m_fi.feature_importances_
    fi_df = (
        pd.DataFrame({"Fitur": fitur_cols, "Score": imp})
        .sort_values("Score", ascending=False)
        .head(top_n)
    )

    fi_df["Label"] = (
        fi_df["Fitur"]
        .map(lambda x: FITUR_LABEL.get(x, x))
    )

    # ── Feature Importance Chart ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    bar_c = [ACCENT if i == 0 else GRID_COL for i in range(len(fi_df))]
    ax.barh(fi_df["Label"][::-1], fi_df["Score"][::-1], color=bar_c[::-1])
    ax.axvline(fi_df["Score"].mean(), color="#ff6b6b",
               linestyle="--", linewidth=1, label="Rata-rata")
    style_ax(
    ax,
    fig,
    f"Faktor yang Paling Berpengaruh terhadap Kasus DBD di {prov_fi}"
    )
    ax.set_xlabel("Tingkat Pengaruh")
    ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COL)
    st.pyplot(fig)
    plt.close()

    fi_df_display = fi_df.copy()

    fi_df_display["Fitur"] = (
        fi_df_display["Fitur"]
        .map(lambda x: FITUR_LABEL.get(x, x))
    )

    fi_df_display = fi_df_display.rename(
        columns={
            "Fitur": "Faktor",
            "Score": "Tingkat Pengaruh"
        }
    )

    st.dataframe(
        fi_df_display.reset_index(drop=True),
        use_container_width=True
    )

    st.divider()

# ── AI Narrative ──────────────────────────────────────────────────────────
    st.subheader("🤖 AI Ringkasan Hasil Analisis")

    df_prov    = df_merge[df_merge["provinsi"] == prov_fi].sort_values("tahun")
    top3_fitur = fi_df.head(3)["Fitur"].tolist()
    top3_score = fi_df.head(3)["Score"].tolist()
    top3_label = [FITUR_LABEL.get(f, f) for f in top3_fitur]

    # Siapkan data konteks
    tahun_max_prov  = int(df_prov["tahun"].max())
    kasus_last_prov = int(df_prov[df_prov["tahun"] == tahun_max_prov]["jumlah_kasus_bulat"].sum())

    nilai_top3 = []
    for fitur in top3_fitur:
        if fitur in df_prov.columns:
            val = df_prov[fitur].mean()
            nilai_top3.append(f"{FITUR_LABEL.get(fitur, fitur)}: {val:.2f}")

    # Baca API key
    from dotenv import load_dotenv
    import os
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_ai_narrative(prov_fi, top3_label, top3_score,
                              nilai_top3, kasus_last_prov,
                              tahun_max_prov, model_name, api_key):
        try:
            import google.generativeai as genai

            if not api_key:
                return None, "GEMINI_API_KEY tidak ditemukan"

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""Kamu adalah sistem analisis kesehatan masyarakat Indonesia
yang fokus pada penyakit DBD.

Berikan narasi analisis faktor eksternal dalam Bahasa Indonesia yang singkat,
jelas, dan mudah dipahami (3-4 kalimat). Langsung ke isi tanpa pembuka.

DATA PROVINSI {prov_fi}:
- Kasus DBD terakhir ({tahun_max_prov}): {kasus_last_prov:,} kasus
- Model prediksi: {model_name}
- Faktor paling berpengaruh: {top3_label[0]} ({top3_score[0]*100:.1f}%)
- Faktor kedua: {top3_label[1]} ({top3_score[1]*100:.1f}%)
- Faktor ketiga: {top3_label[2]} ({top3_score[2]*100:.1f}%)
- Nilai rata-rata faktor: {", ".join(nilai_top3)}

FORMAT OUTPUT:
- Kalimat 1: faktor dominan dan pengaruhnya terhadap DBD di provinsi ini
- Kalimat 2: hubungan faktor kedua dan ketiga dengan penyebaran DBD
- Kalimat 3: interpretasi kondisi aktual berdasarkan nilai rata-rata
- Kalimat 4: rekomendasi spesifik untuk provinsi ini

PENTING: jangan gunakan markdown seperti ** atau ##, tulis teks biasa saja."""

            response = model.generate_content(prompt)
            return response.text, None

        except Exception as e:
            return None, str(e)

    # Panggil AI
    with st.spinner("🤖 AI sedang menganalisis faktor yang mempengaruhi kasus DBD..."):
        ai_narrative, ai_error = generate_ai_narrative(
            prov_fi, top3_label, top3_score,
            nilai_top3, kasus_last_prov,
            tahun_max_prov, t_sfx, gemini_api_key
        )

    if ai_error:
        # Fallback ke narasi if-else
        historis_fitur = {"lag_t1", "lag_t2", "lag_t3",
                          "rolling_mean_2", "rolling_mean_3",
                          "growth_rate", "tahun"}

        if top3_fitur[0] in historis_fitur:
            narasi_pembuka = (
                f"Prediksi kasus DBD di {prov_fi} sangat dipengaruhi oleh "
                f"{top3_label[0]} ({top3_score[0]*100:.1f}%), "
                f"menunjukkan bahwa pola historis kasus merupakan prediktor utama."
            )
        else:
            narasi_pembuka = (
                f"Prediksi kasus DBD di {prov_fi} paling dipengaruhi oleh "
                f"{top3_label[0]} ({top3_score[0]*100:.1f}%), "
                f"menunjukkan peran besar faktor lingkungan terhadap penyebaran DBD."
            )

        narasi_faktor = (
            f"Faktor pendukung: {top3_label[1]} ({top3_score[1]*100:.1f}%) "
            f"dan {top3_label[2]} ({top3_score[2]*100:.1f}%)."
            if len(top3_label) >= 3 else ""
        )

        rekomendasi = REKOMENDASI_MAP.get(
            top3_fitur[0],
            "Pertahankan dan tingkatkan program pencegahan DBD yang sudah berjalan."
        )

        ai_narrative = f"{narasi_pembuka} {narasi_faktor} {rekomendasi}"
        st.caption(f"⚠️ AI tidak tersedia: {ai_error}")

    st.markdown(
        f"""<div class="insight-box">
        <strong>📍 Ringkasan Faktor yang Mempengaruhi Kasus DBD — {prov_fi}</strong><br><br>
        {ai_narrative}
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Keterangan fitur ──────────────────────────────────────────────────────
    st.subheader("📋 Keterangan Fitur")

    st.markdown("""
    | Faktor | Penjelasan |
    |---|---|
    | Kasus DBD tahun lalu | Jumlah kasus DBD pada tahun sebelumnya |
    | Kasus DBD 2 tahun lalu | Jumlah kasus DBD dua tahun sebelumnya |
    | Kasus DBD 3 tahun lalu | Jumlah kasus DBD tiga tahun sebelumnya |
    | Rata-rata kasus 2 tahun terakhir | Gambaran tren kasus dalam dua tahun terakhir |
    | Rata-rata kasus 3 tahun terakhir | Gambaran tren kasus dalam tiga tahun terakhir |
    | Perubahan jumlah kasus | Kenaikan atau penurunan kasus dibanding tahun sebelumnya |
    | Curah hujan | Curah hujan rata-rata di wilayah tersebut |
    | Suhu udara | Suhu udara rata-rata |
    | Kelembaban udara | Tingkat kelembaban udara |
    | Mobilitas penduduk | Tingkat aktivitas dan perpindahan masyarakat |
    | Akses sanitasi layak | Persentase masyarakat yang memiliki sanitasi yang baik |
    | Akses air bersih | Persentase masyarakat yang memiliki akses air bersih |
    | Jumlah penduduk | Total penduduk di provinsi tersebut |
    """)

    # =====================================================
    # EXPORT LAPORAN FAKTOR EKSTERNAL
    # =====================================================

    from utils.export_utils import (
        dataframe_to_csv,
        dataframe_to_excel,
        generate_pdf_via_api
    )

    st.divider()

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#0f172a,#1e293b);
    padding:25px;
    border-radius:18px;
    border:1px solid #06b6d4;
    margin-bottom:20px;
    box-shadow:0 0 25px rgba(6,182,212,.25);
    ">
    <h2 style="color:white;margin-bottom:10px;">
    📥 Unduh Laporan Faktor Penyebab DBD
    </h2>

    <p style="color:#e2e8f0;">
    Unduh hasil analisis faktor eksternal dalam format CSV, Excel, dan PDF.
    </p>

    </div>
    """, unsafe_allow_html=True)

    col_csv, col_excel, col_pdf = st.columns(3)

    # =====================================================
    # DATA EXPORT
    # =====================================================

    export_df = fi_df.copy()

    export_df["Provinsi"] = prov_fi
    export_df["Model"] = t_sfx

    # =====================================================
    # CSV
    # =====================================================

    with col_csv:

        st.markdown("""
        <div style="
        background:#14532d;
        padding:14px;
        border-radius:10px;
        color:white;
        font-weight:bold;
        ">
        📋 CSV
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇ Download CSV",
            dataframe_to_csv(export_df),
            f"faktor_eksternal_{prov_fi}.csv",
            "text/csv",
            use_container_width=True
        )

    # =====================================================
    # EXCEL
    # =====================================================

    with col_excel:

        st.markdown("""
        <div style="
        background:#1e3a5f;
        padding:14px;
        border-radius:10px;
        color:white;
        font-weight:bold;
        ">
        📊 Excel
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇ Download Excel",
            dataframe_to_excel(export_df),
            f"faktor_eksternal_{prov_fi}.xlsx",
            use_container_width=True
        )

    # =====================================================
    # PDF
    # =====================================================

    with col_pdf:

        st.markdown("""
        <div style="
        background:#4d4d00;
        padding:14px;
        border-radius:10px;
        color:white;
        font-weight:bold;
        ">
        📄 PDF
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "📄 Generate PDF Faktor Eksternal",
            use_container_width=True
        ):

            try:

                ranking_html = ""

                for _, row in fi_df.iterrows():

                    nama_faktor = FITUR_LABEL.get(
                        row["Fitur"],
                        row["Fitur"]
                    )

                    ranking_html += f"""
                    <tr>
                        <td>{nama_faktor.title()}</td>
                        <td>{row['Score']:.4f}</td>
                    </tr>
                    """

                fitur_desc_html = """
                <tr><td>Kasus tahun lalu</td><td>Jumlah kasus DBD pada tahun sebelumnya</td></tr>
                <tr><td>Kasus 2 tahun lalu</td><td>Jumlah kasus DBD dua tahun sebelumnya</td></tr>
                <tr><td>Kasus 3 tahun lalu</td><td>Jumlah kasus DBD tiga tahun sebelumnya</td></tr>
                <tr><td>Rata-rata 2 tahun terakhir</td><td>Gambaran tren kasus dalam dua tahun terakhir</td></tr>
                <tr><td>Rata-rata 3 tahun terakhir</td><td>Gambaran tren kasus dalam tiga tahun terakhir</td></tr>
                <tr><td>Perubahan jumlah kasus</td><td>Kenaikan atau penurunan kasus dibanding tahun sebelumnya</td></tr>
                <tr><td>Curah hujan</td><td>Curah hujan rata-rata di wilayah tersebut</td></tr>
                <tr><td>Suhu udara</td><td>Suhu udara rata-rata</td></tr>
                <tr><td>Kelembaban udara</td><td>Tingkat kelembaban udara</td></tr>
                <tr><td>Mobilitas penduduk</td><td>Tingkat aktivitas dan perpindahan masyarakat</td></tr>
                <tr><td>Akses sanitasi layak</td><td>Persentase masyarakat yang memiliki sanitasi yang baik</td></tr>
                <tr><td>Akses air bersih</td><td>Persentase masyarakat yang memiliki akses air bersih</td></tr>
                <tr><td>Jumlah penduduk</td><td>Total penduduk di provinsi tersebut</td></tr>
                """

                html = f"""

                <div class="section">

                <h3>🔬 Ringkasan Hasil Analisis</h3>

                <div class="card">

                <p><b>Provinsi:</b> {prov_fi}</p>
                <p><b>Metode Analisis:</b> {t_sfx}</p>
                <p><b>Faktor yang Paling Berpengaruh:</b>
                {FITUR_LABEL.get(fi_df.iloc[0]['Fitur'], fi_df.iloc[0]['Fitur']).title()}
                </p>
                <p><b>Tingkat Pengaruh:</b> {fi_df.iloc[0]['Score']:.4f}</p>

                </div>

                </div>

                <div class="section">

                <h3>📊 Peringkat Faktor yang Mempengaruhi Kasus DBD</h3>

                <table>

                <tr>
                    <th>Faktor</th>
                    <th>Tingkat Pengaruh</th>
                </tr>

                {ranking_html}

                </table>

                </div>

                <div class="section">

                <h3>🤖 Ringkasan Analisis Otomatis</h3>

                <div class="card">

                {ai_narrative}

                </div>

                </div>

                <div class="section">

                <h3>📋 Keterangan Fitur</h3>

                <table>

                <tr>
                    <th>Fitur</th>
                    <th>Keterangan</th>
                </tr>

                {fitur_desc_html}

                </table>

                </div>

                """

                pdf_bytes = generate_pdf_via_api(
                    title="Laporan Faktor Eksternal",
                    html_content=html,
                    footer_text=f"Sistem Prediksi Kasus DBD Indonesia - Faktor Eksternal - {prov_fi}"
                )

                st.session_state["faktor_pdf"] = pdf_bytes
            except Exception as e:

                st.error(
                    f"Gagal membuat PDF: {e}"
                )

            # =====================================================
            # DOWNLOAD PDF
            # =====================================================
            if "faktor_pdf" in st.session_state:

                st.download_button(
                    "⬇ Download PDF",
                    data=st.session_state["faktor_pdf"],
                    file_name=f"faktor_eksternal_{prov_fi}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf_faktor"
                )
