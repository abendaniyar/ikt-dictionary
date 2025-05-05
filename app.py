import streamlit as st
import json
import pandas as pd
import base64
import requests
from difflib import get_close_matches
from streamlit.components.v1 import html

# GitHub API настройки
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
    """Загрузка JSON данных из GitHub репозитория"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        sha = response.json()["sha"]
        return json.loads(content), sha
    else:
        st.error(f"❌ Ошибка загрузки данных: {response.status_code}")
        return {}, None

def update_json_to_github(new_data, sha):
    """Обновление JSON данных на GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    updated_content = json.dumps(new_data, ensure_ascii=False, indent=2).encode("utf-8")
    b64_content = base64.b64encode(updated_content).decode("utf-8")

    data = {
        "message": "🔄 Обновление терминологии",
        "content": b64_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in (200, 201):
        st.success("✅ Данные успешно обновлены!")
    else:
        st.error(f"❌ Ошибка обновления: {response.text}")

def display_term_info(term):
    """Отображение информации о термине"""
    term_text = f"{term.get('kk', '')} / {term.get('ru', '')} / {term.get('en', '')}"
    st.markdown(f"### 🖥 {term_text}")
    
    with st.expander("📖 Определения"):
        st.markdown(f"**KK:** {term.get('definition', {}).get('kk', '')}")
        st.markdown(f"**RU:** {term.get('definition', {}).get('ru', '')}")
        st.markdown(f"**EN:** {term.get('definition', {}).get('en', '')}")
    
    with st.expander("💬 Примеры"):
        st.markdown(f"**KK:** {term.get('example', {}).get('kk', '')}")
        st.markdown(f"**RU:** {term.get('example', {}).get('ru', '')}")
        st.markdown(f"**EN:** {term.get('example', {}).get('en', '')}")
    
    if relations := term.get("relations"):
        with st.expander("🔗 Связи"):
            st.write(f"🔁 Синонимы: {', '.join(relations.get('synonyms', []))}")
            st.write(f"🔼 Общее понятие: {relations.get('general_concept', '')}")
            st.write(f"🔽 Частные понятия: {', '.join(relations.get('specific_concepts', []))}")
            st.write(f"🔗 Ассоциации: {', '.join(relations.get('associative', []))}")

# Инициализация приложения
st.set_page_config("Электронный терминологический словарь", layout="wide")
st.title("📘 Электронный терминологический словарь")

# Загрузка данных
terms, sha = load_json_from_github()

# Боковая панель
with st.sidebar:
    # Загрузка Excel файла
    uploaded_file = st.file_uploader("📤 Загрузить Excel", type=["xlsx"])
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
                        'synonyms': row.get('relations_synonyms', '').split(',') if row.get('relations_synonyms') else [],
                        'general_concept': row.get('relations_general_concept', ''),
                        'specific_concepts': row.get('relations_specific_concepts', '').split(',') if row.get('relations_specific_concepts') else [],
                        'associative': row.get('relations_associative', '').split(',') if row.get('relations_associative') else []
                    }
                }
                new_terms.append(term)
            
            lecture = st.selectbox("📚 Выберите лекцию", list(terms.keys()))
            if st.button("➕ Добавить термины"):
                terms[lecture].extend(new_terms)
                update_json_to_github(terms, sha)
                st.experimental_rerun()
        
        except Exception as e:
            st.error(f"❌ Ошибка обработки файла: {e}")

    # Семантическая карта
    if st.button("📚 Показать семантическую карту"):
        html_content = """
        <html><body style='font-family:Arial; padding:20px;'>
            <h2>📚 Семантическая карта</h2>
            """ + "".join(
            f"<p><b>{term.get('kk', '')}</b> - " + 
            ", ".join(filter(None, [
                f"🔁 {', '.join(term.get('relations', {}).get('synonyms', []))}" if term.get('relations', {}).get('synonyms') else None,
                f"🔼 {term.get('relations', {}).get('general_concept', '')}" if term.get('relations', {}).get('general_concept') else None,
                f"🔽 {', '.join(term.get('relations', {}).get('specific_concepts', []))}" if term.get('relations', {}).get('specific_concepts') else None,
                f"🔗 {', '.join(term.get('relations', {}).get('associative', []))}" if term.get('relations', {}).get('associative') else None
            ])) + "</p>"
            for lecture_terms in terms.values() for term in lecture_terms
        ) + "</body></html>"
        
        html(html_content, height=500, scrolling=True)

# Основной интерфейс
# Поиск и фильтрация
all_terms = [term for lecture_terms in terms.values() for term in lecture_terms]
search_query = st.text_input("🔍 Поиск термина:", placeholder="Введите запрос...")

# Фильтрация результатов
filtered_terms = [
    term for term in all_terms
    if search_query.lower() in term.get('kk', '').lower() or 
       search_query.lower() in term.get('ru', '').lower() or 
       search_query.lower() in term.get('en', '').lower()
]

# Отображение результатов
if filtered_terms:
    st.subheader(f"📋 Результаты поиска ({len(filtered_terms})")
    for term in filtered_terms:
        display_term_info(term)
        st.markdown("---")
else:
    st.info("🔍 Термины не найдены. Попробуйте изменить запрос.")

# Отображение терминов по лекциям
lecture = st.sidebar.radio("📂 Выберите лекцию:", list(terms.keys()))
st.subheader(f"📚 Термины лекции: {lecture}")

for term in terms[lecture]:
    if st.button(f"🔹 {term.get('kk', '')}", key=f"term_{term.get('kk', '')}"):
        display_term_info(term)
        st.markdown("---")
