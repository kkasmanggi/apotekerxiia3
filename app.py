import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="Chatbot Apoteker Gemini",
    page_icon="💊",
    layout="wide"
)

st.title("👨‍⚕️ Chatbot Apoteker")
st.markdown("Selamat datang! Saya adalah chatbot apoteker Anda. Tanyakan pertanyaan tentang obat.")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Gunakan st.secrets untuk mengelola API Key dengan aman di Streamlit Cloud
# Pastikan Anda telah menambahkan [secrets] ke file .streamlit/secrets.toml
# Contoh:
# [secrets]
# gemini_api_key = "AIzaSy..."
# Jika Anda menjalankan secara lokal, Anda dapat menggunakan variabel lingkungan atau file .env
try:
    API_KEY = st.secrets["gemini_api_key"]
except (KeyError, FileNotFoundError):
    st.error("⚠️ Gemini API Key tidak ditemukan. Harap tambahkan API Key Anda ke file `.streamlit/secrets.toml`.")
    st.info("Kunjungi `https://aistudio.google.com/app/apikey` untuk mendapatkan API Key.")
    st.stop() # Hentikan aplikasi jika API Key tidak ada.

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# FUNGSI UNTUK INISIALISASI MODEL DAN CHAT
# ==============================================================================

def initialize_gemini():
    """Menginisialisasi model dan sesi chat Gemini."""
    genai.configure(api_key=API_KEY)
    
    # Inisialisasi model
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4, 
            max_output_tokens=500 
        )
    )

    # Definisikan konteks awal chatbot (initial context)
    initial_context = [
        {"role": "user", "parts": ["Saya adalah seorang apoteker. Berikan pertanyaan tentang obat. Jawaban singkat. Tolak pertanyaan non-obat."]},
        {"role": "model", "parts": ["Baik! Tanyakan obat yang ingin anda ketahui."]}
    ]

    # Mulai sesi chat dengan konteks awal
    chat_session = model.start_chat(history=initial_context)
    return chat_session

# ==============================================================================
# APLIKASI UTAMA STREAMLIT
# ==============================================================================

# Kelola riwayat chat menggunakan st.session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Tambahkan pesan pembuka dari model ke riwayat
    initial_context = [
        {"role": "user", "content": "Saya adalah seorang apoteker. Berikan pertanyaan tentang obat. Jawaban singkat. Tolak pertanyaan non-obat."},
        {"role": "model", "content": "Baik! Tanyakan obat yang ingin anda ketahui."}
    ]
    st.session_state.messages.extend(initial_context)

# Tampilkan riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.write(message["content"])

# Tangani input pengguna
if prompt := st.chat_input("Tanyakan sesuatu..."):
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Inisialisasi atau dapatkan sesi chat dari st.session_state
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = initialize_gemini()
    
    with st.chat_message("assistant"):
        with st.spinner("Sedang membalas..."):
            try:
                # Kirim pesan pengguna ke model
                response = st.session_state.chat_session.send_message(prompt)
                
                # Tampilkan dan simpan balasan
                if response and response.text:
                    st.write(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                else:
                    st.write("Maaf, saya tidak bisa memberikan balasan.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
