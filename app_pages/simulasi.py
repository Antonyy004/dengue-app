"""
pages/simulasi.py — Simulasi variabel & Policy Impact Analysis
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, TEXT_COL, DARK_BG
from utils.db import get_provinsi_list
from utils.model import (
    get_bundle,
    simulasi_prediksi,
    normalize_province_name
)

SIM_VARS = [
    ("curah_hujan",                     "🌧️ Curah Hujan (mm)",    0.0,  600.0, 200.0),
    ("suhu",                            "🌡️ Suhu (°C)",           20.0,  40.0,  28.0),
    ("kelembaban",                      "💧 Kelembaban (%)",       40.0, 100.0,  75.0),
    ("persentase_mobilitas",            "🚗 Mobilitas (%)",         0.0, 100.0,  60.0),
    ("persentase_akses_sanitasi_layak", "🚿 Sanitasi Layak (%)",    0.0, 100.0,  70.0),
    ("persentase_akses_air_layak",      "💦 Akses Air Layak (%)",   0.0, 100.0,  80.0),
]

POLICY_MAP = {
    "persentase_akses_sanitasi_layak": (
        "Investasi pada infrastruktur sanitasi terbukti efektif menekan kasus DBD. "
        "Prioritaskan program sanitasi di daerah dengan akses sanitasi rendah."
    ),
    "persentase_akses_air_layak": (
        "Peningkatan akses air bersih mengurangi kebutuhan penampungan air terbuka "
        "yang menjadi tempat berkembang biak nyamuk."
    ),
    "persentase_mobilitas": (
        "Mobilitas penduduk berperan dalam penyebaran DBD antar wilayah. "
        "Pertimbangkan pembatasan mobilitas saat musim penularan tinggi."
    ),
    "curah_hujan": (
        "Curah hujan tinggi meningkatkan genangan air. "
        "Perkuat sistem drainase dan program fogging preventif saat musim hujan."
    ),
    "suhu": (
        "Perubahan suhu mempengaruhi siklus hidup nyamuk. "
        "Monitor kondisi iklim dan sesuaikan jadwal program fogging."
    ),
    "kelembaban": (
        "Kelembaban tinggi mempercepat perkembangbiakan nyamuk. "
        "Kurangi area lembab di sekitar pemukiman."
    ),
}


def show(df_merge):
    st.title("⚙️ Simulasi Variabel")
    st.caption("Ubah nilai faktor eksternal dan lihat dampaknya terhadap prediksi kasus DBD.")

    prov_opts    = get_provinsi_list(df_merge)
    fitur_cols   = list(get_bundle("fitur_cols", []))
    prov_to_kode = get_bundle("prov_to_kode", {})
    df_modeling  = get_bundle("df_modeling", pd.DataFrame())

    st.markdown("""
    <div class="section-header"><div class="icon-badge">📍</div> Pilih Provinsi</div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        prov_sim = st.selectbox("Provinsi", prov_opts)

    prov_sim_model = normalize_province_name(prov_sim)

    # Ambil nilai baseline
    X_base = None
    kode   = prov_to_kode.get(prov_sim_model)
    if kode is not None and not df_modeling.empty:
        df_p = df_modeling[df_modeling["provinsi_encoded"] == kode].sort_values("tahun")
        if len(df_p) > 0:
            X_base = df_p[fitur_cols].values[-1].astype(float)

    def get_default(key, fallback):
        if X_base is not None and key in fitur_cols:
            return float(X_base[fitur_cols.index(key)])
        return fallback

    # ── Sliders ───────────────────────────────────────────────────────────────
    st.markdown("#### ⚙️ Atur Nilai Variabel")
    col1, col2 = st.columns(2)
    sliders    = {}
    for i, (key, label, mn, mx, fb) in enumerate(SIM_VARS):
        container    = col1 if i % 2 == 0 else col2
        sliders[key] = container.slider(label, mn, mx, get_default(key, fb))

    if st.button(
        "🔬 Jalankan Simulasi",
        type="primary"
    ):

        result = simulasi_prediksi(
            prov_sim_model,
            **sliders
        )

        st.session_state["sim_result"] = result
        st.session_state["sim_prov"] = prov_sim
        st.session_state["sim_sliders"] = sliders

    if "sim_result" not in st.session_state:
        return

    result = st.session_state["sim_result"]
    prov_sim = st.session_state["sim_prov"]
    sliders = st.session_state["sim_sliders"]

    result = simulasi_prediksi(
        normalize_province_name(prov_sim),
        **sliders
    )

    st.session_state["sim_result"] = result
    st.session_state["sim_prov"] = prov_sim
    st.session_state["sim_sliders"] = sliders

    with st.expander("🔍 Debug Info"):
        st.write("Sliders yang dikirim:", sliders)
        st.write("Fitur cols:", fitur_cols)
        st.write("Log perubahan:", result.get("log", []))
        st.write("Baseline:", result.get("baseline"))
        st.write("Simulasi:", result.get("simulasi"))

    if "error" in result:
        st.error(result["error"])
        return

    s = result["selisih"]

    # ── Metric row ────────────────────────────────────────────────────────────
    st.divider()
    ca, cb, cc = st.columns(3)
    ca.metric("Prediksi Dasar", f"{result['baseline']:,} kasus")
    cb.metric("Prediksi Simulasi", f"{result['simulasi']:,} kasus",
              f"{result['persen']:+.1f}%")
    cc.metric("Model yang Digunakan", result["model"])

    st.divider()

    if s > 0:
        st.warning(f"⚠️ Kasus diprediksi **naik {s:,}** dengan variabel ini.")
    elif s < 0:
        st.success(f"✅ Kasus diprediksi **turun {abs(s):,}** dengan variabel ini.")
    else:
        st.info("Tidak ada perubahan prediksi.")

    st.divider()

    # ── Bar chart + Policy Impact tabel ───────────────────────────────────────
    col_chart, col_policy = st.columns(2)

    with col_chart:
        st.markdown("**📊 Prediksi Dasar vs Simulasi**")
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(
            ["Prediksi Dasar", "Simulasi"],
            [result["baseline"], result["simulasi"]],
            color=[ACCENT, "#ff6b6b" if s > 0 else "#00cc88"],
        )
        style_ax(ax, fig, f"Prediksi Dasar vs Simulasi — {prov_sim}")
        ax.set_ylabel("Jumlah Kasus")
        for xi, v in enumerate([result["baseline"], result["simulasi"]]):
            ax.text(xi, v + v * 0.01, f"{v:,}", ha="center",
                    color=TEXT_COL, fontsize=10)
        st.pyplot(fig)
        plt.close()

    with col_policy:
        st.markdown("**📋 Analysis Dampak Kebijakan**")
        policy_rows = []
        for key, label, mn, mx, fb in SIM_VARS:
            if key not in fitur_cols:
                continue
            idx       = fitur_cols.index(key)
            val_base  = float(X_base[idx]) if X_base is not None else fb
            val_sim   = sliders[key]
            delta     = val_sim - val_base
            delta_pct = (delta / val_base * 100) if val_base != 0 else 0
            if abs(delta) > 0.01:
                policy_rows.append({
                    "Variabel" : label,
                    "Baseline" : round(val_base, 1),
                    "Simulasi" : round(val_sim, 1),
                    "Perubahan": f"{delta:+.1f}",
                    "Delta (%)" : f"{delta_pct:+.1f}%",
                })
        if policy_rows:
            st.dataframe(pd.DataFrame(policy_rows), use_container_width=True,
                         hide_index=True)
        else:
            st.info("Belum ada variabel yang diubah dari Prediksi Dasar.")

    st.divider()

# ── Policy Impact Narrative ───────────────────────────────────────────────
    st.subheader("📝 Analysis Dampak Kebijakan")

    perubahan_signifikan = []
    for key, label, mn, mx, fb in SIM_VARS:
        if key not in fitur_cols:
            continue
        idx       = fitur_cols.index(key)
        val_base  = float(X_base[idx]) if X_base is not None else fb
        val_sim   = sliders[key]
        delta     = val_sim - val_base
        delta_pct = (delta / val_base * 100) if val_base != 0 else 0
        if abs(delta_pct) >= 5:
            perubahan_signifikan.append((label, delta_pct, key))

    perubahan_signifikan.sort(key=lambda x: abs(x[1]), reverse=True)

    if not perubahan_signifikan:
        st.info("Ubah nilai variabel minimal 5% dari Prediksi Dasar"
                "untuk melihat Analysis Dampak Kebijakan.")
    elif s == 0:
        st.info("Tidak ada perubahan signifikan pada prediksi. "
                "Coba ubah nilai variabel lebih jauh dari Prediksi Dasar.")
    else:
        # Siapkan data untuk AI
        perubahan_str = ", ".join(
            [f"{v} ({d:+.1f}%)" for v, d, _ in perubahan_signifikan]
        )
        arah_kasus = "naik" if s > 0 else "turun"

        # Baca API key
        from dotenv import load_dotenv
        import os
        load_dotenv()
        gemini_api_key = (
            os.getenv("GEMINI_API_KEY") or
            st.secrets.get("GEMINI_API_KEY", None)
        )

        @st.cache_data(ttl=1800, show_spinner=False)
        def generate_policy_impact(prov_sim, perubahan_str, arah_kasus,
                                   baseline, simulasi, persen, selisih,
                                   api_key):
            try:
                import google.generativeai as genai

                if not api_key:
                    return None, "GEMINI_API_KEY tidak ditemukan"

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                prompt = f"""Kamu adalah analis kebijakan kesehatan masyarakat Indonesia
yang fokus pada pengendalian DBD (Demam Berdarah Dengue).

Berikan analisis dampak kebijakan dalam Bahasa Indonesia yang singkat,
jelas, dan actionable (4-5 kalimat). Langsung ke isi tanpa pembuka.

DATA SIMULASI — {prov_sim}:
- Prediksi baseline: {baseline:,} kasus
- Prediksi setelah perubahan: {simulasi:,} kasus
- Perubahan: {arah_kasus} {abs(persen):.1f}% ({abs(selisih):,} kasus)
- Variabel yang diubah: {perubahan_str}

FORMAT OUTPUT:
- Kalimat 1: ringkasan dampak keseluruhan perubahan variabel
- Kalimat 2: analisis variabel yang paling berkontribusi
- Kalimat 3: hubungan antar variabel yang diubah (jika ada)
- Kalimat 4: rekomendasi kebijakan spesifik berdasarkan simulasi ini
- Kalimat 5: langkah prioritas yang harus dilakukan pertama

PENTING: jangan gunakan markdown seperti ** atau ##, tulis teks biasa saja."""

                response = model.generate_content(prompt)
                return response.text, None

            except Exception as e:
                return None, str(e)

        # Panggil AI
        with st.spinner("🤖 AI sedang menganalisis dampak kebijakan..."):
            ai_policy, ai_error = generate_policy_impact(
                prov_sim, perubahan_str, arah_kasus,
                result["baseline"], result["simulasi"],
                result["persen"], result["selisih"],
                gemini_api_key
            )

        warna = "#c8502a" if s > 0 else "#2a8c5a"

        if ai_error:
            # Fallback ke if-else
            var_utama, delta_utama, key_utama = perubahan_signifikan[0]
            narasi = (
                f"Berdasarkan simulasi, perubahan {var_utama} sebesar "
                f"{delta_utama:+.1f}% berkontribusi pada prediksi kasus yang "
                f"{arah_kasus} {abs(result['persen']):.1f}% "
                f"({abs(s):,} kasus) dari baseline."
            )
            if len(perubahan_signifikan) > 1:
                var_lain = ", ".join(
                    [f"{v} ({d:+.1f}%)" for v, d, _ in perubahan_signifikan[1:3]]
                )
                narasi += f" Faktor pendukung: {var_lain}."

            rekomendasi = POLICY_MAP.get(
                key_utama,
                "Pertahankan dan tingkatkan program pencegahan DBD."
            )
            ai_policy = f"{narasi} {rekomendasi}"
            st.caption(f"⚠️ AI tidak tersedia: {ai_error}")

        st.markdown(
            f"""<div class="insight-box" style="border-left-color:{warna}">
            <strong>📊 Dampak Perubahan Variabel — {prov_sim}</strong><br><br>
            {ai_policy}
            </div>""",
            unsafe_allow_html=True,
        )

        # =====================================================
        # EXPORT LAPORAN SIMULASI
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
        📥 Unduh Laporan Simulasi
        </h2>

        <p style="color:#e2e8f0;">
        Unduh hasil simulasi variabel dalam format CSV, Excel, dan PDF.
        </p>

        </div>
        """, unsafe_allow_html=True)

        col_csv, col_excel, col_pdf = st.columns(3)

        export_df = pd.DataFrame([
            {
                "Provinsi": prov_sim,
                "Model": result["model"],
                "Baseline": result["baseline"],
                "Simulasi": result["simulasi"],
                "Selisih": result["selisih"],
                "Persentase": result["persen"]
            }
        ])

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
                "simulasi_dbd.csv",
                "text/csv",
                use_container_width=True
            )

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
                "simulasi_dbd.xlsx",
                use_container_width=True
            )

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
                "📄 Generate PDF Simulasi",
                use_container_width=True
            ):

                try:

                    slider_html = ""

                    for k, v in sliders.items():

                        slider_html += f"""
                        <tr>
                            <td>{k}</td>
                            <td>{v}</td>
                        </tr>
                        """

                    policy_html = ""

                    if policy_rows:

                        for row in policy_rows:

                            policy_html += f"""
                            <tr>
                                <td>{row['Variabel']}</td>
                                <td>{row['Baseline']}</td>
                                <td>{row['Simulasi']}</td>
                                <td>{row['Perubahan']}</td>
                                <td>{row['Delta (%)']}</td>
                            </tr>
                            """

                    html = f"""

                    <div class="section">
                    <h3>⚙️ Ringkasan Simulasi</h3>

                    <div class="card">

                    <p><b>Provinsi:</b> {prov_sim}</p>
                    <p><b>Model:</b> {result['model']}</p>
                    <p><b>Baseline:</b> {result['baseline']:,}</p>
                    <p><b>Simulasi:</b> {result['simulasi']:,}</p>
                    <p><b>Selisih:</b> {result['selisih']:,}</p>
                    <p><b>Perubahan:</b> {result['persen']:+.1f}%</p>

                    </div>
                    </div>

                    <div class="section">
                    <h3>🎛️ Parameter Simulasi</h3>

                    <table>
                    <tr>
                        <th>Variabel</th>
                        <th>Nilai Simulasi</th>
                    </tr>

                    {slider_html}

                    </table>
                    </div>

                    <div class="section">
                    <h3>📋 Policy Impact Analysis</h3>

                    <table>

                    <tr>
                        <th>Variabel</th>
                        <th>Baseline</th>
                        <th>Simulasi</th>
                        <th>Perubahan</th>
                        <th>Delta (%)</th>
                    </tr>

                    {policy_html}

                    </table>

                    </div>

                    <div class="section">
                    <h3>📝 Dampak Perubahan Variabel</h3>

                    <div class="card">

                    {ai_policy}

                    </div>

                    </div>

                    """

                    pdf_bytes = generate_pdf_via_api(
                        title="Laporan Simulasi Variabel",
                        html_content=html,
                        footer_text=f"Sistem Prediksi Kasus DBD Indonesia - Simulasi Variabel - {prov_sim}"
                    )

                    st.download_button(
                        "⬇ Download PDF Simulasi",
                        pdf_bytes,
                        f"simulasi_{prov_sim}.pdf",
                        "application/pdf",
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"Gagal membuat PDF: {e}"
                    )


