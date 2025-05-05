import streamlit as st
import json
import pandas as pd

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

if 'selected_term' not in st.session_state:
    st.session_state['selected_term'] = None

# Excel жүктеу
uploaded_file = st.sidebar.file_uploader("📤 Excel файл жүктеу (жаңа терминдер)", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        new_terms = []
        for _, row in df.iterrows():
            term = {
                'kk': row.get('kk', ''),
                'ru': row.get('ru', ''),
                'en': row.get('en', ''),
                'definition': {
                    'kk': row.get('definition_kk', ''),
                    'ru': row.get('definition_ru', ''),
                    'en': row.get('definition_en', '')
                },
                'example': {
                    'kk': row.get('example_kk', ''),
                    'ru': row.get('example_ru', ''),
                    'en': row.get('example_en', '')
                },
                'relations': {
                    'synonyms': str(row.get('relations_synonyms', '')).split(',') if row.get('relations_synonyms') else [],
                    'general_concept': row.get('relations_general_concept', ''),
                    'specific_concepts': str(row.get('relations_specific_concepts', '')).split(',') if row.get('relations_specific_concepts') else [],
                    'associative': str(row.get('relations_associative', '')).split(',') if row.get('relations_associative') else []
                }
            }
            new_terms.append(term)

        lecture_name = st.sidebar.selectbox("📚 Қай дәріске қосылады?", list(terms.keys()))
        if st.sidebar.button("➕ Терминдерді қосу"):
            terms[lecture_name].extend(new_terms)
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(terms, f, ensure_ascii=False, indent=2)
            st.success(f"✅ {len(new_terms)} жаңа термин қосылды!")
    except Exception as e:
        st.error(f"❌ Excel файлды оқу кезінде қате: {e}")

# Іздеу функциясын қосу
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

# Дәріс таңдауы
lecture = st.sidebar.radio("📂 Дәріс таңдаңыз:", list(terms.keys()))

# Термин тізімі
if not search_query:
    st.write("### 📋 Терминдер тізімі:")
    for i, term in enumerate(terms[lecture]):
        name = term.get("kk", "")
        if st.button(f"🔹 {name}", key=f"term_{i}"):
            st.session_state['selected_term'] = name

# Термин мәліметі
selected = st.session_state.get("selected_term")
if selected:
    for term in terms[lecture]:
        if term.get("kk", "") == selected:
            term_text = f"{term.get('kk', '')} / {term.get('ru', '')} / {term.get('en', '')}"
            st.markdown(f"### 🖥 {term_text}")

            st.markdown("**📖 Анықтама:**")
            st.markdown(f"**KK:** {term['definition'].get('kk', 'Жоқ')}")
            st.markdown(f"**RU:** {term['definition'].get('ru', 'Нет')}")
            st.markdown(f"**EN:** {term['definition'].get('en', 'No')}")

            st.markdown("**💬 Мысал:**")
            st.markdown(f"**KK:** {term['example'].get('kk', 'Жоқ')}")
            st.markdown(f"**RU:** {term['example'].get('ru', 'Нет')}")
            st.markdown(f"**EN:** {term['example'].get('en', 'No')}")

            if term.get("image"):
                st.image(term["image"], width=200)
            if term.get("source"):
                st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")
