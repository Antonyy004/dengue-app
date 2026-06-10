import streamlit as st
import pandas as pd
import plotly.express as px

from utils.capital_map import CAPITAL_MAP

from utils.export_utils import (
    dataframe_to_csv,
    dataframe_to_excel,
    generate_pdf_via_api
)

def show(df_merge):

    province_mapping = {
        "Dki Jakarta": "DKI Jakarta",

        "Di Yogyakarta": "Daerah Istimewa Yogyakarta",
        "DI Yogyakarta": "Daerah Istimewa Yogyakarta",

        "Daerah Istimewa Yogyakarta": "Daerah Istimewa Yogyakarta"
    }

    df_merge = df_merge.copy()

    df_merge["provinsi"] = (
        df_merge["provinsi"]
        .astype(str)
        .str.strip()
        .replace(province_mapping)
    )

    st.title("📍 Analisis Provinsi")

    selected_province = st.session_state.get(
        "selected_province",
        None
    )

    if selected_province is None:

        st.info(
            "Silakan pilih provinsi terlebih dahulu melalui Peta Risiko Indonesia pada halaman Beranda."
        )

        return

    province_df = df_merge[
        df_merge["provinsi"]
        .astype(str)
        .str.strip()
        .str.lower()
        ==
        str(selected_province)
        .strip()
        .lower()
    ].copy()

    if province_df.empty:

        st.warning(
            "Data provinsi tidak ditemukan."
        )

        return

    capital = CAPITAL_MAP.get(
        selected_province,
        "-"
    )

    st.markdown(
        f"""
### 🏙️ {selected_province}

**Ibu Kota:** {capital}
"""
    )

    latest_year = province_df["tahun"].max()

    latest_row = province_df[
        province_df["tahun"] == latest_year
    ].iloc[0]

    latest_cases = int(
        latest_row["jumlah_kasus_bulat"]
    )

    # =====================
    # Tingkat Risiko
    # =====================

    if latest_cases < 1000:
        risk = "🟢 Aman"

    elif latest_cases < 3000:
        risk = "🟡 Waspada"

    elif latest_cases < 6000:
        risk = "🟠 Tinggi"

    else:
        risk = "🔴 Bahaya"

    st.metric(
        "Tingkat Prediksi Risiko DBD Tahun 2026",
        risk
    )

    st.divider()

    # =====================
    # Tren Historis
    # =====================

    st.subheader("📈 Tren Historis Kasus DBD")

    trend_df = (
        province_df
        .groupby("tahun")["jumlah_kasus_bulat"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x="tahun",
        y="jumlah_kasus_bulat",
        markers=True,
        title=f"Perkembangan Kasus DBD - {selected_province}"
    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # =====================
    # Deteksi Lonjakan
    # =====================

    st.subheader("⚠️ Deteksi Lonjakan Kasus")

    outbreak_years = []

    trend_df = trend_df.sort_values(
        "tahun"
    )

    for i in range(1, len(trend_df)):

        prev_cases = trend_df.iloc[i - 1][
            "jumlah_kasus_bulat"
        ]

        curr_cases = trend_df.iloc[i][
            "jumlah_kasus_bulat"
        ]

        if prev_cases > 0:

            growth = (
                (curr_cases - prev_cases)
                / prev_cases
            ) * 100

            if growth > 30:

                outbreak_years.append(
                    (
                        int(trend_df.iloc[i]["tahun"]),
                        round(growth, 1)
                    )
                )

    if outbreak_years:

        for year, growth in outbreak_years:

            st.warning(
                f"Terdeteksi lonjakan kasus pada tahun {year} (+{growth}%)."
            )

    else:

        st.success(
            "Tidak ditemukan lonjakan kasus yang signifikan."
        )

    st.divider()

    # =====================
    # Profil Provinsi
    # =====================

    st.subheader("📊 Profil Provinsi")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "🌧️ Curah Hujan",
            round(
                latest_row["curah_hujan"],
                2
            )
        )

        st.metric(
            "🌡️ Suhu",
            round(
                latest_row["suhu"],
                2
            )
        )

        st.metric(
            "💧 Kelembaban",
            round(
                latest_row["kelembaban"],
                2
            )
        )

    with c2:

        st.metric(
            "🚗 Mobilitas",
            round(
                latest_row["persentase_mobilitas"],
                2
            )
        )

        st.metric(
            "🚿 Sanitasi Layak",
            round(
                latest_row[
                    "persentase_akses_sanitasi_layak"
                ],
                2
            )
        )

        st.metric(
            "👥 Kepadatan Penduduk",
            round(
                latest_row[
                    "kepadatan_penduduk_per_km2"
                ],
                2
            )
        )

    st.divider()

    # =====================
    # Analisis AI
    # =====================

    st.subheader("🤖 Analisis AI")

    if latest_cases > 6000:

        st.error(
            "Provinsi ini memiliki tingkat risiko tinggi dan memerlukan perhatian khusus dalam pengendalian DBD."
        )

    elif latest_cases > 3000:

        st.warning(
            "Provinsi ini menunjukkan risiko sedang hingga tinggi dan perlu pemantauan berkala."
        )

    else:

        st.success(
            "Risiko DBD relatif terkendali, namun upaya pencegahan tetap perlu dilakukan."
        )

    st.divider()

    # =====================
    # Export Data
    # =====================

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
    📥 Unduh Laporan Analisis Provinsi
    </h2>

    <p style="
    color:#cbd5e1;
    font-size:15px;
    margin-bottom:0px;
    ">
    Unduh hasil analisis provinsi dalam format CSV, Excel, dan PDF.
    </p>

    </div>
    """, unsafe_allow_html=True)

    export_df = province_df.copy()

    col1, col2, col3 = st.columns(3)

    # =====================
    # CSV
    # =====================

    with col1:

        st.success("📋 CSV")

        csv_data = dataframe_to_csv(
            export_df
        )

        st.download_button(
            label="⬇ Download CSV",
            data=csv_data,
            file_name=f"{selected_province}_dbd.csv",
            mime="text/csv",
            use_container_width=True
        )

    # =====================
    # EXCEL
    # =====================

    with col2:

        st.info("📊 Excel")

        excel_data = dataframe_to_excel(
            export_df
        )

        st.download_button(
            label="⬇ Download Excel",
            data=excel_data,
            file_name=f"{selected_province}_dbd.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # =====================
    # PDF
    # =====================

    with col3:

        st.warning("📄 PDF")

        if st.button(
            "📄 Generate PDF",
            use_container_width=True
        ):

            try:

                trend_table = ""

                for _, row in trend_df.iterrows():

                    trend_table += f"""
                    <tr>
                        <td>{int(row['tahun'])}</td>
                        <td>{int(row['jumlah_kasus_bulat'])}</td>
                    </tr>
                    """

                outbreak_html = ""

                if outbreak_years:

                    for year, growth in outbreak_years:

                        outbreak_html += f"""
                        <li>
                        ⚠ Tahun {year}
                        (+{growth}%)
                        </li>
                        """

                else:

                    outbreak_html = """
                    <li>
                    ✅ Tidak ditemukan lonjakan signifikan
                    </li>
                    """

                if latest_cases > 6000:

                    ai_text = """
                    Provinsi ini memiliki tingkat risiko tinggi dan memerlukan perhatian khusus dalam pengendalian DBD.
                    """

                elif latest_cases > 3000:

                    ai_text = """
                    Provinsi ini menunjukkan risiko sedang hingga tinggi dan perlu pemantauan berkala.
                    """

                else:

                    ai_text = """
                    Risiko DBD relatif terkendali, namun upaya pencegahan tetap perlu dilakukan.
                    """

                html_content = f"""

                <div class="section">

                    <h3>📍 Informasi Provinsi</h3>

                    <div class="card">

                        <p><b>Provinsi:</b> {selected_province}</p>

                        <p><b>Ibu Kota:</b> {capital}</p>

                        <p><b>Tingkat Risiko:</b> {risk}</p>

                        <p><b>Jumlah Kasus Terakhir:</b> {latest_cases:,}</p>

                    </div>

                </div>

                <div class="section">

                    <h3>📈 Tren Historis Kasus DBD</h3>

                    <table>

                        <tr>
                            <th>Tahun</th>
                            <th>Jumlah Kasus</th>
                        </tr>

                        {trend_table}

                    </table>

                </div>

                <div class="section">

                    <h3>⚠️ Deteksi Lonjakan Kasus</h3>

                    <div class="card">

                        <ul>

                            {outbreak_html}

                        </ul>

                    </div>

                </div>

                <div class="section">

                    <h3>📊 Profil Wilayah</h3>

                    <div class="card">

                        <ul>

                            <li>🌧 Curah Hujan : {round(latest_row['curah_hujan'],2)}</li>
                            <li>🌡 Suhu : {round(latest_row['suhu'],2)}</li>
                            <li>💧 Kelembaban : {round(latest_row['kelembaban'],2)}</li>
                            <li>🚗 Mobilitas : {round(latest_row['persentase_mobilitas'],2)}</li>
                            <li>🚿 Sanitasi Layak : {round(latest_row['persentase_akses_sanitasi_layak'],2)}</li>
                            <li>👥 Kepadatan Penduduk : {round(latest_row['kepadatan_penduduk_per_km2'],2)}</li>

                        </ul>

                    </div>

                </div>

                <div class="section">

                    <h3>🤖 Analisis Sistem</h3>

                    <div class="card">

                        <p>{ai_text}</p>

                    </div>

                </div>

                """

                pdf_bytes = generate_pdf_via_api(
                    f"Laporan Analisis Provinsi - {selected_province}",
                    html_content,
                    footer_text=(
                        f"Sistem Prediksi Kasus DBD Indonesia - "
                        f"Analisis Provinsi - "
                        f"{selected_province}"
                    )
                )

                st.download_button(
                    label="⬇ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{selected_province}_laporan.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"Gagal membuat PDF: {e}"
                )

    st.divider()

    if st.button("⬅️ Kembali ke Beranda"):

        st.session_state.page = "Beranda"

        st.rerun()