import streamlit as st
import json
from pathlib import Path
from difflib import get_close_matches
from streamlit.components.v1 import html

# ==================== Конфигурация ====================
ITEMS_PER_PAGE = 30
COLUMN_ITEMS = 10
KAZ_ALPHABET = [
    'Ә', 'І', 'Ң', 'Ғ', 'Ү', 'Ұ', 'Қ', 'Ө', 'Һ',
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З',
    'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П',
    'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч',
    'Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я'
]
# ==================== Основные функции ====================
@st.cache_data(show_spinner=False)
def load_github_data():
    try:
        path = Path(__file__).resolve().with_name("data.json")
        with path.open(encoding="utf-8") as file:
            return json.load(file), None
    except (OSError, ValueError) as e:
        st.error(f"❌ Деректер жүктелмеді: {e}")
        return {}, None

# ==================== Вспомогательные функции ====================
def display_term_compact(term, index):
    kk_title = term.get('kk', 'Атауы жоқ')
    unique_key = f"compact_{index}_{kk_title[:10]}"
    if st.button(f"🔹 {kk_title}", key=unique_key):
        st.session_state.selected_term = term

def display_terms_in_columns(terms, start_idx):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        for idx_in_page, term in enumerate(terms[:COLUMN_ITEMS]):
            global_index = start_idx + idx_in_page
            display_term_compact(term, global_index)
    
    with col2:
        for idx_in_page, term in enumerate(terms[COLUMN_ITEMS:COLUMN_ITEMS*2], start=COLUMN_ITEMS):
            global_index = start_idx + idx_in_page
            display_term_compact(term, global_index)
    
    with col3:
        for idx_in_page, term in enumerate(terms[COLUMN_ITEMS*2:], start=COLUMN_ITEMS*2):
            global_index = start_idx + idx_in_page
            display_term_compact(term, global_index)

def display_term_full(term):
    FLAGS = {
        'kk': 'https://img.icons8.com/?size=100&id=bTwapbmoLtc6&format=png&color=000000',    # Қазақстан
        'ru': 'https://img.icons8.com/?size=100&id=hT4UdesmXlvG&format=png&color=000000',    # Ресей
        'en': 'https://img.icons8.com/?size=100&id=Halaubi1vvya&format=png&color=000000'     # АҚШ
    }
    term_html = []
    for lang, url in FLAGS.items():
        if term.get(lang):
            term_html.append(
                f'<span style="vertical-align: middle;">'
                f'<img src="{url}" style="height: 18px; margin-right: 5px;">'
                f'{term[lang]}'
                f'</span>'
            )
    term_text = '  |  '.join(term_html) or 'Термин атауы жоқ'        
    with st.expander(f"📘 Термин ақпараты", expanded=True):
        st.markdown(f"""
        <div style="font-size: 1.5rem; margin-bottom: 15px;">
            {term_text}
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(5)
        #with cols[0]:
        #    if term.get('kk'):
        #        if st.button("🔊 Қазақша", key=f"sound_kk_{term['kk']}"):
        #            text_to_speech(term['kk'], 'kk')
        with cols[1]:
            if term.get('ru'):
                if st.button("🔊 Русский", key=f"sound_ru_{term['ru']}"):
                    text_to_speech(term['ru'], 'ru')
        with cols[2]:
            if term.get('en'):
                if st.button("🔊 English", key=f"sound_en_{term['en']}"):
                    text_to_speech(term['en'], 'en')
        
        # Основная информация
        tabs = st.tabs(["📖 Анықтама", "💬 Мысал", "🔗 Байланыстар"])
        definition = term.get('definition', {})
        example = term.get('example', {})
        relations = term.get('relations', {})

        with tabs[0]:
            st.markdown(f"**KK:** {definition.get('kk', '-')}")
            st.markdown(f"**RU:** {definition.get('ru', '-')}")
            st.markdown(f"**EN:** {definition.get('en', '-')}")

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

        with tabs[1]:
            st.markdown(f"**KK:** {example.get('kk', '-')}")
            st.markdown(f"**RU:** {example.get('ru', '-')}")
            st.markdown(f"**EN:** {example.get('en', '-')}")
            
        with tabs[2]:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("🔁 **Синонимдер:**\n" + "\n".join(f"- {s}" for s in relations.get('synonyms', [])))
                st.markdown("🔼 **Жалпы ұғым:**\n" + str(relations.get('general_concept', '')))
            with cols[1]:
                st.markdown("🔽 **Арнайы ұғымдар:**\n" + "\n".join(f"- {s}" for s in relations.get('specific_concepts', [])))
                st.markdown("🔗 **Ассоциациялар:**\n" + "\n".join(f"- {s}" for s in relations.get('associative', [])))
def text_to_speech(text, lang):
    """Текстті дыбыстау үшін JavaScript функциясы"""
    js_code = f"""
    <script>
        function speak() {{
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance();
            utterance.text = "{text}";
            utterance.lang = "{'kk-KZ' if lang == 'kk' else lang + '-RU' if lang == 'ru' else 'en-US'}";
            synth.speak(utterance);
        }}
        speak();
    </script>
    """
    html(js_code, height=0)
def display_pagination(total_terms):
    total_pages = (total_terms + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    prev_col, _, next_col = st.columns([1, 8, 1])
    
    with prev_col:
        if st.button("◀️ Алдыңғы", disabled=(st.session_state.current_page == 0)):
            st.session_state.current_page -= 1
            st.rerun()
    
    with next_col:
        if st.button("Келесі ▶️", disabled=(st.session_state.current_page >= total_pages-1)):
            st.session_state.current_page += 1
            st.rerun()
    
    st.caption(f"Бет {st.session_state.current_page + 1}/{total_pages}")

# ==================== Интерфейс ====================
def main():
    st.set_page_config("Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
    st.title("📘 АКТ курсы: Электрондық ұғымдық-терминологиялық сөздік")
    
    terms_data, sha = load_github_data()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    if not terms_data or not isinstance(terms_data, dict):
        st.error("❌ Деректер жүктелмеді немесе қате формат")
        return
    
    all_terms = [term for lecture in terms_data.values() for term in lecture]
    
    with st.sidebar:
        if st.button("🌍 Байланыстарды көрсету"):
            html_content = "<div style='padding:20px; font-family:Arial;'><h3>🔗 Семантикалық байланыстар</h3>"
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
                    except:
                        continue
            html_content += "</div>"
            html(html_content, height=500, scrolling=True)

    view_mode = st.radio("🔍 Көріну режимі:", ["📂 Тақырып бойынша", "🔎 Барлық терминдерден іздеу"], horizontal=True)

    if view_mode == "📂 Тақырып бойынша":
        selected_lecture = st.selectbox("📚 Тақырыпты таңдаңыз:", list(terms_data.keys()), index=0, key="lecture_selector")
        st.subheader(f"📖 Тақырып: {selected_lecture}")
        
        initial_terms = sorted(
            terms_data[selected_lecture],
            key=lambda x: x.get('kk', '').lower() )
        letters = sorted({term['kk'][0].upper() for term in initial_terms if term.get('kk')})

        used_letters = [letter for letter in KAZ_ALPHABET 
                       if any(term.get('kk', '').upper().startswith(letter) 
                             for term in initial_terms)]
        
        selected_letter = st.session_state.get('selected_letter', 'Барлығы')
        
        with st.container():
            # Кнопка "Все"
            if st.button("🌐 Барлығы", use_container_width=True):
                selected_letter = 'Барлығы'
                st.session_state.selected_letter = selected_letter
                st.session_state.current_page = 0
                st.rerun()
            BUTTONS_PER_ROW = 8
            for i in range(0, len(used_letters), BUTTONS_PER_ROW):
                row_letters = used_letters[i:i+BUTTONS_PER_ROW]
                
                empty_cols = (BUTTONS_PER_ROW - len(row_letters)) // 2
                columns = st.columns([1]*empty_cols + [2]*len(row_letters) + [1]*empty_cols)
                
                for idx, letter in enumerate(row_letters):
                    with columns[empty_cols + idx]:
                        if st.button(
                            letter,
                            key=f"btn_{letter}_{i}",
                            help=f"Әріппен басталатын терминдер: {letter}",
                            use_container_width=True
                        ):
                            selected_letter = letter
                            st.session_state.selected_letter = selected_letter
                            st.session_state.current_page = 0
                            st.rerun()

        # Фильтрация терминов
        filtered_terms = [
            term for term in initial_terms
            if selected_letter == 'Барлығы' or 
            term.get('kk', '').upper().startswith(selected_letter)
        ]
    
        col1, col2 = st.columns([3, 2])
        with col1:
            sort_option = st.selectbox(
                "🔃 Сұрыптау түрі",
                options=[
                    "Алфавит бойынша (А-Я)",
                    "Алфавит бойынша (Я-А)"
                ],
                index=0
            )
        
        if sort_option == "Алфавит бойынша (А-Я)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''))
        elif sort_option == "Алфавит бойынша (Я-А)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''), reverse=True)
        elif sort_option == "Мысалдары барлар алдымен":
            filtered_terms.sort(key=lambda x: len(x.get('example', {}).get('kk', '')), reverse=True)

        if st.session_state.get('prev_lecture') != selected_lecture or st.session_state.get('prev_letter') != selected_letter:
            st.session_state.current_page = 0
            st.session_state.prev_lecture = selected_lecture
            st.session_state.prev_letter = selected_letter
        
        start_idx = st.session_state.current_page * ITEMS_PER_PAGE
        paginated_terms = filtered_terms[start_idx : start_idx + ITEMS_PER_PAGE]
            
        st.write(f"🔢 Жалпы терминдер: {len(filtered_terms)}")

        if paginated_terms:
            display_terms_in_columns(paginated_terms, start_idx)
            display_pagination(len(filtered_terms))
        else:
            st.warning("📭 Осы бетте терминдер жоқ")

        if st.session_state.get('selected_term'):
            display_term_full(st.session_state.selected_term)
            if st.button("❌ Жабу"):
                del st.session_state.selected_term
                st.rerun()
    else:
        search_query = st.text_input("🔍 Терминдерді іздеу", help="Кез келген тілде іздеңіз")
        filtered_terms = [
            term for term in all_terms
            if search_query.lower() in str(term).lower()
        ] if search_query else all_terms
        
        if filtered_terms:
            st.subheader(f"📚 Табылды: {len(filtered_terms)} термин")
            for idx, term in enumerate(filtered_terms):
                display_term_compact(term, idx)
        else:
            st.info("🔍 Ештеңе табылған жоқ. Іздеу сұранысын өзгертіңіз.")

        if st.session_state.get("selected_term"):
            display_term_full(st.session_state.selected_term)
            if st.button("❌ Жабу"):
                del st.session_state.selected_term
                st.rerun()

if __name__ == "__main__":
    main()
