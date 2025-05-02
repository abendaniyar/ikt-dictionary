import streamlit as st
import json
from streamlit.components.v1 import html
import streamlit.components.v1 as components

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

# Іздеу функциясын қосу
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

def speak_buttons(term):
    kk = term['kk']
    ru = term['ru']
    en = term['en']
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
            f"<p><b>{term['kk']}</b> - " +
            (f"🔁 Синонимдер: {', '.join(term['relations'].get('synonyms', []))} | " if 'relations' in term and term['relations'].get('synonyms') else '') +
            (f"🔼 Жалпылама: {term['relations'].get('general_concept')} | " if 'relations' in term and term['relations'].get('general_concept') else '') +
            (f"🔽 Арнайы: {', '.join(term['relations'].get('specific_concepts', []))} | " if 'relations' in term and term['relations'].get('specific_concepts') else '') +
            (f"🔗 Қатысты: {', '.join(term['relations'].get('associative', []))}" if 'relations' in term and term['relations'].get('associative') else '') +
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
            if search_query in term['kk'].lower() or search_query in term['ru'].lower() or search_query in term['en'].lower():
                found_terms.append((lecture_name, term))

    if not found_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")
    else:
        for lecture_name, term in found_terms:
            term_text = f"{term['kk']} / {term['ru']} / {term['en']}"
            st.markdown(f"### 📂 {lecture_name}<br>🖥 {term_text}", unsafe_allow_html=True)
            speak_buttons(term)

            with st.expander("📖 Анықтама / Определение / Definition"):
                st.markdown(f"**KK:** {term['definition']['kk']}")
                st.markdown(f"**RU:** {term['definition']['ru']}")
                st.markdown(f"**EN:** {term['definition']['en']}")

            with st.expander("💬 Мысал / Пример / Example"):
                st.markdown(f"**KK:** {term['example']['kk']}")
                st.markdown(f"**RU:** {term['example']['ru']}")
                st.markdown(f"**EN:** {term['example']['en']}")

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
    term_names = sorted([t['kk'] for t in terms[lecture]])
    st.write("### 📋 Терминдер тізімі:")
    for name in term_names:
        if st.button(f"🔹 {name}"):
            st.session_state['selected_term'] = name

    selected_term = st.session_state.get('selected_term')
    if selected_term:
        for term in terms[lecture]:
            if term['kk'] == selected_term:
                term_text = f"{term['kk']} / {term['ru']} / {term['en']}"
                st.markdown(f"### 🖥 {term_text}")
                speak_buttons(term)

                with st.expander("📖 Анықтама / Определение / Definition"):
                    st.markdown(f"**KK:** {term['definition']['kk']}")
                    st.markdown(f"**RU:** {term['definition']['ru']}")
                    st.markdown(f"**EN:** {term['definition']['en']}")

                with st.expander("💬 Мысал / Пример / Example"):
                    st.markdown(f"**KK:** {term['example']['kk']}")
                    st.markdown(f"**RU:** {term['example']['ru']}")
                    st.markdown(f"**EN:** {term['example']['en']}")

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
