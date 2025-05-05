import streamlit as st
import json
import pandas as pd
import requests
import base64
import logging
from difflib import get_close_matches
from streamlit.components.v1 import html

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== КОНФИГУРАЦИЯ ====================
REQUIRED_SECRETS = ["GITHUB_TOKEN", "REPO_OWNER", "REPO_NAME"]
REQUIRED_TERM_KEYS = ['kk', 'ru', 'en']

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def validate_secrets():
    """Проверка наличия необходимых секретов"""
    missing = [key for key in REQUIRED_SECRETS if key not in st.secrets]
    if missing:
        st.error(f"❌ Отсутствуют секреты: {', '.join(missing)}")
        raise RuntimeError("Missing secrets")

def load_github_data():
    """Загрузка данных из GitHub"""
    try:
        url = f"https://api.github.com/repos/{st.secrets.REPO_OWNER}/{st.secrets.REPO_NAME}/contents/data.json"
        response = requests.get(
            url,
            headers={"Authorization": f"token {st.secrets.GITHUB_TOKEN}"}
        )
        response.raise_for_status()
        
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return json.loads(content), response.json()["sha"]
    
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {str(e)}")
        st.error("❌ Ошибка загрузки данных из GitHub")
        return {}, None

def validate_term(term):
    """Проверка структуры термина"""
    return all(key in term for key in REQUIRED_TERM_KEYS)

def safe_get(data, *keys, default=None):
    """Безопасное получение данных из словаря"""
    for key in keys:
        data = data.get(key, {}) if isinstance(data, dict) else default
    return data if data is not None else default

# ==================== ОСНОВНЫЕ КОМПОНЕНТЫ ====================
def display_term(term):
    """Отображение карточки термина"""
    try:
        with st.container():
            # Заголовок
            title = safe_get(term, 'kk', default='Без названия')
            st.markdown(f"### 🌐 {title}")
            
            # Вкладки с информацией
            tabs = st.tabs(["📖 Определение", "💬 Пример", "🔗 Связи"])
            
            # Определения
            with tabs[0]:
                st.markdown(f"**KK:** {safe_get(term, 'definition', 'kk', default='-')}")
                st.markdown(f"**RU:** {safe_get(term, 'definition', 'ru', default='-')}")
                st.markdown(f"**EN:** {safe_get(term, 'definition', 'en', default='-')}")
            
            # Примеры
            with tabs[1]:
                st.markdown(f"**KK:** {safe_get(term, 'example', 'kk', default='-')}")
                st.markdown(f"**RU:** {safe_get(term, 'example', 'ru', default='-')}")
                st.markdown(f"**EN:** {safe_get(term, 'example', 'en', default='-')}")
            
            # Связи
            with tabs[2]:
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("🔁 **Синонимы:**\n" + "\n".join(
                        f"- {s}" for s in safe_get(term, 'relations', 'synonyms', default=[])
                    ))
                    st.markdown("🔼 **Общее понятие:**\n" + safe_get(term, 'relations', 'general', default='-'))
                
                with cols[1]:
                    st.markdown("🔽 **Частные понятия:**\n" + "\n".join(
                        f"- {s}" for s in safe_get(term, 'relations', 'specific', default=[])
                    ))
                    st.markdown("🔗 **Ассоциации:**\n" + "\n".join(
                        f"- {s}" for s in safe_get(term, 'relations', 'associative', default=[])
                    ))
    
    except Exception as e:
        logger.error(f"Ошибка отображения термина: {str(e)}")
        st.error("⚠️ Ошибка отображения термина")

def show_semantic_map(terms_data):
    """Генерация семантической карты"""
    html_content = "<div style='padding:20px; font-family:Arial;'><h3>🔗 Семантические связи</h3>"
    
    for lecture in terms_data.values():
        for term in lecture:
            try:
                title = safe_get(term, 'kk', default='Без названия')
                synonyms = safe_get(term, 'relations', 'synonyms', default=[])
                specific = safe_get(term, 'relations', 'specific', default=[])
                relations = ', '.join(synonyms + specific)
                
                html_content += f"<p><b>{title}</b> → {relations or 'нет связей'}</p>"
            
            except Exception as e:
                logger.error(f"Ошибка обработки термина: {str(e)}")
                continue
    
    html_content += "</div>"
    html(html_content, height=500, scrolling=True)

# ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
def main():
    st.set_page_config("Электронный словарь", layout="wide")
    st.title("📚 Терминологический словарь АКТ")
    
    try:
        # Загрузка данных
        terms_data, _ = load_github_data()
        
        # Фильтрация терминов
        valid_terms = [
            term for lecture in terms_data.values() 
            for term in lecture 
            if validate_term(term)
        ]
        
        # Поиск
        search_query = st.text_input("🔍 Поиск по всем терминам", help="Ищите на любом языке")
        filtered_terms = [
            term for term in valid_terms
            if search_query.lower() in str(term).lower()
        ] if search_query else valid_terms
        
        # Отображение результатов
        if filtered_terms:
            st.subheader(f"📚 Найдено терминов: {len(filtered_terms)}")
            for term in filtered_terms:
                display_term(term)
                st.divider()
        else:
            st.info("🔍 Ничего не найдено. Попробуйте другой запрос.")
        
        # Боковая панель
        with st.sidebar:
            st.header("⚙️ Управление")
            if st.button("🌍 Показать связи"):
                show_semantic_map(terms_data)
    
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        st.error("🚨 Произошла критическая ошибка. Пожалуйста, проверьте логи.")

if __name__ == "__main__":
    try:
        validate_secrets()
        main()
    except Exception as e:
        st.error("❌ Приложение не может быть запущено")
