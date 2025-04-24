import streamlit as st
import json
from streamlit.components.v1 import html

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
            <button onclick=\"speakKK()\" style='margin-right: 10px;'>🔊 Қазақша</button>
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

if search_query:
    st.header(f"🔎 Іздеу нәтижелері: \"{search_query}\"")

    found_terms = []
    for lecture, term_list in terms.items():
        for term in term_list:
            if search_query in term['kk'].lower() or search_query in term['ru'].lower() or search_query in term['en'].lower():
                found_terms.append((lecture, term))

    if not found_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")
    else:
        for lecture, term in found_terms:
            term_text = f"{term['kk']} / {term['ru']} / {term['en']}"
            st.markdown(f"### 📂 {lecture}<br>🖥 {term_text}", unsafe_allow_html=True)
            speak_buttons(term)

            with st.expander("📖 Анықтама / Определение / Definition"):
                st.markdown(f"**KK:** {term['definition']['kk']}")
                st.markdown(f"**RU:** {term['definition']['ru']}")
                st.markdown(f"**EN:** {term['definition']['en']}")

            with st.expander("💬 Мысал / Пример / Example"):
                st.markdown(f"**KK:** {term['example']['kk']}")
                st.markdown(f"**RU:** {term['example']['ru']}")
                st.markdown(f"**EN:** {term['example']['en']}")

            if 'relations' in term:
                with st.expander("🧠 Семантикалық байланыстар / Семантические связи / Semantic Relations"):
                    rel = term['relations']
                    if rel.get('synonyms'):
                        st.markdown(f"**🔁 Синонимдер / Синонимы / Synonyms:** {', '.join(rel['synonyms'])}")
                    if rel.get('antonyms'):
                        st.markdown(f"**🆚 Антонимдер / Антонимы / Antonyms:** {', '.join(rel['antonyms'])}")
                    if rel.get('broader_term'):
                        st.markdown(f"**🔼 Жалпылама ұғым / Обобщающее понятие / Broader term:** {rel['broader_term']}")
                    if rel.get('narrower_terms'):
                        st.markdown(f"**🔽 Арнайы ұғымдар / Специальные понятия / Narrower terms:** {', '.join(rel['narrower_terms'])}")
                    if rel.get('related_terms'):
                        st.markdown(f"**🔗 Қатысты ұғымдар / В родственном понятии / Related terms:** {', '.join(rel['related_terms'])}")

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
else:
    lecture = st.sidebar.radio("📂 Дәріс таңдаңыз:", list(terms.keys()))
    st.header(lecture)

    if lecture in terms:
        for term in terms[lecture]:
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
