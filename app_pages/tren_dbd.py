"""
pages/tren_dbd.py — Visualisasi tren DBD & Province Profile
"""

import streamlit as st
import matplotlib.pyplot as plt
from utils.charts import style_ax, ACCENT, GRID_COL, TEXT_COL, DARK_BG, PALETTE
from utils.db import get_provinsi_list, get_tahun_list


def show(df_merge):
    st.title("📈 Visualisasi Tren DBD")

    prov_opts = get_provinsi_list(df_merge)
    thn_opts  = get_tahun_list(df_merge)

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

    chart_type = st.radio("Tipe Grafik", ["Line Chart", "Bar Chart"], horizontal=True)

    df_f = df_merge[
        (df_merge["tahun"] >= thn_range[0]) &
        (df_merge["tahun"] <= thn_range[1])
    ]
    if sel_prov:
        df_f = df_f[df_f["provinsi"].isin(sel_prov)]

    # ── Main chart ────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    style_ax(ax, fig)

    if sel_prov:
        for i, prov in enumerate(sel_prov):
            sub = (
                df_f[df_f["provinsi"] == prov]
                .groupby("tahun")["jumlah_kasus_bulat"].sum()
            )
            c = PALETTE[i % len(PALETTE)]
            if chart_type == "Line Chart":
                ax.plot(sub.index, sub.values, marker="o", linewidth=2,
                        label=prov, color=c)
            else:
                ax.bar(sub.index + i * 0.15, sub.values, width=0.15,
                       label=prov, color=c)
        ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COL)
        ax.set_title(f"Tren DBD: {', '.join(sel_prov)}", color=TEXT_COL)
    else:
        sub = df_f.groupby("tahun")["jumlah_kasus_bulat"].sum()
        if chart_type == "Line Chart":
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
        st.info("💡 Pilih provinsi di atas untuk melihat Province Profile.")
        return

    st.subheader("📋 Province Profile")
    st.markdown("Rata-rata faktor eksternal per provinsi berdasarkan rentang tahun dipilih.")

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
        st.markdown(f"#### 📍 {prov}")
        df_prov = df_f[df_f["provinsi"] == prov]

        if df_prov.empty:
            st.warning(f"Data tidak tersedia untuk {prov}.")
            continue

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

        st.divider()
