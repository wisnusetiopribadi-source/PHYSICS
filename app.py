import streamlit as st
import google.generativeai as genai
import os
import re

# ==============================================================================
# KONFIGURASI DAN PENGATURAN
# ==============================================================================
st.set_page_config(page_title="Ahli Fisika Chatbot", page_icon="⚛️", layout="wide")
st.title("Ahli Fisika Chatbot ⚛️")
st.markdown("Tanyakan seputar rumus-rumus fisika. Chatbot ini akan menolak pertanyaan di luar topik fisika. Anda dapat memasukkan rumus dalam format LaTeX seperti `$$E=mc^2$$`.")

# Ambil API key dari Streamlit secrets
try:
    API_KEY = st.secrets["gemini_api_key"]
except KeyError:
    st.error("API Key tidak ditemukan di Streamlit secrets. Harap tambahkan API Key Anda.")
    st.info("Kunjungi Streamlit Cloud, buka pengaturan aplikasi, dan tambahkan `gemini_api_key`.")
    st.stop()

MODEL_NAME = 'gemini-1.5-flash'

# Konteks awal chatbot
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli FISIKA. Berikan rumus yang ingin anda ketahui. Jawaban singkat dan faktual. Jika memungkinkan, gunakan notasi LaTeX untuk rumus. Tolak pertanyaan non-fisika."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan memberikan rumus fisika. Silakan ketikkan rumus yang ingin Anda ketahui."]
    }
]

# ==============================================================================
# MANAJEMEN SESI DAN CHAT
# ==============================================================================

# Konfigurasi Gemini API (hanya sekali)
@st.cache_resource
def configure_model():
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        return model
    except Exception as e:
        st.error(f"Kesalahan saat menginisialisasi Gemini API: {e}")
        return None

model = configure_model()
if not model:
    st.stop()

# Inisialisasi riwayat chat di session state
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Fungsi untuk memformat respons dengan LaTeX
def format_response(text):
    # Mengganti notasi $$...$$ menjadi tag HTML untuk rendering LaTeX
    return re.sub(r'\$\$(.*?)\$\$', r'<div>\(\1\)</div>', text, flags=re.DOTALL)

# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model" and "Baik! Saya akan memberikan rumus fisika" not in message["parts"][0]:
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# ==============================================================================
# INTERAKSI PENGGUNA
# ==============================================================================

if prompt := st.chat_input("Ketikkan pertanyaan Anda..."):
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim riwayat chat ke model dan dapatkan respons
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                # Siapkan riwayat chat untuk Gemini
                gemini_history = [
                    {"role": "user" if msg["role"] == "user" else "model", "parts": msg["parts"]}
                    for msg in st.session_state.messages
                ]
                
                # Menggunakan start_chat untuk memulai sesi baru dengan riwayat lengkap
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                
                # Tampilkan balasan
                st.markdown(response.text)
                
                # Tambahkan balasan ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [response.text]})

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                # Hapus pesan terakhir jika terjadi error
                st.session_state.messages.pop()
