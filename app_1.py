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
@st.cache_data(ttl=60, show_spinner=False)
def load_github_data():
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return json.loads(content), response.json()["sha"]
    except Exception as e:
        st.error(f"❌ Деректер жүктелмеді: {str(e)}")
        return {}, None

def update_github(data):
    """GitHub-та деректерді жаңарту (автоматты SHA алу арқылы)"""
    try:
        # 1. Ағымдағы SHA-ны алу
        current_content = requests.get(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}",
            headers=headers
        ).json()
        sha = current_content.get("sha")

        # 2. Жаңа деректерді жіберу
        response = requests.put(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}",
            headers=headers,
            json={
                "message": "Терминдер жаңартылды",
                "content": base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode(),
                "sha": sha  # Ағымдағы SHA қолдану
            }
        )

        if response.status_code == 200:
            st.success("✅ Терминдер сәтті сақталды!")
            return True
        else:
            st.error(f"❌ GitHub қатесі: {response.json().get('message')}")
            return False

    except Exception as e:
        st.error(f"❌ Сақтау қатесі: {str(e)}")
        return False

def parse_excel(uploaded_file):
    """Excel файлды дұрыс парсинг жасау (жаңартылған нұсқасы)"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Міндетті бағандарды тексеру
        required_columns = ['kk', 'ru', 'en']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"❌ Қажетті бағандар жоқ: {', '.join(missing)}")
            return []

        new_terms = []
        for _, row in df.iterrows():
            # Негізгі ақпарат
            term = {
                'kk': str(row['kk']).strip(),
                'ru': str(row['ru']).strip(),
                'en': str(row['en']).strip(),
                'definition': {
                    'kk': str(row.get('definition_kk', '')).strip(),
                    'ru': str(row.get('definition_ru', '')).strip(),
                    'en': str(row.get('definition_en', '')).strip()
                },
                'example': {
                    'kk': str(row.get('example_kk', '')).strip(),
                    'ru': str(row.get('example_ru', '')).strip(),
                    'en': str(row.get('example_en', '')).strip()
                },
                'relations': {
                    'synonyms': [s.strip() for s in str(row.get('synonyms', '')).split(',') if s.strip()],
                    'general_concept': str(row.get('general_concept', '')).strip(),
                    'specific_concepts': [s.strip() for s in str(row.get('specific_concepts', '')).split(',') if s.strip()],
                    'associative': [s.strip() for s in str(row.get('associative', '')).split(',') if s.strip()]
                }
            }
            
            # Пустық өрістерді өшіру
            for key in ['definition', 'example']:
                term[key] = {k: v for k, v in term[key].items() if v}
            
            new_terms.append(term)
        
        return new_terms

    except Exception as e:
        st.error(f"❌ Excel қатесі: {str(e)}")
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
        uploaded_file = st.file_uploader("📤 Excel файл жүктеу", type=["xlsx"])
        if uploaded_file:
            new_terms = parse_excel(uploaded_file)
            if new_terms:
                st.success(f"✅ {len(new_terms)} жаңа термин табылды!")
                
                # Тақырыпты таңдау
                lecture_options = list(terms_data.keys()) + ["+ ЖАҢА ТАҚЫРЫП"]
                selected_lecture = st.selectbox(
                    "📚 Тақырып таңдаңыз:", 
                    lecture_options,
                    index=0
                )

                if selected_lecture == "+ ЖАҢА ТАҚЫРЫП":
                    new_lecture_name = st.text_input("Жаңа тақырып атауы:")
                    if new_lecture_name:
                        selected_lecture = new_lecture_name
                        terms_data[selected_lecture] = []  
                
                if selected_lecture not in terms_data:
                    terms_data[selected_lecture] = []  # Кілт жоқ болса жасау

                if st.button("💾 Сақтау"):
                     st.cache_data.clear()
                     terms_data, _ = load_github_data()
                     terms_data[selected_lecture].extend(new_terms)
                     if update_github(terms_data):
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
