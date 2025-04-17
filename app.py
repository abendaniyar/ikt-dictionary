
import streamlit as st
import json
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

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
else:
    st.warning("Бұл дәрісте мәліметтер табылмады. Басқа дәрісті таңдаңыз.")
