import streamlit as st
import json
import pandas as pd
import base64
import requests
from streamlit.components.v1 import html
import streamlit.components.v1 as components

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_OWNER = st.secrets["REPO_OWNER"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data.json"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# JSON файлды GitHub-тан жүктеу
@st.cache_data
def load_json_from_github():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"]).decode("utf-8")
        sha = res.json()["sha"]
        return json.loads(content), sha
    else:
        st.error(f"❌ GitHub-тан дерек жүктелмеді: {res.status_code}")
        return {}, None

# GitHub-қа жаңа JSON жазу
def update_json_to_github(new_data, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    updated_content = json.dumps(new_data, ensure_ascii=False, indent=2).encode("utf-8")
    b64_content = base64.b64encode(updated_content).decode("utf-8")

    data = {
        "message": "🔄 Терминдер жаңартылды",
        "content": b64_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        st.success("✅ Терминдер GitHub-та жаңартылды!")
    else:
        st.error(f"❌ GitHub-қа жазу қатесі: {response.text}")

# Интерфейс
st.set_page_config("Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘 АКТ курсы: Электрондық терминологиялық сөздік")

terms, sha = load_json_from_github()

# Excel жүктеу
uploaded_file = st.sidebar.file_uploader("📤 Excel файл жүктеу (xlsx)", type=["xlsx"])
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
            st.session_state['selected_term'] = None  # жаңадан бастау
            st.experimental_rerun()
            except Exception as e:
        st.error(f"❌ Excel оқу қатесі: {e}")

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

# Термин тізімі
if not search_query:
    st.write("### 📋 Терминдер тізімі:")

    page_size = 10
    total_terms = len(terms[lecture])
    total_pages = (total_terms + page_size - 1) // page_size

    page = st.number_input("📄 Бет таңдау", min_value=1, max_value=total_pages, step=1)

    start = (page - 1) * page_size
    end = start + page_size
    paginated_terms = terms[lecture][start:end]

    for i, term in enumerate(paginated_terms):
        name = term.get("kk", "")
        if st.button(f"🔹 {name}", key=f"term_{start + i}"):
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
