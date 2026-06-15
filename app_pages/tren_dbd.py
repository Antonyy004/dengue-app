"""
pages/tren_dbd.py — Visualisasi tren DBD & Province Profile
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, GRID_COL, TEXT_COL, DARK_BG, PALETTE
from utils.db import get_provinsi_list, get_tahun_list
from utils.export_utils import (
    dataframe_to_csv,
    dataframe_to_excel,
    generate_pdf_via_api
)

def show(df_merge):
    st.title("Visualisasi Tren DBD")
    st.caption("Eksplorasi tren kasus DBD dari waktu ke waktu, secara nasional maupun per provinsi.")

    prov_opts = get_provinsi_list(df_merge)
    thn_opts  = get_tahun_list(df_merge)

    st.markdown("""
    <div class="section-header"><div class="icon-badge">🔧</div> Filter & Pengaturan</div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            sel_prov = st.multiselect(
                "Pilih Provinsi (kosongkan = nasional)", options=prov_opts, default=[]
            )
        with col2:
            thn_range = st.slider(
                "Rentang Tahun",
                min_value=int(min(thn_opts)), max_value=int(max(thn_opts)),
                value=(int(min(thn_opts)), int(max(thn_opts))),
            )

        chart_type = st.radio("Tipe Grafik", ["Grafik Garis", "Grafik Batang"], horizontal=True)

    df_f = df_merge[
        (df_merge["tahun"] >= thn_range[0]) &
        (df_merge["tahun"] <= thn_range[1])
    ]
    if sel_prov:
        df_f = df_f[df_f["provinsi"].isin(sel_prov)]

# ── Main chart ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header"><div class="icon-badge">📈</div> Grafik Tren Kasus DBD</div>
    """, unsafe_allow_html=True)

    chart_container = st.container(border=True)
    with chart_container:
        fig, ax = plt.subplots(figsize=(12, 5))
        style_ax(ax, fig)

        if sel_prov:
            for i, prov in enumerate(sel_prov):
                sub = (
                    df_f[df_f["provinsi"] == prov]
                    .groupby("tahun")["jumlah_kasus_bulat"].sum()
                )
                c = PALETTE[i % len(PALETTE)]
                if chart_type == "Grafik Garis":
                    ax.plot(sub.index, sub.values, marker="o", linewidth=2,
                            label=prov, color=c)
                else:
                    ax.bar(sub.index + i * 0.15, sub.values, width=0.15,
                           label=prov, color=c)
            ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COL)
            ax.set_title(f"Tren DBD: {', '.join(sel_prov)}", color=TEXT_COL)
        else:
            sub = df_f.groupby("tahun")["jumlah_kasus_bulat"].sum()
            if chart_type == "Grafik Garis":
                ax.fill_between(sub.index, sub.values, alpha=0.12, color=ACCENT)
                ax.plot(sub.index, sub.values, marker="o", linewidth=2.5, color=ACCENT)
            else:
                ax.bar(sub.index, sub.values, color=ACCENT, alpha=0.85)
            ax.set_title("Tren DBD Nasional", color=TEXT_COL)

        ax.set_xlabel("Tahun")
        ax.set_ylabel("Jumlah Kasus")
        st.pyplot(fig)
        plt.close()

    st.divider()

    # ── Province Profile ──────────────────────────────────────────────────────
    if not sel_prov:
        st.info("💡 Pilih provinsi di atas untuk melihat Profil Provinsi.")
        return

    st.markdown("""
    <div class="section-header"><div class="icon-badge">📋</div> Profil Provinsi</div>
    <p class="section-sub">Rata-rata faktor eksternal per provinsi berdasarkan rentang tahun yang dipilih.</p>
    """, unsafe_allow_html=True)

    profile_cols = {
        "curah_hujan"                    : "🌧️ Curah Hujan (mm)",
        "suhu"                           : "🌡️ Suhu (°C)",
        "kelembaban"                     : "💧 Kelembaban (%)",
        "persentase_mobilitas"           : "🚗 Mobilitas (%)",
        "persentase_akses_sanitasi_layak": "🚿 Sanitasi Layak (%)",
        "persentase_akses_air_layak"     : "💦 Akses Air (%)",
        "jumlah_penduduk"                : "👥 Jumlah Penduduk",
    }
    available_cols = {k: v for k, v in profile_cols.items() if k in df_f.columns}

    for prov in sel_prov:
        df_prov = df_f[df_f["provinsi"] == prov]

        if df_prov.empty:
            st.warning(f"Data tidak tersedia untuk {prov}.")
            continue

        st.markdown(f"""
        <div class="province-header"><div class="icon-badge-sm">📍</div> {prov}</div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            kasus_per_tahun = df_prov.groupby("tahun")["jumlah_kasus_bulat"].sum()
            total_kasus_prov = int(df_prov["jumlah_kasus_bulat"].sum())

            delta_str = "-"
            if len(kasus_per_tahun) >= 2:
                delta_prov = (
                    (kasus_per_tahun.iloc[-1] - kasus_per_tahun.iloc[-2])
                    / kasus_per_tahun.iloc[-2] * 100
                )
                delta_str = f"{delta_prov:+.1f}% vs tahun sebelumnya"

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Kasus", f"{total_kasus_prov:,}")
            mc2.metric("Rata-rata per Tahun",
                       f"{int(kasus_per_tahun.mean()):,}")
            mc3.metric("Tren Terakhir", delta_str)

            st.markdown("**Faktor Eksternal (rata-rata):**")
            items = list(available_cols.items())
            for row in [items[i:i+4] for i in range(0, len(items), 4)]:
                rcols = st.columns(len(row))
                for j, (col_key, col_label) in enumerate(row):
                    val     = df_prov[col_key].mean()
                    val_str = f"{int(val):,}" if col_key == "jumlah_penduduk" else f"{val:.1f}"
                    rcols[j].markdown(
                        f"""<div class="metric-card">
                            <div class="label">{col_label}</div>
                            <div class="value" style="font-size:20px">{val_str}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # Mini chart per provinsi
            fig_p, ax_p = plt.subplots(figsize=(10, 3))
            ax_p.fill_between(kasus_per_tahun.index, kasus_per_tahun.values,
                              alpha=0.12, color=ACCENT)
            ax_p.plot(kasus_per_tahun.index, kasus_per_tahun.values,
                      marker="o", linewidth=2, color=ACCENT)

            idx_max = kasus_per_tahun.idxmax()
            ax_p.scatter([idx_max], [kasus_per_tahun[idx_max]],
                         color="#ff6b6b", s=120, zorder=5,
                         label=f"Puncak: {idx_max}")
            ax_p.annotate(f"  {int(kasus_per_tahun[idx_max]):,}",
                          (idx_max, kasus_per_tahun[idx_max]),
                          color="#ff6b6b", fontsize=9)
            style_ax(ax_p, fig_p, f"Tren Kasus — {prov}")
            ax_p.set_xlabel("Tahun")
            ax_p.set_ylabel("Jumlah Kasus")
            ax_p.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)
            st.pyplot(fig_p)
            plt.close()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==================================================
    # EXPORT LAPORAN TREN DBD
    # ==================================================

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
    📥 Unduh Laporan Tren DBD
    </h2>

    <p style="
    color:#cbd5e1;
    font-size:15px;
    margin-bottom:0px;
    ">
    Unduh hasil analisis tren DBD dalam format CSV, Excel, dan PDF.
    </p>

    </div>
    """, unsafe_allow_html=True)

    export_df = df_f[
        ["provinsi", "tahun", "jumlah_kasus_bulat"]
    ].copy()

    col1, col2, col3 = st.columns(3)

    # ==========================
    # CSV
    # ==========================

    with col1:

        st.success("📋 CSV")

        st.download_button(
            "⬇ Download CSV",
            dataframe_to_csv(export_df),
            file_name="tren_dbd.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ==========================
    # EXCEL
    # ==========================

    with col2:

        st.info("📊 Excel")

        st.download_button(
            "⬇ Download Excel",
            dataframe_to_excel(export_df),
            file_name="tren_dbd.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # ==========================
    # PDF
    # ==========================

    with col3:

        st.warning("📄 PDF")

        if st.button(
            "📄 Generate PDF Tren",
            use_container_width=True
        ):

            try:

                # --------------------------------
                # Ringkasan
                # --------------------------------

                total_cases = int(
                    df_f["jumlah_kasus_bulat"].sum()
                )

                prov_summary = (
                    df_f.groupby("provinsi")
                    ["jumlah_kasus_bulat"]
                    .sum()
                    .sort_values(ascending=False)
                )

                top_prov = (
                    prov_summary.index[0]
                    if len(prov_summary)
                    else "-"
                )

                low_prov = (
                    prov_summary.index[-1]
                    if len(prov_summary)
                    else "-"
                )

                # --------------------------------
                # Tabel Historis
                # --------------------------------

                trend_table = ""

                trend_df = (
                    df_f.groupby(
                        ["provinsi", "tahun"]
                    )["jumlah_kasus_bulat"]
                    .sum()
                    .reset_index()
                )

                for _, row in trend_df.iterrows():

                    trend_table += f"""
                    <tr>
                        <td>{row['provinsi']}</td>
                        <td>{int(row['tahun'])}</td>
                        <td>{int(row['jumlah_kasus_bulat']):,}</td>
                    </tr>
                    """

                # --------------------------------
                # Province Profile
                # --------------------------------

                profile_html = ""

                for prov in sel_prov:

                    df_prov = df_f[
                        df_f["provinsi"] == prov
                    ]

                    kasus_per_tahun = (
                        df_prov.groupby("tahun")
                        ["jumlah_kasus_bulat"]
                        .sum()
                    )

                    total_kasus = int(
                        df_prov["jumlah_kasus_bulat"].sum()
                    )

                    rata_kasus = int(
                        kasus_per_tahun.mean()
                    )

                    profile_html += f"""

                    <div class="card">

                    <h4>{prov}</h4>

                    <p>
                    <b>Total Kasus:</b>
                    {total_kasus:,}
                    </p>

                    <p>
                    <b>Rata-rata per Tahun:</b>
                    {rata_kasus:,}
                    </p>

                    </div>

                    """

                # --------------------------------
                # Insight
                # --------------------------------

                insight_text = f"""
                Analisis dilakukan terhadap
                {len(sel_prov)} provinsi
                pada rentang tahun
                {thn_range[0]} hingga {thn_range[1]}.

                Provinsi dengan jumlah kasus
                tertinggi adalah {top_prov},
                sedangkan yang terendah adalah
                {low_prov}.
                """

                # --------------------------------
                # HTML PDF
                # --------------------------------

                html_content = f"""

                <div class="section">

                <h3>📈 Ringkasan Analisis</h3>

                <div class="card">

                <p>
                <b>Jumlah Provinsi:</b>
                {len(sel_prov)}
                </p>

                <p>
                <b>Rentang Tahun:</b>
                {thn_range[0]} - {thn_range[1]}
                </p>

                <p>
                <b>Total Kasus:</b>
                {total_cases:,}
                </p>

                <p>
                <b>Provinsi Tertinggi:</b>
                {top_prov}
                </p>

                <p>
                <b>Provinsi Terendah:</b>
                {low_prov}
                </p>

                <p>
                <b>Tipe Grafik:</b>
                {chart_type}
                </p>

                </div>

                </div>

                <div class="section">

                <h3>📊 Data Historis Lengkap</h3>

                <table>

                <tr>
                    <th>Provinsi</th>
                    <th>Tahun</th>
                    <th>Jumlah Kasus</th>
                </tr>

                {trend_table}

                </table>

                </div>

                <div class="section">

                <h3>📋 Province Profile</h3>

                {profile_html}

                </div>

                <div class="section">

                <h3>🤖 Insight Analisis</h3>

                <div class="card">

                <p>
                {insight_text}
                </p>

                </div>

                </div>

                """

                pdf_bytes = generate_pdf_via_api(
                    "Laporan Tren DBD",
                    html_content,
                    footer_text=(
                        "Sistem Prediksi Kasus DBD Indonesia - "
                        "Tren DBD"
                    )
                )

                st.download_button(
                    "⬇ Download PDF",
                    pdf_bytes,
                    file_name="laporan_tren_dbd.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"Gagal membuat PDF: {e}"
                )