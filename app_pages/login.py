"""
app_pages/login.py — Halaman Login & Register
"""

import streamlit as st
from utils.auth import login_user, register_user


def show():
    col_l, col_mid, col_r = st.columns([1, 2, 1])

    with col_mid:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 24px 0;">
            <div style="font-size:48px; margin-bottom:12px;">🦟</div>
            <div style="font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:800; color:var(--text-primary);">DBD Forecasting</div>
            <div style="color:var(--text-muted); font-size:14px; margin-top:4px;">Indonesia · 2020–2025</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Daftar Akun"])

        with tab_login:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            email    = st.text_input("Email", placeholder="contoh@email.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Masuk", use_container_width=True, key="btn_login"):
                if not email or not password:
                    st.error("Email dan password wajib diisi.")
                else:
                    with st.spinner("Memverifikasi..."):
                        user, err = login_user(email, password)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.session_state["user"] = user
                        st.success(f"✅ Selamat datang, **{user['nama']}**!")
                        st.rerun()

        with tab_register:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.info("Akun baru otomatis mendapat role **Viewer**. Hubungi Admin untuk mengubah role.")
            nama_reg     = st.text_input("Nama Lengkap", key="reg_nama")
            email_reg    = st.text_input("Email", placeholder="contoh@email.com", key="reg_email")
            password_reg = st.text_input("Password", type="password", key="reg_password")
            konfirm_reg  = st.text_input("Konfirmasi Password", type="password", key="reg_konfirm")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Daftar", use_container_width=True, key="btn_register"):
                if not all([nama_reg, email_reg, password_reg, konfirm_reg]):
                    st.error("Semua field wajib diisi.")
                elif password_reg != konfirm_reg:
                    st.error("Password dan konfirmasi tidak cocok.")
                elif len(password_reg) < 6:
                    st.error("Password minimal 6 karakter.")
                else:
                    with st.spinner("Mendaftarkan akun..."):
                        ok, err = register_user(nama_reg, email_reg, password_reg)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.success("✅ Akun berhasil dibuat! Silakan login.")

        st.markdown("""
        <div style="text-align:center; margin-top:32px; font-size:12px; color:var(--text-muted);">
            Kelompok 4 · DSGA · Dengue Disease Forecasting
        </div>
        """, unsafe_allow_html=True)