import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

# Mengatur judul halaman aplikasi web
st.set_page_config(
    page_title="Chatbot Apoteker",
    page_icon="💊",
    layout="wide"
)

# Menambahkan judul utama di antarmuka web
st.title("👨‍⚕️ Chatbot Apoteker Berbasis Gemini 💊")
st.markdown("Aplikasi ini dibuat menggunakan Google Gemini API. Tanyakan seputar obat dan kesehatan.")
st.markdown("---")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING!)
# ==============================================================================

# Mengambil API Key dari Streamlit Secrets atau variabel lingkungan (environment variable).
# Ini adalah cara yang aman untuk menyimpan kredensial di Streamlit Cloud.
# API key tidak boleh dikodekan secara langsung dalam file.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Pastikan Anda telah mengaturnya di Streamlit Secrets.")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot
INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", "parts": ["Saya adalah seorang apoteker. Berikan pertanyaan tentang obat. Jawaban singkat. Tolak pertanyaan non-obat."]},
    {"role": "model", "parts": ["Baik! Tanyakan obat yang ingin anda ketahui."]}
]

# ==============================================================================
# FUNGSI-FUNGSI UTAMA UNTUK LOGIKA CHAT
# ==============================================================================

# Inisialisasi model dan sesi chat
@st.cache_resource(show_spinner=False)
def get_model_and_chat_session():
    """Menginisialisasi model Gemini dan sesi chat."""
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
    # Memulai sesi chat dengan riwayat awal
    chat = model.start_chat(history=INITIAL_CHATBOT_CONTEXT)
    return chat

# ==============================================================================
# LOGIKA UTAMA APLIKASI STREAMLIT
# ==============================================================================

# Ambil objek chat yang sudah diinisialisasi
chat = get_model_and_chat_session()

# Inisialisasi riwayat chat di Streamlit's session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat yang sudah ada di antarmuka
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Tangani input dari pengguna
if prompt := st.chat_input("Tanyakan tentang obat..."):
    # Tambahkan input pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Tampilkan input pengguna di antarmuka
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim input pengguna ke model Gemini
    try:
        with st.spinner("Sedang mencari jawaban..."):
            response = chat.send_message(prompt, request_options={"timeout": 60})
            ai_response = response.text
    except Exception as e:
        ai_response = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}"

    # Tampilkan respons dari model
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    # Tambahkan respons dari model ke riwayat chat
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
