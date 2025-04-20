import streamlit as st
import json

# ================================
# Загрузка данных из файла
# ================================
with open("data.json", "r", encoding="utf-8") as f:
    terms = json.load(f)

# ================================
# Настройка страницы
# ================================
st.set_page_config(page_title="Электрондық ұғымдық-терминологиялық сөздік", layout="wide")
st.title("📘 Электрондық ұғымдық-терминологиялық сөздік")

# ================================
# Функция для отображения термина
# ================================
def show_term(term):
    st.subheader(f"🖥 {term['kk']} / {term['ru']} / {term['en']}")
    
    with st.expander("📖 Анықтама / Определение / Definition", expanded=True):
        st.markdown(f"**KK:** {term['definition']['kk']}")
        st.markdown(f"**RU:** {term['definition']['ru']}")
        st.markdown(f"**EN:** {term['definition']['en']}")
    
    with st.expander("💬 Мысал / Пример / Example"):
        st.markdown(f"**KK:** {term['example']['kk']}")
        st.markdown(f"**RU:** {term['example']['ru']}")
        st.markdown(f"**EN:** {term['example']['en']}")
    
    if 'relations' in term:
        with st.expander("🧠 Семантикалық байланыстар / Semantic Relations"):
            rel = term['relations']
            if rel.get('synonyms'):
                st.markdown("**🔁 Синонимдер / Synonyms:**")
                for s in rel['synonyms']:
                    # При нажатии на синоним задаём выбранный термин в session_state
                    if st.button(s, key=f"syn_{s}"):
                        st.session_state["selected_term"] = s
            if rel.get('antonyms'):
                st.markdown(f"**🆚 Антонимдер / Antonyms:** {', '.join(rel['antonyms'])}")
            if rel.get('broader_term'):
                st.markdown(f"**🔼 Жалпылама ұғым / Broader term:** {rel['broader_term']}")
            if rel.get('narrower_terms'):
                st.markdown(f"**🔽 Арнайы ұғымдар / Narrower terms:** {', '.join(rel['narrower_terms'])}")
            if rel.get('related_terms'):
                st.markdown(f"**🔗 Қатысты ұғымдар / Related terms:** {', '.join(rel['related_terms'])}")
    
    if term.get("image"):
        st.image(term['image'], caption="Иллюстрация", use_column_width=True)
    
    if term.get("source"):
        st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")
    
    st.markdown("---")

# ================================
# Режим: поиск или навигация по лекциям
# ================================

# Поле ввода для поиска термина
search_query = st.text_input("🔍 Терминді іздеу:", "").strip().lower()

if search_query:
    # Режим поиска: обход по всем лекциям и терминам
    st.header(f"🔎 Іздеу нәтижелері: \"{search_query}\"")
    found_terms = []

    for lecture, term_list in terms.items():
        for term in term_list:
            if (search_query in term['kk'].lower() or 
                search_query in term['ru'].lower() or 
                search_query in term['en'].lower()):
                found_terms.append((lecture, term))
    
    if not found_terms:
        st.warning("🛑 Бұл іздеу сұранысына сәйкес терминдер табылмады.")
    else:
        for lecture, term in found_terms:
            st.subheader(f"📂 {lecture} | 🖥 {term['kk']} / {term['ru']} / {term['en']}")
            with st.expander("📖 Анықтама / Определение / Definition"):
                st.markdown(f"**KK:** {term['definition']['kk']}")
                st.markdown(f"**RU:** {term['definition']['ru']}")
                st.markdown(f"**EN:** {term['definition']['en']}")
            with st.expander("💬 Мысал / Пример / Example"):
                st.markdown(f"**KK:** {term['example']['kk']}")
                st.markdown(f"**RU:** {term['example']['ru']}")
                st.markdown(f"**EN:** {term['example']['en']}")
            
            if 'relations' in term:
                with st.expander("🧠 Семантикалық байланыстар / Semantic Relations"):
                    rel = term['relations']
                    if rel.get('synonyms'):
                        st.markdown("**🔁 Синонимдер / Synonyms:**")
                        for s in rel['synonyms']:
                            if st.button(s, key=f"syn_search_{s}"):
                                st.session_state["selected_term"] = s
                    if rel.get('antonyms'):
                        st.markdown(f"**🆚 Антонимдер / Antonyms:** {', '.join(rel['antonyms'])}")
                    if rel.get('broader_term'):
                        st.markdown(f"**🔼 Жалпылама ұғым / Broader term:** {rel['broader_term']}")
                    if rel.get('narrower_terms'):
                        st.markdown(f"**🔽 Арнайы ұғымдар / Narrower terms:** {', '.join(rel['narrower_terms'])}")
                    if rel.get('related_terms'):
                        st.markdown(f"**🔗 Қатысты ұғымдар / Related terms:** {', '.join(rel['related_terms'])}")
            
            if term.get("image"):
                st.image(term['image'], caption="Иллюстрация", use_column_width=True)
            if term.get("source"):
                st.markdown(f"🔗 [Дереккөз / Источник / Source]({term['source']})")
            
            st.markdown("---")
else:
    # Если поиск не активен, используем навигацию по лекциям
    st.session_state.setdefault("selected_term", None)
    
    lecture = st.sidebar.selectbox("📂 Таңдаңыз дәріс (тему):", list(terms.keys()))
    st.header(lecture)
    
    selected = None
    target = st.session_state.get("selected_term")
    # Поиск выбранного термина по 'kk'
    for term in terms[lecture]:
        if term["kk"] == target:
            selected = term
            break

    # Вывод выбранного термина (если имеется) первым
    if selected:
        show_term(selected)
        st.divider()
    
    # Вывод остальных терминов текущей лекции
    for term in terms[lecture]:
        if term != selected:
            show_term(term)
