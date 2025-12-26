import streamlit as st
import os
import time
from pipeline.rag_engine import generate_answer
from config import ENABLE_HYBRID_RAG

# Page Config
st.set_page_config(
    page_title="Hacettepe Akademik Asistan",
    page_icon="🎓",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/tr/thumb/3/30/Hacettepe_Üniversitesi_Logosu.svg/1200px-Hacettepe_Üniversitesi_Logosu.svg.png", width=100)
    st.title("Ayarlar")
    st.divider()
    
    st.caption("Model Durumu")
    st.success("🟢 Sistem Hazır")
    
    if ENABLE_HYBRID_RAG:
        st.info("✨ Hybrid RAG Aktif")
    else:
        st.warning("⚠️ Hybrid RAG Kapalı")
        
    st.divider()
    st.markdown("### 📝 Hakkında")
    st.markdown("""
    Bu sistem Hacettepe Üniversitesi akademik yönetmelikleri kullanılarak geliştirilmiştir.
    
    **v2.0 (Docling + Layout Intelligence)**
    """)

# Main Screen
st.title("🎓 Hacettepe Akademik Asistan")
st.markdown("Merak ettiğiniz yönetmelik, mezuniyet şartı veya ders kuralını sorun.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Belgeler taranıyor..."):
            try:
                # Call RAG Engine
                response = generate_answer(prompt)
                
                # Simple typing effect simulation is redundant if response is instant, 
                # but nice for UX. RAG is synchronous so we just display it.
                message_placeholder.markdown(response)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

# Footer
st.markdown("---")
st.caption("⚠️ Yasal Uyarı: Bu asistan sadece bilgilendirme amaçlıdır. Resmi kararlar için öğrenci işlerine başvurunuz.")
