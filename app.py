import streamlit as st
import json
import pandas as pd
import requests
import base64
from difflib import get_close_matches
from streamlit.components.v1 import html

# ==================== Конфигурация ====================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_OWNER = st.secrets["REPO_OWNER"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data.json"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ==================== Основные функции ====================
@st.cache_data
def load_github_data():
    """Загрузка данных из GitHub репозитория"""
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return json.loads(content), response.json()["sha"]
    
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {str(e)}")
        return {}, None

def update_github(data, sha):
    """Обновление данных на GitHub"""
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        
        response = requests.put(
            url,
            headers=headers,
            json={
                "message": "🔄 Обновление данных",
                "content": base64.b64encode(content).decode("utf-8"),
                "sha": sha
            }
        )
        response.raise_for_status()
        st.success("✅ Данные успешно обновлены!")
    
    except Exception as e:
        st.error(f"❌ Ошибка обновления: {str(e)}")

def parse_excel(uploaded_file):
    """Обработка Excel-файла с терминами"""
    try:
        df = pd.read_excel(uploaded_file)
        return [
            {
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
                    'synonyms': [s.strip() for s in str(row.get('synonyms', '')).split(',')],
                    'general': row.get('general_concept', ''),
                    'specific': [s.strip() for s in str(row.get('specific_concepts', '')).split(',')],
                    'associative': [s.strip() for s in str(row.get('associative', '')).split(',')]
                }
            }
            for _, row in df.iterrows()
        ]
    
    except Exception as e:
        st.error(f"❌ Ошибка обработки Excel: {str(e)}")
        return []

# ==================== Вспомогательные функции ====================
def display_term(term):
    """Отображение карточки термина"""
    with st.container():
        st.markdown(f"### 🌐 {term.get('kk', '')}")
        
        # Вкладки с информацией
        tabs = st.tabs(["📖 Определение", "💬 Пример", "🔗 Связи"])
        
        with tabs[0]:
            st.markdown(f"**KK:** {term['definition'].get('kk', '-')}")
            st.markdown(f"**RU:** {term['definition'].get('ru', '-')}")
            st.markdown(f"**EN:** {term['definition'].get('en', '-')}")
        
        with tabs[1]:
            st.markdown(f"**KK:** {term['example'].get('kk', '-')}")
            st.markdown(f"**RU:** {term['example'].get('ru', '-')}")
            st.markdown(f"**EN:** {term['example'].get('en', '-')}")
        
        with tabs[2]:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("🔁 **Синонимы:**\n" + "\n".join(f"- {s}" for s in term['relations']['synonyms']))
                st.markdown("🔼 **Общее понятие:**\n" + term['relations']['general'])
            with cols[1]:
                st.markdown("🔽 **Частные понятия:**\n" + "\n".join(f"- {s}" for s in term['relations']['specific']))
                st.markdown("🔗 **Ассоциации:**\n" + "\n".join(f"- {s}" for s in term['relations']['associative']))

# ==================== Интерфейс ====================
def main():
    st.set_page_config("Электронный словарь", layout="wide")
    st.title("📚 Терминологический словарь АКТ")
    
    # Инициализация данных
    terms_data, sha = load_github_data()
    all_terms = [term for lecture in terms_data.values() for term in lecture]
    
    # ==================== Боковая панель ====================
    with st.sidebar:
        st.header("⚙️ Управление данными")
        
        # Загрузка Excel
        uploaded_file = st.file_uploader("📤 Загрузить Excel", type=["xlsx"])
        if uploaded_file:
            new_terms = parse_excel(uploaded_file)
            if new_terms:
                selected_lecture = st.selectbox("📚 Выберите лекцию", list(terms_data.keys()))
                if st.button("💾 Сохранить термины"):
                    terms_data[selected_lecture].extend(new_terms)
                    update_github(terms_data, sha)
                    st.rerun()
        
        # Семантическая карта
        if st.button("🌍 Показать связи"):
            html_content = "<div style='padding:20px; font-family:Arial;'>"
            html_content += "<h3>🔗 Семантические связи</h3>"
            for term in all_terms:
                html_content += f"<p><b>{term['kk']}</b> → {', '.join(term['relations']['synonyms'] + term['relations']['specific'])}</p>"
            html_content += "</div>"
            html(html_content, height=500, scrolling=True)
    
    # ==================== Основной интерфейс ====================
    # Поиск и фильтрация
    search_query = st.text_input("🔍 Поиск по всем терминам", help="Ищите на любом языке")
    filtered_terms = [
        term for term in all_terms
        if search_query.lower() in str(term).lower()
    ] if search_query else all_terms
    
    # Отображение результатов
    if filtered_terms:
        st.subheader(f"📚 Найдено терминов: {len(filtered_terms)}")
        for term in filtered_terms:
            display_term(term)
            st.divider()
    else:
        st.info("🔍 Ничего не найдено. Попробуйте другой запрос.")

if __name__ == "__main__":
    main()
