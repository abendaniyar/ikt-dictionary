import streamlit as st
import json
import pandas as pd
import base64
import requests
from streamlit.components.v1 import html

# GitHub баптаулары
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_OWNER = st.secrets["REPO_OWNER"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data.json"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

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
            st.session_state['selected_term'] = None
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Excel оқу қатесі: {e}")
# Іздеу функциясын қосу
# --- ІЗДЕУ ЖӘНЕ СҮЗГІ ---
all_terms = []
for lecture, tlist in terms.items():
    for term in tlist:
        all_terms.append(term)

# 1. Автоаяқтау (autocomplete) және көптілді іздеу
all_titles = list({t.get("kk", "") for t in all_terms} | {t.get("ru", "") for t in all_terms} | {t.get("en", "") for t in all_terms})
search_query = st.text_input("🔍 Термин іздеу (kk, ru, en):", value="", placeholder="мыс. алгоритм, network, база", help="Кез келген тілде іздеңіз")

# 2. Алфавиттік сүзгі
alphabet = sorted(set(term.get("kk", "")[:1].upper() for term in all_terms if term.get("kk", "")))
selected_letter = st.selectbox("🔡 Әріп бойынша сүзгі (kk):", ["Барлығы"] + alphabet)

filtered_terms = []
for term in all_terms:
    name_kk = term.get("kk", "").lower()
    name_ru = term.get("ru", "").lower()
    name_en = term.get("en", "").lower()

    if search_query.lower() in name_kk or search_query.lower() in name_ru or search_query.lower() in name_en:
        if selected_letter == "Барлығы" or name_kk.startswith(selected_letter.lower()):
            filtered_terms.append(term)
    elif not search_query and (selected_letter == "Барлығы" or name_kk.startswith(selected_letter.lower())):
        filtered_terms.append(term)

# 3. Ұсыныстар (recommendations)
if search_query and not filtered_terms:
    from difflib import get_close_matches
    suggestions = get_close_matches(search_query, all_titles, n=5)
    if suggestions:
        st.warning("🛑 Нақты термин табылмады. Мүмкін сіз мынаны іздедіңіз:")
        for s in suggestions:
            st.write(f"👉 {s}")
    else:
        st.info("❗ Ұқсас терминдер табылмады.")

# 4. Терминдерді визуализациялау
if filtered_terms:
    st.write(f"### 📋 Нәтижелер: {len(filtered_terms)} термин")
    for term in filtered_terms:
        term_text = f"{term.get('kk', '')} / {term.get('ru', '')} / {term.get('en', '')}"
        st.markdown(f"### 🖥 {term_text}")
        
        with st.expander("📖 Анықтама / Definition"):
            st.markdown(f"**KK:** {term.get('definition', {}).get('kk', '')}")
            st.markdown(f"**RU:** {term.get('definition', {}).get('ru', '')}")
            st.markdown(f"**EN:** {term.get('definition', {}).get('en', '')}")

        with st.expander("💬 Мысал / Example"):
            st.markdown(f"**KK:** {term.get('example', {}).get('kk', '')}")
            st.markdown(f"**RU:** {term.get('example', {}).get('ru', '')}")
            st.markdown(f"**EN:** {term.get('example', {}).get('en', '')}")

        relations = term.get("relations", {})
        if relations:
            with st.expander("🔗 Байланыстар"):
                st.write(f"🔁 Синонимдер: {', '.join(relations.get('synonyms', []))}")
                st.write(f"🔼 Жалпылама: {relations.get('general_concept', '')}")
                st.write(f"🔽 Арнайы: {', '.join(relations.get('specific_concepts', []))}")
                st.write(f"🔗 Қатысты: {', '.join(relations.get('associative', []))}")
        st.markdown("---")
else:
    st.info("📝 Термин таңдаңыз немесе сүзгі қолданыңыз.")

# Дәріс таңдауы
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
