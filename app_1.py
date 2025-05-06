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
                    'general': [s.strip() for s in str(row.get('general_concept', '')).split(',')],
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
def display_term_compact(term):
    """Отображение термина в компактном режиме (только название)"""
    kk_title = term.get('kk', 'Без названия')
    if st.button(f"🔹 {kk_title}", key=f"compact_{kk_title}"):
        st.session_state.selected_term = term

def display_term_full(term):
    """Отображение полной информации о термине"""
    with st.expander(f"📘 {term.get('kk', 'Без названия')}", expanded=True):
        tabs = st.tabs(["📖 Определение", "💬 Пример", "🔗 Связи"])
        
        definition = term.get('definition', {})
        example = term.get('example', {})
        relations = term.get('relations', {})

        with tabs[0]:
            st.markdown(f"**KK:** {definition.get('kk', '-')}")
            st.markdown(f"**RU:** {definition.get('ru', '-')}")
            st.markdown(f"**EN:** {definition.get('en', '-')}")
        
        with tabs[1]:
            st.markdown(f"**KK:** {example.get('kk', '-')}")
            st.markdown(f"**RU:** {example.get('ru', '-')}")
            st.markdown(f"**EN:** {example.get('en', '-')}")
        
        with tabs[2]:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("🔁 **Синонимы:**\n" + "\n".join(
                    f"- {s}" for s in relations.get('synonyms', [])
                ))
                st.markdown("🔼 **Общее понятие:**\n" + relations.get('general', '-'))
            with cols[1]:
                st.markdown("🔽 **Частные понятия:**\n" + "\n".join(
                    f"- {s}" for s in relations.get('specific', [])
                ))
                st.markdown("🔗 **Ассоциации:**\n" + "\n".join(
                    f"- {s}" for s in relations.get('associative', [])
                ))
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
            
            for lecture in terms_data.values():
                for term in lecture:
                    try:
                        kk = term.get('kk', 'Без названия')
                        relations = term.get('relations', {})
                        elements = []
                        if 'synonyms' in relations:
                            elements.extend(relations['synonyms'])
                        if 'specific' in relations:
                            elements.extend(relations['specific'])
                        html_content += f"<p><b>{kk}</b> → {', '.join(elements)}</p>"
                    except Exception as e:
                        continue
            
            html_content += "</div>"
            html(html_content, height=500, scrolling=True)

    # ==================== Основной интерфейс ====================
    # Переключатель режимов
    view_mode = st.radio("🔍 Режим просмотра:", 
                        ["📂 По темам", "🔎 Поиск по всем терминам"], 
                        horizontal=True)

    if view_mode == "📂 По темам":
        selected_lecture = st.selectbox(
            "📚 Выберите тему:",
            list(terms_data.keys()),
            index=0,
            key="lecture_selector"
        )

        st.subheader(f"📖 Тема: {selected_lecture}")
        st.write(f"🔢 Количество терминов 1: {len(terms_data[selected_lecture])}")
        
        # Инициализация состояния выбранного термина
        if 'selected_term' not in st.session_state:
            st.session_state.selected_term = None
            
        # Отображение списка терминов
        for term in terms_data[selected_lecture]:
            display_term_compact(term)
        
        # Отображение выбранного термина
        if st.session_state.selected_term:
            display_term_full(st.session_state.selected_term)
            if st.button("❌ Закрыть"):
                st.session_state.selected_term = None
                st.rerun()

    else:
        # Поиск по всем терминам
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
