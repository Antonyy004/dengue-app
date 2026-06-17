"""
app_pages/admin_users.py — Halaman Kelola User (Admin only)
"""

import streamlit as st
from utils.auth import get_all_users, update_user_role, toggle_user_active, register_user


def show():
    st.markdown("""
    <div class="section-header">
        <div class="icon-badge">👥</div>
        Kelola User
    </div>
    <p class="section-sub">Manajemen akun pengguna aplikasi DBD Forecasting</p>
    """, unsafe_allow_html=True)

    with st.expander("➕ Tambah User Baru", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nama_baru  = st.text_input("Nama Lengkap", key="admin_nama")
            email_baru = st.text_input("Email", key="admin_email")
        with col2:
            pass_baru = st.text_input("Password", type="password", key="admin_pass")
            role_baru = st.selectbox("Role", ["viewer", "researcher", "admin"], key="admin_role")

        if st.button("Tambah User", key="btn_tambah_user"):
            if not all([nama_baru, email_baru, pass_baru]):
                st.error("Semua field wajib diisi.")
            elif len(pass_baru) < 6:
                st.error("Password minimal 6 karakter.")
            else:
                ok, err = register_user(nama_baru, email_baru, pass_baru, role_baru)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.success(f"✅ User **{nama_baru}** berhasil ditambahkan sebagai **{role_baru}**.")
                    st.rerun()

    st.divider()

    df, err = get_all_users()
    if err:
        st.error(f"Gagal memuat data user: {err}")
        return
    if df.empty:
        st.info("Belum ada user terdaftar.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total User",  len(df))
    col2.metric("Admin",       len(df[df["role"] == "admin"]))
    col3.metric("Researcher",  len(df[df["role"] == "researcher"]))
    col4.metric("Viewer",      len(df[df["role"] == "viewer"]))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    current_user_id = st.session_state["user"]["id"]

    for _, row in df.iterrows():
        is_self = (row["id"] == current_user_id)
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

            with c1:
                status_icon = "🟢" if row["is_active"] else "🔴"
                st.markdown(f"**{row['nama']}** {status_icon}")
                st.caption(row["email"])

            with c2:
                role_icon = {"admin": "🔴", "researcher": "🟡", "viewer": "🔵"}.get(row["role"], "⚪")
                st.markdown(f"{role_icon} `{row['role']}`")
                st.caption(str(row["created_at"])[:10])

            with c3:
                if not is_self:
                    role_options = ["viewer", "researcher", "admin"]
                    new_role = st.selectbox(
                        "role", role_options,
                        index=role_options.index(row["role"]),
                        key=f"role_{row['id']}",
                        label_visibility="collapsed"
                    )
                    if new_role != row["role"]:
                        if st.button("Simpan", key=f"save_{row['id']}", use_container_width=True):
                            ok, err = update_user_role(row["id"], new_role)
                            if ok:
                                st.rerun()
                            else:
                                st.error(err)
                else:
                    st.caption("(akun kamu)")

            with c4:
                if not is_self:
                    if row["is_active"]:
                        if st.button("🚫 Nonaktifkan", key=f"deact_{row['id']}", use_container_width=True):
                            ok, err = toggle_user_active(row["id"], False)
                            if ok:
                                st.rerun()
                    else:
                        if st.button("✅ Aktifkan", key=f"act_{row['id']}", use_container_width=True):
                            ok, err = toggle_user_active(row["id"], True)
                            if ok:
                                st.rerun()