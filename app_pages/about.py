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
    
    Sistem Prediksi Kasus DBD Indonesia merupakan platform analitik berbasis
    machine learning yang dirancang untuk membantu proses pemantauan, analisis, 
    dan prediksi kasus Demam Berdarah Dengue (DBD) di seluruh provinsi Indonesia. 
    Sistem ini mengintegrasikan data historis kasus DBD dan faktor eksternal 
    lingkungan untuk menghasilkan prediksi yang dapat digunakan sebagai pendukung 
    pengambilan keputusan.

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

    c1, c2, c3, c4, c5 = st.columns(5)

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

    with c5:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">PDF/Excel</div>
            <div class="stat-label">Format Export</div>
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
               
    ✅ Menyediakan laporan otomatis dalam berbagai format

    """)

    st.divider()

    # ==================================================
    # FITUR
    # ==================================================

    st.markdown("## 🧩 Fitur Utama Sistem")

    col1, col2 = st.columns(2)

    with col1:

        st.info("""
    ### 🏠 Dashboard Nasional

    Menampilkan kondisi nasional DBD Indonesia,
    ringkasan statistik, insight AI, serta wilayah risiko tinggi.
    """)

        st.info("""
    ### 🔮 Prediksi Kasus

    Memprediksi jumlah kasus DBD masa depan
    menggunakan model Machine Learning terbaik.
    """)

        st.info("""
    ### 📈 Tren DBD

    Membandingkan tren perkembangan kasus
    antar provinsi secara interaktif.
    """)

        st.info("""
    ### 🔬 Analisis Faktor Eksternal

    Menjelaskan faktor-faktor yang paling 
    memengaruhi perubahan jumlah kasus.

    """)


    with col2:

        st.info("""
    ### 📍 Analisis Provinsi

    Menyajikan profil lengkap setiap provinsi,
    tren kasus, dan tingkat risiko DBD.
    """)

        st.info("""
    ### ⚙️ Simulasi Variabel

    Melakukan what-if analysis terhadap
    faktor lingkungan dan sosial.
    """)

        st.info("""
    ### 🔬 Faktor Eksternal

    Mengidentifikasi faktor paling berpengaruh
    terhadap perubahan jumlah kasus DBD.
    """)

        st.info("""
    ### 🤖 AI Insight Generator

    Interpretasi otomatis menggunakan Google 
    Gemini AI.
    """)

    st.divider()

    # ==================================================
    # DATASET
    # ==================================================

    st.markdown("## 🗂️ Sumber Dataset")

    c1, c2 = st.columns(2)

    with c1:

        st.info("""
    ### 🦟 Data Kasus DBD

    Data historis kasus DBD seluruh provinsi
    Indonesia periode 2020–2025.

    Digunakan sebagai target prediksi sistem.
                
    Dataset dikumpulkan dari berbagai sumber resmi untuk memperoleh cakupan nasional yang lebih lengkap.

    Sumber data:

    • Badan Pusat Statistik (BPS) – Kasus Penyakit Menurut Provinsi dan Jenis Penyakit

    • Kementerian Kesehatan Republik Indonesia (Kemenkes) – Data Kasus DBD Tahun 2020–2022

    • Badan Pusat Statistik (BPS) – Data Kasus DBD Provinsi Tahun 2023

    • Satu Data Indonesia – Data Kasus DBD Provinsi DKI Jakarta Tahun 2023

    """)
        
        st.info("""
    ### 🚰 Data Infrastruktur

    - Sanitasi layak
    - Akses air bersih
    - Mobilitas penduduk

    Digunakan sebagai faktor eksternal prediksi.
    
    Sumber data:
    
    • Persentase Rumah Tangga yang Memiliki Akses Sanitasi Layak Menurut Provinsi Tahun 2020–2025 – BPS

    • Persentase Rumah Tangga yang Memiliki Akses Sumber Air Minum Layak Menurut Provinsi Tahun 2020–2025 – BPS

    • Badan Pusat Statistik (BPS) – Data Mobilitas Penduduk Tahun 2020–2024

    """)

    with c2:

        st.info("""
    ### 👥 Data Kependudukan

    Data kepadatan penduduk digunakan untuk menggambarkan tingkat konsentrasi populasi yang dapat memengaruhi kecepatan penyebaran penyakit.

    Sumber data:

    • Badan Pusat Statistik (BPS) – Data Kepadatan Penduduk Tahun 2020–2025
    
    """)

        st.info("""
    ### 🌧️ Data Iklim

    Data iklim digunakan untuk menganalisis pengaruh kondisi lingkungan terhadap perkembangan populasi nyamuk Aedes aegypti sebagai vektor utama DBD.

    Variabel yang digunakan meliputi:

    • Curah hujan

    • Suhu udara

    • Kelembapan udara

    Sumber data:

    • Climate Data Daily Indonesia – Kaggle

    • Semarang Daily Climate Data 2020–2023 – Kaggle

    • Pontianak Weather Daily 2021–2024 – BMKG

    • NASA POWER Monthly Surface Meteorology 2020–2025 – NASA


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
    # CARA KERJA SISTEM
    # ==================================================

    st.markdown("## ⚙️ Cara Kerja Sistem")

    st.caption(
        "Alur kerja sistem mulai dari pengumpulan data hingga pembuatan laporan analitik."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.info("""
    ### 1️⃣ Akuisisi Data

    📥 Mengumpulkan data dari:

    • BPS

    • Kemenkes

    • BMKG

    • NASA POWER

    • Kaggle

    • Satu Data Indonesia
    """)

        st.info("""
    ### 2️⃣ Integrasi Data

    🔄 Seluruh dataset digabungkan menjadi satu dataset nasional.

    Proses:

    • Cleaning

    • Validasi

    • Normalisasi

    • Sinkronisasi waktu
    """)

        st.info("""
    ### 3️⃣ Feature Engineering

    🧩 Membentuk fitur analitik:

    • Lag 1 Tahun

    • Lag 2 Tahun

    • Lag 3 Tahun

    • Rolling Mean

    • Growth Rate

    • Faktor Eksternal
    """)

        st.info("""
    ### 4️⃣ Penyimpanan Database

    ☁️ Dataset tersimpan pada Supabase.

    Digunakan untuk:

    • Dashboard

    • Prediksi

    • Analisis

    • Export
    """)

    with col2:

        st.info("""
    ### 5️⃣ Machine Learning

    🤖 Model yang digunakan:

    • Random Forest

    • XGBoost

    • Ensemble Model

    Digunakan untuk memprediksi kasus DBD.
    """)

        st.info("""
    ### 6️⃣ Explainable AI

    🔬 Analisis faktor dominan:

    • Feature Importance

    • Ranking Faktor

    • Analisis Risiko

    • Interpretasi Faktor
    """)

        st.info("""
    ### 7️⃣ AI Insight Generator

    🧠 Google Gemini AI menghasilkan:

    • Insight Nasional

    • Insight Provinsi

    • Insight Simulasi

    • Rekomendasi Kebijakan
    """)

        st.info("""
    ### 8️⃣ Dashboard & Export

    📊 Hasil ditampilkan dalam dashboard interaktif.

    📄 PDF

    📈 Excel

    📋 CSV
    """)

    st.success("""
    ### 🎯 Hasil Akhir Sistem

    Seluruh proses menghasilkan platform analitik DBD berbasis Artificial Intelligence dan Machine Learning yang mampu membantu pengguna:

    ✅ Memahami kondisi DBD nasional dan provinsi

    ✅ Mengidentifikasi faktor penyebab peningkatan kasus

    ✅ Melakukan simulasi kebijakan

    ✅ Membandingkan tren antar wilayah

    ✅ Memprediksi kasus pada periode mendatang

    ✅ Menghasilkan laporan profesional secara otomatis
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
    # INOVASI SISTEM
    # ==================================================

    st.markdown("## 🚀 Inovasi Sistem")

    st.markdown("""
    Sistem Prediksi Kasus DBD Indonesia mengintegrasikan berbagai pendekatan
    analitik modern ke dalam satu platform yang terintegrasi.

    ### Inovasi yang diterapkan:

    - 📊 Dashboard visual interaktif
    - 🤖 Prediksi berbasis Machine Learning
    - 🔬 Explainable AI melalui Feature Importance
    - 🧠 AI Narrative menggunakan Gemini AI
    - ⚙️ What-if Analysis melalui Simulasi Variabel
    - ☁️ Integrasi Database Supabase
    - 📥 Export Laporan PDF, Excel, dan CSV
    - 🎯 Pendukung pengambilan keputusan berbasis data

    Dengan pendekatan tersebut, sistem tidak hanya menampilkan data,
    tetapi juga membantu pengguna memahami faktor penyebab,
    menganalisis risiko, dan merancang strategi mitigasi DBD secara lebih efektif.
    """)

    st.divider()

    # ==================================================
    # MANFAAT
    # ==================================================

    st.markdown("## 🎯 Manfaat Sistem")

    col1, col2 = st.columns(2)

    with col1:

        st.success("""
    ### 🏛️ Untuk Pemerintah

    ✅ Perencanaan intervensi

    ✅ Prioritas wilayah risiko tinggi

    ✅ Early Warning System

    ✅ Pendukung kebijakan kesehatan
    """)

        st.success("""
    ### 🏥 Untuk Dinas Kesehatan

    ✅ Monitoring kasus DBD

    ✅ Analisis risiko wilayah

    ✅ Evaluasi program pengendalian

    ✅ Penyusunan strategi mitigasi
    """)

    with col2:

        st.success("""
    ### 🔬 Untuk Peneliti

    ✅ Analisis faktor penyebab

    ✅ Evaluasi pengaruh variabel

    ✅ Pengembangan model prediksi

    ✅ Penelitian epidemiologi
    """)

        st.success("""
    ### 👨‍👩‍👧‍👦 Untuk Masyarakat

    ✅ Edukasi kesehatan

    ✅ Peningkatan kewaspadaan dini

    ✅ Pemahaman faktor risiko

    ✅ Kesadaran pencegahan DBD
    """)

    st.divider()
    # ==================================================
    # SISTEM EXPORT
    # ==================================================

    st.markdown("## 📥 Sistem Export Laporan")

    st.success("""
    Sistem mendukung pembuatan laporan otomatis dalam berbagai format:

    ✅ PDF Report

    ✅ Microsoft Excel (.xlsx)

    ✅ CSV Dataset

    Laporan dapat dihasilkan dari:

    • Dashboard Nasional

    • Analisis Provinsi

    • Prediksi Kasus

    • Tren DBD

    • Simulasi Variabel

    • Faktor Eksternal
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