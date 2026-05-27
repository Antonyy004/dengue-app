"""
pages/prediksi.py — Prediksi kasus DBD per provinsi
"""

import streamlit as st
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, DARK_BG, TEXT_COL
from utils.db import get_provinsi_list, get_tahun_list
from utils.model import generate_insight, get_province_series


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

    if not st.button("🔮 Jalankan Prediksi", type="primary"):
        return

    with st.spinner("Menghitung..."):
        ins = generate_insight(df_merge, prov_pred, thn_pred)

    if "error" in ins:
        st.error(ins["error"])
        return

    # ── 1. Metric row ─────────────────────────────────────────────────────────
    ca, cb, cc = st.columns(3)
    ca.metric("Kasus Aktual Terakhir", f"{ins['aktual']:,}",
              f"Tahun {ins['tahun_acuan']}")
    cb.metric("Prediksi Kasus", f"{ins['prediksi']:,}",
              f"{ins['persen']:+.1f}%")
    cc.metric("Model", ins["model"])

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
                <div class="label">Risk Indicator</div>
                <div class="value" style="color:{risk_color}">{risk_emoji} {risk_level}</div>
                <div class="sub">{risk_desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_outbreak:
        st.markdown(
            f"""<div class="metric-card">
                <div class="label">Outbreak Probability</div>
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
    st.subheader("📋 Recommended Actions")

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
