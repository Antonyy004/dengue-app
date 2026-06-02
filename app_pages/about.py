import streamlit as st


def show():

    # ==================================================
    # CUSTOM STYLE
    # ==================================================

    st.markdown("""
    <style>

    .hero {
        background: linear-gradient(135deg,#0a192f,#112240);
        padding:35px;
        border-radius:18px;
        border:1px solid #233554;
        margin-bottom:25px;
    }

    .hero-title{
        font-size:40px;
        font-weight:800;
        color:#64ffda;
    }

    .hero-sub{
        font-size:18px;
        color:#ccd6f6;
        margin-top:10px;
    }

    .section-title{
        color:#64ffda;
        margin-top:20px;
    }

    .custom-card{
        background:#112240;
        padding:20px;
        border-radius:15px;
        border:1px solid #233554;
        margin-bottom:15px;
    }

    .custom-card h4{
        color:#64ffda;
    }

    .dataset-card{
        background:#0a192f;
        padding:18px;
        border-left:4px solid #64ffda;
        border-radius:12px;
        margin-bottom:15px;
    }
    
    .stat-card{
        background:#112240;
        border:1px solid #233554;
        border-radius:16px;
        padding:20px;
        text-align:center;
    }

    .stat-number{
        font-size:32px;
        font-weight:800;
        color:#64ffda;
    }

    .stat-label{
        color:#8892b0;
        font-size:14px;
        margin-top:6px;
    }

    .tech-badge{
        display:inline-block;
        padding:8px 15px;
        margin:5px;
        background:#112240;
        border:1px solid #64ffda;
        border-radius:25px;
        color:#64ffda;
    }

    </style>
    """, unsafe_allow_html=True)

    # ==================================================
    # HERO SECTION
    # ==================================================

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#071a35,#0f274e);
    padding:40px;
    border-radius:20px;
    border:1px solid rgba(100,255,218,0.15);
    margin-bottom:25px;
    ">

    <h1 style="
    color:#64ffda;
    font-size:48px;
    font-weight:800;
    margin-bottom:15px;
    ">
    🦟 Sistem Prediksi Kasus DBD Indonesia
    </h1>

    <p style="
    color:#ccd6f6;
    font-size:18px;
    line-height:1.8;
    ">

    Platform analitik berbasis Artificial Intelligence dan Machine Learning
    yang dirancang untuk membantu memprediksi, menganalisis, dan
    memvisualisasikan perkembangan kasus Demam Berdarah Dengue (DBD)
    di Indonesia.

    </p>

    <br>

    <span style="background:rgba(100,255,218,0.12);padding:8px 15px;border-radius:20px;color:#64ffda;margin-right:8px;">
    📅 2020–2025
    </span>

    <span style="background:rgba(100,255,218,0.12);padding:8px 15px;border-radius:20px;color:#64ffda;margin-right:8px;">
    📍 38 Provinsi
    </span>

    <span style="background:rgba(100,255,218,0.12);padding:8px 15px;border-radius:20px;color:#64ffda;margin-right:8px;">
    🤖 Gemini AI
    </span>

    <span style="background:rgba(100,255,218,0.12);padding:8px 15px;border-radius:20px;color:#64ffda;">
    🧠 Machine Learning
    </span>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # QUICK STATS
    # ==================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">6</div>
            <div class="stat-label">Tahun Data</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">38</div>
            <div class="stat-label">Provinsi</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Kelompok Dataset</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">AI+ML</div>
            <div class="stat-label">Prediction Engine</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # LATAR BELAKANG
    # ==================================================

    st.markdown("## 🎯 Latar Belakang")

    st.markdown("""
    Indonesia merupakan salah satu negara dengan jumlah kasus Demam Berdarah Dengue (DBD)
    yang cukup tinggi setiap tahunnya. Faktor lingkungan, perubahan iklim, mobilitas masyarakat,
    kepadatan penduduk, sanitasi, dan akses air bersih memiliki peran penting dalam
    penyebaran penyakit ini.

    Aplikasi ini dikembangkan untuk mengintegrasikan berbagai sumber data menjadi sebuah
    dashboard analitik yang mampu membantu pengguna memahami kondisi DBD secara lebih
    komprehensif melalui visualisasi data, prediksi kasus, simulasi skenario, serta insight
    berbasis Artificial Intelligence.
    """)

    st.divider()

    # ==================================================
    # TUJUAN
    # ==================================================

    st.markdown("## 🎯 Tujuan Pengembangan")

    st.success("""
    ✅ Memantau perkembangan kasus DBD di Indonesia

    ✅ Melakukan prediksi jumlah kasus DBD pada periode mendatang

    ✅ Mengidentifikasi faktor-faktor yang memengaruhi peningkatan kasus

    ✅ Mendukung analisis risiko outbreak secara lebih dini

    ✅ Menyediakan simulasi berbagai skenario perubahan lingkungan

    ✅ Menghasilkan insight otomatis berbasis Artificial Intelligence
    """)

    st.divider()

    # ==================================================
    # FITUR
    # ==================================================

    st.markdown("## ✨ Fitur Utama Sistem")

    col1, col2 = st.columns(2)

    with col1:

        st.info("""
        🏠 Dashboard Nasional

        Menampilkan statistik nasional, insight AI, dan ringkasan kondisi DBD Indonesia.
        """)

        st.info("""
        🔮 Prediksi Kasus DBD

        Menghasilkan prediksi jumlah kasus DBD pada tingkat provinsi menggunakan Machine Learning.
        """)

        st.info("""
        📈 Analisis Tren DBD

        Visualisasi interaktif perkembangan kasus DBD dari waktu ke waktu.
        """)

    with col2:

        st.info("""
        🔬 Analisis Faktor Eksternal

        Menjelaskan faktor-faktor yang paling memengaruhi perubahan jumlah kasus.
        """)

        st.info("""
        ⚙️ Simulasi Variabel

        What-if analysis terhadap curah hujan, suhu, mobilitas, sanitasi, dan lainnya.
        """)

        st.info("""
        🤖 AI Insight Generator

        Interpretasi otomatis menggunakan Google Gemini AI.
        """)

    st.divider()

    # ==================================================
    # DATASET
    # ==================================================

    st.markdown("## 🗂️ Sumber Dataset")

    st.markdown("""
    ### 🦟 Data Kasus DBD

    - Kasus Penyakit Menurut Provinsi dan Jenis Penyakit (BPS)
    - Kasus DBD 2020–2022 (Kementerian Kesehatan RI)
    - Kasus DBD Provinsi Tahun 2023 (BPS)
    - Kasus DBD Jakarta Tahun 2023 (Satu Data Indonesia)
    """)

    st.markdown("""
    ### 🚗 Data Mobilitas Masyarakat

    - Mobilitas Penduduk 2020–2024 (BPS)
    - Forecasted Mobility Data 2025
    """)

    st.markdown("""
    ### 🌦️ Data Cuaca dan Iklim

    - Climate Data Daily IDN (Kaggle)
    - Semarang Daily Climate Data (Kaggle)
    - Pontianak Weather Daily (BMKG)
    - NASA POWER Surface Meteorology
    """)

    st.markdown("""
    ### 🚿 Data Sanitasi & Air Layak

    - Sanitasi Layak 2020–2025 (BPS)
    - Air Minum Layak 2020–2025 (BPS)
    """)

    st.markdown("""
    ### 👥 Data Kepadatan Penduduk

    - Kepadatan Penduduk Indonesia 2020–2025 (BPS)
    """)

    st.divider()

    # ==================================================
    # VARIABEL
    # ==================================================

    st.markdown("## 📊 Variabel yang Dianalisis")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("🌧️ Curah Hujan", "Aktif")
        st.metric("🌡️ Suhu", "Aktif")

    with c2:
        st.metric("💧 Kelembaban", "Aktif")
        st.metric("🚿 Sanitasi", "Aktif")

    with c3:
        st.metric("🚗 Mobilitas", "Aktif")
        st.metric("👥 Kepadatan", "Aktif")

    st.divider()

    # ==================================================
    # ARSITEKTUR
    # ==================================================

    st.markdown("## ⚙️ Cara Kerja Sistem")

    st.markdown("""
    1️⃣ **Data Collection**

    Pengumpulan data DBD, cuaca, mobilitas, sanitasi, dan kependudukan.

    2️⃣ **Data Integration & Cleaning**

    Seluruh dataset digabungkan dan dibersihkan.

    3️⃣ **Feature Engineering**

    Pembentukan variabel yang digunakan model.

    4️⃣ **Machine Learning Prediction**

    Prediksi jumlah kasus menggunakan Random Forest dan XGBoost.

    5️⃣ **AI Insight Generation**

    Google Gemini menghasilkan interpretasi otomatis.

    6️⃣ **Interactive Dashboard**

    Hasil disajikan dalam dashboard yang mudah dipahami.
    """)

    st.divider()

    # ==================================================
    # TEKNOLOGI
    # ==================================================

    st.markdown("## 🧠 Teknologi yang Digunakan")

    tech1, tech2, tech3 = st.columns(3)

    with tech1:

        st.info("""
    ### 💻 Framework & Data Processing

    - Python
    - Streamlit
    - Pandas
    - NumPy
    - Scikit-Learn
    """)

    with tech2:

        st.info("""
    ### 🤖 Artificial Intelligence & Machine Learning

    - Google Gemini API
    - Random Forest Regressor
    - XGBoost Regressor
    - Ensemble Prediction Model
    """)

    with tech3:

        st.info("""
    ### 📊 Visualisasi & Analytics

    - Plotly
    - Matplotlib
    - Interactive Dashboard
    - Data Storytelling
    """)

    st.divider()

    # ==================================================
    # MANFAAT
    # ==================================================

    st.markdown("## 🎯 Manfaat Sistem")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("""
        🏛️ Pemerintah

        Mendukung monitoring dan perencanaan program pencegahan DBD.
        """)

    with col2:
        st.success("""
        🔬 Peneliti

        Membantu eksplorasi dan analisis faktor risiko DBD.
        """)

    with col3:
        st.success("""
        👨‍👩‍👧‍👦 Masyarakat

        Meningkatkan kesadaran terhadap faktor penyebab DBD.
        """)

    st.divider()

    # ==================================================
    # DISCLAIMER
    # ==================================================

    st.markdown("## ⚠️ Disclaimer")

    st.warning("""
    Prediksi yang dihasilkan merupakan estimasi berbasis data historis dan model
    Machine Learning.

    Hasil prediksi tidak dimaksudkan sebagai pengganti keputusan medis maupun
    kebijakan kesehatan resmi, melainkan sebagai alat pendukung analisis dan
    pengambilan keputusan berbasis data.
    """)

    st.divider()

    st.caption(
        "🦟 Sistem Prediksi Kasus DBD Indonesia | AI • Machine Learning • Data Analytics"
    )