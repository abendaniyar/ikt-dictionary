import streamlit as st
import json
import pandas as pd
from streamlit.components.v1 import html
import streamlit.components.v1 as components

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

if 'selected_term' not in st.session_state:
    st.session_state['selected_term'] = None
if 'show_map' not in st.session_state:
    st.session_state['show_map'] = False

# Excel жүктеу
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Excel жолдарын қажетті JSON құрылымына түрлендіру
        def transform_row(row):
            return {
                "kk": row["kk"],
                "ru": row["ru"],
                "en": row["en"],
                "definition": {
                    "kk": row.get("definition_kk", ""),
                    "ru": row.get("definition_ru", ""),
                    "en": row.get("definition_en", "")
                },
                "example": {
                    "kk": row.get("example_kk", ""),
                    "ru": row.get("example_ru", ""),
                    "en": row.get("example_en", "")
                },
                "relations": {
                    "synonyms": [s.strip() for s in str(row.get("relations_synonyms", "")).split(",") if s.strip()],
                    "general_concept": row.get("relations_general_concept", ""),
                    "specific_concepts": [s.strip() for s in str(row.get("relations_specific_concepts", "")).split(",") if s.strip()],
                    "associative": [s.strip() for s in str(row.get("relations_associative", "")).split(",") if s.strip()]
                }
            }

        new_terms = [transform_row(row) for index, row in df.iterrows()]
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

def speak_buttons(term):
    kk = term.get('kk', '')
    ru = term.get('ru', '')
    en = term.get('en', '')
    html(f"""
        <div style='margin-bottom: 10px;'>
            <button onclick=\"speakRU()\" style='margin-right: 10px;'>🔊 Орысша</button>
            <button onclick=\"speakEN()\">🔊 Ағылшынша</button>
        </div>
        <script>
            function speakKK() {{
                var msg = new SpeechSynthesisUtterance("{kk}");
                msg.lang = "kk-KZ";
                window.speechSynthesis.speak(msg);
            }}
            function speakRU() {{
                var msg = new SpeechSynthesisUtterance("{ru}");
                msg.lang = "ru-RU";
                window.speechSynthesis.speak(msg);
            }}
            function speakEN() {{
                var msg = new SpeechSynthesisUtterance("{en}");
                msg.lang = "en-US";
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """, height=60)

# Дәріс таңдауы
lecture = st.sidebar.radio("📂 Дәріс таңдаңыз:", list(terms.keys()))

# Семантикалық картаны көру батырмасы
if st.sidebar.button("📚 Семантикалық картаны көру"):
    st.session_state['show_map'] = True
    components.html(
        """
        <html>
        <head><title>Семантикалық карта</title></head>
        <body>
        <h2>📚 Семантикалық карта</h2>
        <div style='font-family:Arial;'>
        """ +
        ''.join([
            f"<p><b>{term.get('kk', '')}</b> - " +
            (f"🔁 Синонимдер: {', '.join(term.get('relations', {{}}).get('synonyms', []))} | " if term.get('relations', {{}}).get('synonyms') else '') +
            (f"🔼 Жалпылама: {term.get('relations', {{}}).get('general_concept')} | " if term.get('relations', {{}}).get('general_concept') else '') +
            (f"🔽 Арнайы: {', '.join(term.get('relations', {{}}).get('specific_concepts', []))} | " if term.get('relations', {{}}).get('specific_concepts') else '') +
            (f"🔗 Қатысты: {', '.join(term.get('relations', {{}}).get('associative', []))}" if term.get('relations', {{}}).get('associative') else '') +
            "</p>"
            for lecture_terms in terms.values() for term in lecture_terms
        ]) +
        """
        </div>
        </body>
        </html>
        """,
        height=500,
        scrolling=True
    )

if search_query:
    st.session_state['show_map'] = False
    st.header(f"🔎 Іздеу нәтижелері: \"{search_query}\"")
    found_terms = []
    for lecture_name, term_list in terms.items():
        for term in term_list:
            if search_query in term.get('kk', '').lower() or search_query in term.get('ru', '').lower() or search_query in term.get('en', '').lower():
                found_terms.append((lecture_name, term))

    if not found_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")
    else:
        for lecture_name, term in found_terms:
            term_text = f"{term.get('kk', '')} / {term.get('ru', '')} / {term.get('en', '')}"
            st.markdown(f"### 📂 {lecture_name}<br>🖥 {term_text}", unsafe_allow_html=True)
            speak_buttons(term)

            with st.expander("📖 Анықтама / Определение / Definition"):
                if 'definition' in term:
                    st.markdown(f"**KK:** {term['definition'].get('kk', 'Жоқ')}")
                    st.markdown(f"**RU:** {term['definition'].get('ru', 'Нет')}")
                    st.markdown(f"**EN:** {term['definition'].get('en', 'No')}")
                else:
                    st.info("❗ Бұл термин үшін анықтама берілмеген.")

            with st.expander("💬 Мысал / Пример / Example"):
                if 'example' in term:
                    st.markdown(f"**KK:** {term['example'].get('kk', 'Жоқ')}")
                    st.markdown(f"**RU:** {term['example'].get('ru', 'Нет')}")
                    st.markdown(f"**EN:** {term['example'].get('en', 'No')}")
                else:
                    st.info("❗ Бұл термин үшін мысал берілмеген.")

            if term.get("image"):
                st.markdown(
                    f'<a href="{term["image"]}" target="_blank">'
                    f'<img src="{term["image"]}" width="200" style="border-radius:10px;" />'
                    f'</a>',
                    unsafe_allow_html=True
                )

            if term.get("source"):
                st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")

            st.markdown("---")
elif not st.session_state.get('show_map'):
    term_names = sorted([t.get('kk', '') for t in terms[lecture]])
    st.write("### 📋 Терминдер тізімі:")
    for name in term_names:
        if st.button(f"🔹 {name}"):
            st.session_state['selected_term'] = name

    selected_term = st.session_state.get('selected_term')
    if selected_term:
        for term in terms[lecture]:
            if term.get('kk', '') == selected_term:
                term_text = f"{term.get('kk', '')} / {term.get('ru', '')} / {term.get('en', '')}"
                st.markdown(f"### 🖥 {term_text}")
                speak_buttons(term)

                with st.expander("📖 Анықтама / Определение / Definition"):
                    if 'definition' in term:
                        st.markdown(f"**KK:** {term['definition'].get('kk', 'Жоқ')}")
                        st.markdown(f"**RU:** {term['definition'].get('ru', 'Нет')}")
                        st.markdown(f"**EN:** {term['definition'].get('en', 'No')}")
                    else:
                        st.info("❗ Бұл термин үшін анықтама берілмеген.")

                with st.expander("💬 Мысал / Пример / Example"):
                    if 'example' in term:
                        st.markdown(f"**KK:** {term['example'].get('kk', 'Жоқ')}")
                        st.markdown(f"**RU:** {term['example'].get('ru', 'Нет')}")
                        st.markdown(f"**EN:** {term['example'].get('en', 'No')}")
                    else:
                        st.info("❗ Бұл термин үшін мысал берілмеген.")

                if term.get("image"):
                    st.markdown(
                        f'<a href="{term["image"]}" target="_blank">'
                        f'<img src="{term["image"]}" width="200" style="border-radius:10px;" />'
                        f'</a>',
                        unsafe_allow_html=True
                    )

                if term.get("source"):
                    st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")

                st.markdown("---")
