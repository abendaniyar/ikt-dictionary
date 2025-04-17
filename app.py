import streamlit as st
import json

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

# Іздеу функциясын қосу
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

# Дәрістерді навигатор ретінде көрсету
lecture = st.sidebar.radio("📂 Дәріс таңдаңыз:", list(terms.keys()))

st.header(lecture)

# Іздеу сұранысына сәйкес терминдерді сүзу
if lecture in terms:
    filtered_terms = [term for term in terms[lecture] if search_query in term['kk'].lower() or search_query in term['ru'].lower() or search_query in term['en'].lower()]

    if search_query and not filtered_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")

    for term in filtered_terms if search_query else terms[lecture]:
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
else:
    st.warning("Бұл дәрісте мәліметтер табылмады. Басқа дәрісті таңдаңыз.")

st.success("Іздеу функциясы қосылды! 🚀 Терминдерді табу енді оңайырақ.")
