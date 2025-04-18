import streamlit as st
import json

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

# Іздеу функциясын қосу
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

if search_query:
    st.header(f"🔎 Іздеу нәтижелері: \"{search_query}\"")

    found_terms = []  # Барлық дәрістерден сәйкес терминдерді жинайтын тізім

    for lecture, term_list in terms.items():
        for term in term_list:
            if search_query in term['kk'].lower() or search_query in term['ru'].lower() or search_query in term['en'].lower():
                found_terms.append((lecture, term))

    if not found_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")
    else:
        for lecture, term in found_terms:
            st.subheader(f"📂 {lecture} | 🖥 {term['kk']} / {term['ru']} / {term['en']}")

            with st.expander("📖 Анықтама / Определение / Definition"):
                st.markdown(f"**KK:** {term['definition']['kk']}")
                st.markdown(f"**RU:** {term['definition']['ru']}")
                st.markdown(f"**EN:** {term['definition']['en']}")

            with st.expander("💬 Мысал / Пример / Example"):
                st.markdown(f"**KK:** {term['example']['kk']}")
                st.markdown(f"**RU:** {term['example']['ru']}")
                st.markdown(f"**EN:** {term['example']['en']}")

            if term.get("image"):
                st.image(term['image'], caption="Иллюстрация", use_column_width=True)

            if term.get("source"):
                st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")

            st.markdown("---")
else:
    # Дәрістерді навигатор ретінде көрсету
    lecture = st.sidebar.radio("📂 Дәріс таңдаңыз:", list(terms.keys()))
    st.header(lecture)

    if lecture in terms:
        for term in terms[lecture]:
            st.subheader(f"🖥 {term['kk']} / {term['ru']} / {term['en']}")

            with st.expander("📖 Анықтама / Определение / Definition"):
                st.markdown(f"**KK:** {term['definition']['kk']}")
                st.markdown(f"**RU:** {term['definition']['ru']}")
                st.markdown(f"**EN:** {term['definition']['en']}")

            with st.expander("💬 Мысал / Пример / Example"):
                st.markdown(f"**KK:** {term['example']['kk']}")
                st.markdown(f"**RU:** {term['example']['ru']}")
                st.markdown(f"**EN:** {term['example']['en']}")

            if term.get("image"):
                st.image(term['image'], caption="Иллюстрация", use_column_width=True)

            if term.get("source"):
                st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")

            st.markdown("---")

