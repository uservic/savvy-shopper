import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://backend:8000")

st.set_page_config(page_title="SavvyShopper", page_icon="🛍️", layout="centered")
st.title("🛍️ SavvyShopper")
st.caption("Независимый ИИ-консьерж: анализ форумов без рекламы и честный ценовой коридор")

query = st.chat_input("Например: Хочу в подарок купить что-то из флагманов телефонов самсунг")

if query:
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("Создаю исследовательскую сессию...")

        resp = requests.post(f"{API_URL}/api/v1/sessions", json={"query": query, "domain": "smartphones"})
        if resp.status_code != 201:
            st.error("Ошибка связи с сервером FastAPI")
        else:
            session_data = resp.json()
            session_id = session_data["id"]

            while session_data["status"] in ("PENDING", "PROCESSING"):
                status_placeholder.info(f"⏳ {session_data['current_step']}")
                time.sleep(1)
                session_data = requests.get(f"{API_URL}/api/v1/sessions/{session_id}").json()

            if session_data["status"] == "COMPLETED":
                status_placeholder.empty()
                st.markdown(session_data["result_markdown"])

                # Визуализация ценового коридора (US-004)
                corridor = session_data.get("price_corridor")
                if corridor and corridor.get("offers"):
                    st.subheader("📊 Разброс рыночных цен (₽)")
                    chart_data = {item["title"]: item["price_rub"] for item in corridor["offers"]}
                    st.bar_chart(chart_data)

                st.download_button(
                    label="📥 Скачать справку (.md)",
                    data=session_data["result_markdown"],
                    file_name=f"savvy_report_{session_id[:8]}.md",
                    mime="text/markdown",
                )
            else:
                status_placeholder.error(f"Сбой обработки: {session_data.get('error_message')}")
