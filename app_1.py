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
def display_term_compact(term, index):
    """Терминнің қысқаша көрінісі"""
    kk_title = term.get('kk', 'Атауы жоқ')
    unique_key = f"compact_{index}_{kk_title[:10]}"  # Индекс пен атаудан кілт
    if st.button(f"🔹 {kk_title}", key=unique_key):
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
    st.set_page_config("Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
    st.title("📘 АКТ курсы: Электрондық ұғымдық-терминологиялық сөздік")
    
    # Инициализация данных
    terms_data, sha = load_github_data()
    
    # Проверка загруженных данных
    if not terms_data or not isinstance(terms_data, dict):
        st.error("❌ Деректер жүктелмеді немесе қате формат")
        return
    
    all_terms = [term for lecture in terms_data.values() for term in lecture]
    
    # ==================== Боковая панель ====================
    with st.sidebar:
        st.header("⚙️ Деректерді басқару")
        
        # Загрузка Excel
        uploaded_file = st.file_uploader("📤 Excel файл жүктеу", type=["xlsx"])
        if uploaded_file:
            new_terms = parse_excel(uploaded_file)
            if new_terms:
                selected_lecture = st.selectbox("📚 Дәріс таңдаңыз", list(terms_data.keys()))
                if st.button("💾 Терминдерді сақтау"):
                    terms_data[selected_lecture].extend(new_terms)
                    update_github(terms_data, sha)
                    st.rerun()
        
        # Семантикалық карта
        if st.button("🌍 Байланыстарды көрсету"):
            html_content = "<div style='padding:20px; font-family:Arial;'>"
            html_content += "<h3>🔗 Семантикалық байланыстар</h3>"
            
            for lecture in terms_data.values():
                for term in lecture:
                    try:
                        kk = term.get('kk', 'Атауы жоқ')
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

    # ==================== Негізгі интерфейс ====================
    view_mode = st.radio("🔍 Көріну режимі:", 
                        ["📂 Тақырып бойынша", "🔎 Барлық терминдерден іздеу"], 
                        horizontal=True)

    if view_mode == "📂 Тақырып бойынша":
        # Тақырыпты таңдау
        selected_lecture = st.selectbox(
            "📚 Тақырыпты таңдаңыз:",
            list(terms_data.keys()),
            index=0,
            key="lecture_selector"
        )
    
        # Фильтрлер
        st.subheader(f"📖 Тақырып: {selected_lecture}")
        
        # 1. Әріп бойынша сүзгі
        initial_terms = terms_data[selected_lecture]
        letters = sorted({term['kk'][0].upper() for term in initial_terms if term.get('kk')})
        selected_letter = st.selectbox("🔤 Әріп бойынша сүзгі", ["Барлығы"] + letters)
        
        # Фильтрация
        filtered_terms = [
            term for term in initial_terms
            if selected_letter == "Барлығы" or term.get('kk', '').upper().startswith(selected_letter)
        ]
    
        # 2. Сұрыптау параметрлері
        col1, col2 = st.columns([3, 2])
        with col1:
            sort_option = st.selectbox(
                "🔃 Сұрыптау түрі",
                options=[
                    "Алфавит бойынша (А-Я)",
                    "Алфавит бойынша (Я-А)",
                    "Мысалдары барлар алдымен"
                ],
                index=0
            )
        
        # Сұрыптау логикасы
        if sort_option == "Алфавит бойынша (А-Я)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''))
        elif sort_option == "Алфавит бойынша (Я-А)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''), reverse=True)
        elif sort_option == "Мысалдары барлар алдымен":
            filtered_terms.sort(key=lambda x: len(x.get('example', {}).get('kk', '')), reverse=True)
    
        # Терминдерді көрсету
        st.write(f"🔢 Жалпы терминдер: {len(filtered_terms)}")
        
        for idx, term in enumerate(filtered_terms):
            display_term_compact(term, idx)
       # Толық ақпаратты көрсету
        if st.session_state.get('selected_term'):
            display_term_full(st.session_state.selected_term)
            if st.button("❌ Жабу"):
                del st.session_state.selected_term
                st.rerun()
    else:
        # Барлық терминдерден іздеу
        search_query = st.text_input("🔍 Терминдерді іздеу", help="Кез келген тілде іздеңіз")
        filtered_terms = [
            term for term in all_terms
            if search_query.lower() in str(term).lower()
        ] if search_query else all_terms
        
        if filtered_terms:
            st.subheader(f"📚 Табылды: {len(filtered_terms)} термин")
            for idx, term in enumerate(filtered_terms):  # <-- enumerate қосылды
                display_term_compact(term, idx)  # <-- индекс берілді
                #st.divider()
        else:
            st.info("🔍 Ештеңе табылған жоқ. Іздеу сұранысын өзгертіңіз.")
if __name__ == "__main__":
    main()
