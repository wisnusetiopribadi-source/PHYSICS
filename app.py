import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================
# Ambil API key dari Streamlit secrets
API_KEY = st.secrets["gemini_api_key"]

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli fisika. Tuliskan rumus tentang fisika. jawaban singkat. Tolak pertanyaan non-fisika."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan rumus yang ingin anda ketahui."]
    }
]

# ==============================================================================
# KONFIGURASI STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Ahli Fisika Chatbot", page_icon="⚛️")
st.title("Ahli Fisika Chatbot ⚛️")
st.markdown("Tanyakan seputar rumus-rumus fisika. Chatbot ini akan menolak pertanyaan di luar topik fisika.")

# ==============================================================================
# FUNGSI UTAMA APLIKASI
# ==============================================================================

# Konfigurasi genai (hanya sekali)
if "model" not in st.session_state:
    try:
        genai.configure(api_key=API_KEY)
        st.session_state.model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
    except Exception as e:
        st.error(f"Kesalahan saat menginisialisasi Gemini API: {e}")
        st.stop()

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Tampilkan riwayat chat sebelumnya
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model" and message["parts"][0] != "Baik! Berikan rumus yang ingin anda ketahui.":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# Tangani input dari pengguna
if prompt := st.chat_input("Tanyakan sesuatu tentang fisika..."):
    # Tampilkan pesan pengguna di antarmuka
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim riwayat chat ke model
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                # Perbarui riwayat chat untuk Gemini
                gemini_history = [
                    {"role": "user" if msg["role"] == "user" else "model", "parts": msg["parts"]}
                    for msg in st.session_state.messages
                ]
                
                # Menggunakan start_chat untuk memulai sesi baru dengan riwayat lengkap
                chat_session = st.session_state.model.start_chat(history=gemini_history)
                
                # Kirim input terakhir saja
                response = chat_session.send_message(prompt)
                
                # Tampilkan balasan
                st.markdown(response.text)
                
                # Simpan balasan ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [response.text]})

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                # Hapus pesan terakhir jika terjadi error
                st.session_state.messages.pop()
