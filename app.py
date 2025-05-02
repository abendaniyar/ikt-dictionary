import streamlit as st
import json
from streamlit.components.v1 import html
from sentence_transformers import SentenceTransformer, util
import torch

# JSON файлды жүктеу
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

st.set_page_config(page_title="Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘АКТ курсы бойынша электрондық ұғымдық-терминологиялық сөздік")

# NLP моделін жүктеу
@st.cache_resource
def load_similarity_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

model = load_similarity_model()

# Барлық терминдерден қазақша атауларды жинау
all_kk_terms = []
for term_list in terms.values():
    for t in term_list:
        all_kk_terms.append(t['kk'])

# Барлық қазақша терминдерді тексеру үшін жинау (төменгі регистрде)
all_kk_set = set(t.lower() for t in all_kk_terms)

# Семантикалық ұқсас терминдер

def get_similar_terms(query, top_k=3):
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(all_kk_terms, convert_to_tensor=True)
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)[0]
    return [all_kk_terms[hit['corpus_id']] for hit in hits if all_kk_terms[hit['corpus_id']].lower() != query.lower()]

# Іздеу функциясын қосу
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

# Дыбыстау батырмасы

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

# Семантикалық карта батырмасы
show_map = st.sidebar.checkbox("📚 Семантикалық картаны көрсету")

if show_map:
    st.subheader("📚 Семантикалық карта / Semantic Map")
    for lecture_name, term_list in terms.items():
        for term in term_list:
            if 'relations' in term:
                st.markdown(f"🔸 **{term['kk']}** — ", unsafe_allow_html=True)
                rel = term['relations']

                if rel.get('synonyms'):
                    synonyms = ', '.join([f"`{syn}`" for syn in rel['synonyms']])
                    st.markdown(f"  🔁 Синонимдер: {synonyms}")

                if rel.get('general_concept'):
                    st.markdown(f"  🔼 Жалпылама ұғым: `{rel['general_concept']}`")

                if rel.get('specific_concepts'):
                    nar = ', '.join([f"`{n}`" for n in rel['specific_concepts']])
                    st.markdown(f"  🔽 Арнайы ұғымдар: {nar}")

                if rel.get('associative'):
                    rels = ', '.join([f"`{r}`" for r in rel['associative']])
                    st.markdown(f"  🔗 Қатысты: {rels}")

if search_query:
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

            similar_terms = get_similar_terms(term['kk'])
            valid_similar_terms = [t for t in similar_terms if t.lower() in all_kk_set]
            if valid_similar_terms:
                st.markdown("**🔁 Мағыналық жағынан ұқсас терминдер:** " + ", ".join(f"`{t}`" for t in valid_similar_terms))

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
    st.header(lecture)
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

        similar_terms = get_similar_terms(term['kk'])
        valid_similar_terms = [t for t in similar_terms if t.lower() in all_kk_set]
        if valid_similar_terms:
            st.markdown("**🔁 Мағыналық жағынан ұқсас терминдер:** " + ", ".join(f"`{t}`" for t in valid_similar_terms))

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
