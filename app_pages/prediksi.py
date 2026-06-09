"""
pages/prediksi.py — Prediksi kasus DBD per provinsi
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, DARK_BG, TEXT_COL
from utils.db import get_provinsi_list, get_tahun_list
from utils.model import generate_insight, get_province_series
from utils.export_utils import (
    dataframe_to_csv,
    dataframe_to_excel,
    generate_pdf_via_api
)

def show(df_merge):
    st.title("🔮 Prediksi Kasus DBD")

    prov_opts = get_provinsi_list(df_merge)
    thn_opts  = get_tahun_list(df_merge)
    max_thn   = int(max(thn_opts))

    col1, col2 = st.columns(2)
    with col1:
        prov_pred = st.selectbox("Provinsi", prov_opts)
    with col2:
        thn_pred = st.selectbox("Tahun Prediksi",
                                list(range(max_thn + 1, max_thn + 6)))


    if st.button("🔮 Jalankan Prediksi", type="primary"):

        with st.spinner("Menghitung..."):

            ins = generate_insight(
                df_merge,
                prov_pred,
                thn_pred
            )

            st.session_state["pred_result"] = ins
            st.session_state["pred_prov"] = prov_pred
            st.session_state["pred_year"] = thn_pred


    if "pred_result" not in st.session_state:
        return


    ins = st.session_state["pred_result"]
    prov_pred = st.session_state["pred_prov"]
    thn_pred = st.session_state["pred_year"]


    if "error" in ins:
        st.error(ins["error"])
        return

    # ── 1. Metric row ─────────────────────────────────────────────────────────
    ca, cb, cc = st.columns(3)
    ca.metric("Kasus Aktual Terakhir", f"{ins['aktual']:,}",
              f"Tahun {ins['tahun_acuan']}")
    cb.metric("Prediksi Kasus", f"{ins['prediksi']:,}",
              f"{ins['persen']:+.1f}%")
    cc.metric("Model yang Digunakan", ins["model"])

    st.divider()

    # ── 2. Risk Indicator ─────────────────────────────────────────────────────
    persen = ins["persen"]
    if persen > 20:
        risk_level, risk_color = "HIGH",   "#ff4444"
        risk_emoji, risk_desc  = "🔴", "Risiko tinggi — potensi outbreak signifikan"
    elif persen > 5:
        risk_level, risk_color = "MEDIUM", "#ffaa00"
        risk_emoji, risk_desc  = "🟡", "Risiko sedang — perlu pemantauan ketat"
    else:
        risk_level, risk_color = "LOW",    "#00cc88"
        risk_emoji, risk_desc  = "🟢", "Risiko rendah — kondisi relatif terkendali"

    outbreak_prob = min(99, max(1, int(50 + persen * 1.5)))

    col_risk, col_outbreak = st.columns(2)
    with col_risk:
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">Indikator Risiko</div>
                <div class="value" style="color:{risk_color}">{risk_emoji} {risk_level}</div>
                <div class="sub">{risk_desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_outbreak:
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">Probabilitas Outbreak</div>
                <div class="value" style="color:{risk_color}">{outbreak_prob}%</div>
                <div class="sub">estimasi probabilitas peningkatan kasus</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── 3. Alert ──────────────────────────────────────────────────────────────
    if risk_level == "HIGH":
        st.error(
            f"⚠️ **ALERT — Potensi Outbreak Terdeteksi!**\n\n"
            f"Provinsi **{prov_pred}** diprediksi mengalami peningkatan kasus "
            f"sebesar **{persen:+.1f}%** pada tahun {thn_pred}. "
            f"Segera lakukan tindakan pencegahan."
        )
    elif risk_level == "MEDIUM":
        st.warning(
            f"⚠️ **Perhatian — Peningkatan Kasus Terdeteksi**\n\n"
            f"Provinsi **{prov_pred}** menunjukkan tren peningkatan "
            f"**{persen:+.1f}%**. Monitor situasi secara berkala."
        )
    else:
        st.success(
            f"✅ **Kondisi Terkendali**\n\n"
            f"Provinsi **{prov_pred}** diprediksi stabil "
            f"({persen:+.1f}%) pada tahun {thn_pred}."
        )

    st.divider()

    # ── 4. Insight box ────────────────────────────────────────────────────────
    st.markdown(
        f"""<div class="insight-box">
        <strong>{ins['status']}</strong><br><br>{ins['saran']}
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

# ── 5. Recommended Actions ────────────────────────────────────────────────
    st.subheader("📋 Tindakan yang Direkomendasikan")

    # Ambil data konteks provinsi
    df_prov     = df_merge[df_merge["provinsi"] == prov_pred].sort_values("tahun")
    tahun_max_p = int(df_prov["tahun"].max())
    df_last     = df_prov[df_prov["tahun"] == tahun_max_p]

    # Ambil nilai faktor eksternal terakhir
    faktor_konteks = {}
    for col, label in [
        ("curah_hujan",                     "curah hujan"),
        ("suhu",                            "suhu"),
        ("kelembaban",                      "kelembaban"),
        ("persentase_mobilitas",            "mobilitas"),
        ("persentase_akses_sanitasi_layak", "sanitasi layak"),
        ("persentase_akses_air_layak",      "akses air"),
    ]:
        if col in df_last.columns:
            faktor_konteks[label] = round(float(df_last[col].mean()), 1)

    faktor_str = ", ".join([f"{k}: {v}" for k, v in faktor_konteks.items()])

    # Baca API key
    from dotenv import load_dotenv
    import os
    load_dotenv()
    gemini_api_key = (
        os.getenv("GEMINI_API_KEY") or
        st.secrets.get("GEMINI_API_KEY", None)
    )

    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_recommendations(prov_pred, thn_pred, risk_level,
                                 persen, prediksi, faktor_str, api_key):
        try:
            import google.generativeai as genai

            if not api_key:
                return None, "GEMINI_API_KEY tidak ditemukan"

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""Kamu adalah sistem rekomendasi kebijakan kesehatan masyarakat
Indonesia yang fokus pada pengendalian DBD.

Berikan 4-5 rekomendasi tindakan yang spesifik, actionable, dan diprioritaskan
berdasarkan kondisi provinsi ini. Setiap rekomendasi 1-2 kalimat.

DATA PROVINSI {prov_pred}:
- Tahun prediksi: {thn_pred}
- Prediksi kasus: {prediksi:,} kasus
- Perubahan: {persen:+.1f}%
- Risk level: {risk_level}
- Kondisi faktor eksternal terkini: {faktor_str}

FORMAT OUTPUT (ikuti persis, tanpa markdown):
1. [Nama Tindakan]: [Deskripsi spesifik 1-2 kalimat]
2. [Nama Tindakan]: [Deskripsi spesifik 1-2 kalimat]
3. [Nama Tindakan]: [Deskripsi spesifik 1-2 kalimat]
4. [Nama Tindakan]: [Deskripsi spesifik 1-2 kalimat]
5. [Nama Tindakan]: [Deskripsi spesifik 1-2 kalimat]

PENTING:
- Sesuaikan rekomendasi dengan kondisi faktor eksternal provinsi ini
- Prioritaskan berdasarkan faktor yang paling kritis
- Gunakan Bahasa Indonesia yang jelas dan mudah dipahami
- Jangan gunakan markdown seperti ** atau ##"""

            response = model.generate_content(prompt)
            return response.text, None

        except Exception as e:
            return None, str(e)

    # Panggil AI
    with st.spinner("🤖 AI sedang menyusun rekomendasi..."):
        ai_actions, ai_error = generate_recommendations(
            prov_pred, thn_pred, risk_level,
            persen, ins["prediksi"], faktor_str,
            gemini_api_key
        )

    if ai_error:
        # Fallback ke if-else
        if risk_level == "HIGH":
            actions = [
                ("🚁", "Fogging massal",              "Lakukan fogging di seluruh wilayah berisiko tinggi segera."),
                ("🏥", "Siapkan fasilitas kesehatan", "Tingkatkan kapasitas rumah sakit dan puskesmas untuk antisipasi lonjakan."),
                ("🧹", "Perbaikan sanitasi darurat",  "Bersihkan genangan air dan tempat perindukan nyamuk."),
                ("📢", "Kampanye masyarakat",          "Sosialisasi 3M Plus secara masif di seluruh kecamatan."),
                ("📊", "Aktivasi posko DBD",           "Bentuk posko pemantauan dan pelaporan kasus harian."),
            ]
        elif risk_level == "MEDIUM":
            actions = [
                ("🚁", "Fogging preventif",   "Lakukan fogging di titik-titik berisiko sedang."),
                ("🧹", "Perbaikan sanitasi",  "Tingkatkan program kebersihan lingkungan secara berkala."),
                ("📢", "Kampanye masyarakat", "Sosialisasi 3M Plus di tingkat kelurahan."),
                ("📊", "Pemantauan rutin",    "Monitor perkembangan kasus mingguan."),
            ]
        else:
            actions = [
                ("✅", "Pertahankan program", "Lanjutkan program pencegahan DBD yang sudah berjalan."),
                ("📊", "Pemantauan berkala",  "Pantau data kasus secara bulanan."),
                ("📢", "Edukasi masyarakat",  "Pertahankan kesadaran masyarakat tentang pencegahan DBD."),
            ]

        for emoji, title, desc in actions:
            st.markdown(
                f"""<div class="insight-box">
                <strong>{emoji} {title}</strong><br>
                <span style="color:#8892b0">{desc}</span>
                </div>""",
                unsafe_allow_html=True,
            )
        st.caption(f"⚠️ AI tidak tersedia: {ai_error}")

    else:
        # Tampilkan rekomendasi dari Gemini
        # Parse output Gemini yang format "1. Judul: Deskripsi"
        lines = [l.strip() for l in ai_actions.strip().split("\n") if l.strip()]
        emojis = ["🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢",
                  "🚁", "🧹", "📢", "📊", "🏥"]

        for i, line in enumerate(lines):
            if not line:
                continue
            # Pisahkan nomor dari konten
            if ". " in line:
                _, content = line.split(". ", 1)
            else:
                content = line

            # Pisahkan judul dari deskripsi
            if ": " in content:
                title, desc = content.split(": ", 1)
            else:
                title, desc = content, ""

            emoji = emojis[i % len(emojis)]
            st.markdown(
                f"""<div class="insight-box">
                <strong>{emoji} {title}</strong><br>
                <span style="color:#8892b0">{desc}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── 6. Grafik historis + prediksi ─────────────────────────────────────────
    st.subheader("📊 Grafik Historis & Prediksi")
    series = get_province_series(df_merge, prov_pred)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(series.index, series.values, alpha=0.1, color=ACCENT)
    ax.plot(series.index, series.values, marker="o", color=ACCENT,
            linewidth=2, label="Data historis")
    ax.scatter([thn_pred], [ins["prediksi"]], color="#ff6b6b",
               s=150, zorder=5, label=f"Prediksi {thn_pred}")
    ax.annotate(f"  {ins['prediksi']:,}", (thn_pred, ins["prediksi"]),
                color="#ff6b6b", fontsize=10)
    style_ax(ax, fig, f"Historis + Prediksi — {prov_pred}")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Jumlah Kasus")
    ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COL)
    st.pyplot(fig)
    plt.close()

    st.session_state["last_pred"] = ins

    st.divider()

    st.markdown("""
        <div style="
        padding:25px;
        border-radius:20px;
        background:linear-gradient(
        135deg,
        rgba(15,23,42,0.98),
        rgba(30,41,59,0.98)
        );
        border:1px solid rgba(34,211,238,0.4);
        box-shadow:0 0 25px rgba(34,211,238,0.15);
        margin-bottom:25px;
        ">

        <h2 style="
        margin-bottom:10px;
        color:white;
        ">
        📥 Unduh Laporan Prediksi
        </h2>

        <p style="
        color:#cbd5e1;
        font-size:15px;
        margin-bottom:0px;
        ">
        Unduh hasil prediksi DBD dalam format CSV, Excel, dan PDF.
        </p>

        </div>
        """, unsafe_allow_html=True)
    # ==================================
    # DATA EXPORT
    # ==================================

    export_df = pd.DataFrame({
        "Provinsi": [prov_pred],
        "Tahun Prediksi": [thn_pred],
        "Kasus Aktual": [ins["aktual"]],
        "Prediksi Kasus": [ins["prediksi"]],
        "Perubahan (%)": [round(ins["persen"], 2)],
        "Risk Level": [risk_level],
        "Outbreak Probability": [outbreak_prob]
    })

    col1, col2, col3 = st.columns(3)

    # =========================
    # CSV
    # =========================

    with col1:

        st.success("📋 CSV")

        st.download_button(
            "⬇ Download CSV",
            dataframe_to_csv(export_df),
            file_name=f"prediksi_{prov_pred}_{thn_pred}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # =========================
    # EXCEL
    # =========================

    with col2:

        st.info("📊 Excel")

        st.download_button(
            "⬇ Download Excel",
            dataframe_to_excel(export_df),
            file_name=f"prediksi_{prov_pred}_{thn_pred}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # =========================
    # PDF
    # =========================

    with col3:

        st.warning("📄 PDF")

        if st.button(
            "📄 Generate PDF Prediksi",
            use_container_width=True
        ):

            try:

                history_table = ""

                for year, value in series.items():

                    history_table += f"""
                    <tr>
                        <td>{year}</td>
                        <td>{int(value):,}</td>
                    </tr>
                    """

                history_table += f"""
                <tr>
                    <td><b>{thn_pred}</b></td>
                    <td><b>{ins['prediksi']:,}</b></td>
                </tr>
                """

                recommendations_html = ""

                try:

                    if ai_error:

                        for emoji, title, desc in actions:

                            recommendations_html += f"""
                            <li>
                            <b>{emoji} {title}</b><br>
                            {desc}
                            </li>
                            """

                    else:

                        for item in ai_actions:

                            recommendations_html += f"""
                            <li>{item}</li>
                            """

                except:

                    recommendations_html = """
                    <li>Fogging massal</li>
                    <li>Siapkan fasilitas kesehatan</li>
                    <li>Perbaikan sanitasi darurat</li>
                    <li>Kampanye masyarakat</li>
                    <li>Aktivasi posko DBD</li>
                    """

                html_content = f"""

                <div class="section">

                    <h3>📊 Ringkasan Prediksi</h3>

                    <div class="card">

                        <p><b>Provinsi:</b> {prov_pred}</p>

                        <p><b>Tahun Prediksi:</b> {thn_pred}</p>

                        <p><b>Kasus Aktual:</b> {ins['aktual']:,}</p>

                        <p><b>Prediksi Kasus:</b> {ins['prediksi']:,}</p>

                        <p><b>Perubahan:</b> {ins['persen']:+.1f}%</p>

                        <p><b>Model:</b> {ins['model']}</p>

                    </div>

                </div>

                <div class="section">

                    <h3>⚠ Risk Assessment</h3>

                    <div class="card">

                        <p><b>Risk Level:</b> {risk_level}</p>

                        <p><b>Deskripsi:</b> {risk_desc}</p>

                        <p><b>Outbreak Probability:</b> {outbreak_prob}%</p>

                    </div>

                </div>

                <div class="section">

                    <h3>🤖 Insight Sistem</h3>

                    <div class="card">

                        <p><b>{ins['status']}</b></p>

                        <p>{ins['saran']}</p>

                    </div>

                </div>

                <div class="section">

                <h3>📋 Recommended Actions</h3>

                <div class="card">

                <ul>

                {recommendations_html}

                </ul>

                </div>

                </div>

                <div class="section">

                    <h3>📈 Data Historis & Prediksi</h3>

                    <table>

                        <tr>
                            <th>Tahun</th>
                            <th>Jumlah Kasus</th>
                        </tr>

                        {history_table}

                    </table>

                </div>

                """

                pdf_bytes = generate_pdf_via_api(
                    f"Laporan Prediksi DBD - {prov_pred}",
                    html_content,
                    footer_text=(
                        f"Sistem Prediksi Kasus DBD Indonesia - "
                        f"Prediksi - "
                        f"{prov_pred} - "
                        f"{thn_pred}"
                    )
                )

                st.download_button(
                    "⬇ Download PDF",
                    pdf_bytes,
                    file_name=f"prediksi_{prov_pred}_{thn_pred}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:

                st.error(f"Gagal membuat PDF: {e}")