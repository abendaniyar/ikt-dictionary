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
    st.set_page_config(page_title="АКТ терминдер сөздігі", page_icon="📘", layout="wide")
    st.markdown("""
    <style>
    .block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem;}
    [data-testid="stExpander"] {border: 1px solid #e4eaf2; border-radius: 12px; margin-bottom: .4rem;}
    [data-testid="stExpander"] summary {font-size: 1rem; font-weight: 600;}
    [data-testid="stCaptionContainer"] {color: #64748b;}
    @media (max-width: 640px) {
        .block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
        h1 {font-size: 1.7rem !important;}
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("📘 АКТ терминдер сөздігі")
    st.caption("Қазақша · Русский · English  |  Терминдерді іздеңіз және тақырыптар бойынша шолыңыз")

    terms_data, _ = load_github_data()
    if not isinstance(terms_data, dict) or not terms_data:
        st.error("❌ Деректер жүктелмеді немесе қате формат")
        return

    query = st.text_input(
        "🔍 Термин іздеу",
        placeholder="Қазақша, орысша немесе ағылшынша іздеңіз",
    )
    topic_col, sort_col = st.columns([3, 2])
    with topic_col:
        topic = st.selectbox("📚 Тақырып", ["Барлық тақырыптар"] + list(terms_data.keys()))
    with sort_col:
        sort_order = st.selectbox("🔃 Сұрыптау", ["Алфавит бойынша (А–Я)", "Алфавит бойынша (Я–А)"])

    terms = [term for group in terms_data.values() for term in group] if topic == "Барлық тақырыптар" else terms_data[topic]
    query_normalized = query.strip().casefold()
    if query_normalized:
        terms = [term for term in terms if query_normalized in json.dumps(term, ensure_ascii=False).casefold()]

    available_letters = [letter for letter in KAZ_ALPHABET if any(
        str(term.get("kk", "")).upper().startswith(letter) for term in terms
    )]
    letter = st.selectbox("🔤 Бастапқы әріп", ["Барлығы"] + available_letters)
    if letter != "Барлығы":
        terms = [term for term in terms if str(term.get("kk", "")).upper().startswith(letter)]
    terms = sorted(terms, key=lambda term: str(term.get("kk", "")).casefold(), reverse=sort_order.endswith("(Я–А)"))

    filters = (query_normalized, topic, sort_order, letter)
    if st.session_state.get("dictionary_filters") != filters:
        st.session_state.dictionary_page = 0
        st.session_state.dictionary_filters = filters
    page = st.session_state.get("dictionary_page", 0)
    page_size = 30
    total = len(terms)
    pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, pages - 1)
    start = page * page_size
    end = min(start + page_size, total)
    st.markdown(f"**📚 Табылды: {total} термин**")
    if total:
        st.caption(f"Көрсетілгені: {start + 1}–{end} / {total}")
        for term_index, term in enumerate(terms[start:end], start=start):
            title = str(term.get("kk") or term.get("ru") or term.get("en") or "Атауы жоқ")
            with st.expander("📘 " + title):
                translations = [f"{label}: {term[lang]}" for lang, label in (("kk", "Қазақша"), ("ru", "Русский"), ("en", "English")) if term.get(lang)]
                st.caption("  |  ".join(translations))
                sound_ru, sound_en = st.columns(2)
                with sound_ru:
                    if term.get("ru") and st.button("🔊 Русский", key=f"ru_{term_index}"):
                        text_to_speech(term["ru"], "ru")
                with sound_en:
                    if term.get("en") and st.button("🔊 English", key=f"en_{term_index}"):
                        text_to_speech(term["en"], "en")
                tabs = st.tabs(["📖 Анықтама", "💬 Мысал", "🔗 Байланыстар"])
                with tabs[0]:
                    definition = term.get("definition") or {}
                    for lang, label in (("kk", "Қазақша"), ("ru", "Русский"), ("en", "English")):
                        if definition.get(lang):
                            st.markdown(f"**{label}:** {definition[lang]}")
                    if term.get("image"):
                        st.image(term["image"], width=200)
                    if term.get("source"):
                        st.link_button("🔗 Дереккөз / Источник / Source", term["source"])
                with tabs[1]:
                    examples = term.get("example") or {}
                    if not any(examples.values()):
                        st.caption("Мысалдар әзірге қосылмаған.")
                    for lang, label in (("kk", "Қазақша"), ("ru", "Русский"), ("en", "English")):
                        if examples.get(lang):
                            st.markdown(f"**{label}:** {examples[lang]}")
                with tabs[2]:
                    relations = term.get("relations") or {}
                    for key, label in (("synonyms", "Синонимдер"), ("general_concept", "Жалпы ұғым"), ("specific_concepts", "Арнайы ұғымдар"), ("associative", "Ассоциациялар")):
                        value = relations.get(key)
                        if value:
                            text = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
                            st.markdown(f"**{label}:** {text}")
                    if not any(relations.values()):
                        st.caption("Байланыстар әзірге қосылмаған.")
        prev_col, page_col, next_col = st.columns([1, 2, 1])
        with prev_col:
            if st.button("← Алдыңғы", disabled=page == 0, use_container_width=True):
                st.session_state.dictionary_page = page - 1
                st.rerun()
        with page_col:
            st.caption(f"Бет {page + 1} / {pages}")
        with next_col:
            if st.button("Келесі →", disabled=page >= pages - 1, use_container_width=True):
                st.session_state.dictionary_page = page + 1
                st.rerun()
    else:
        st.info("Термин табылмады. Іздеу сөзін немесе сүзгілерді өзгертіңіз.")

if __name__ == "__main__":
    main()
