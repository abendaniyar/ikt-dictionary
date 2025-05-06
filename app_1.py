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
        
        # 1. Ішкі іздеу
        topic_search = st.text_input("🔍 Тақырып ішінде іздеу")
        
        # 2. Әріп бойынша сүзгі
        initial_terms = terms_data[selected_lecture]
        letters = sorted({term['kk'][0].upper() for term in initial_terms if term.get('kk')})
        selected_letter = st.selectbox("🔤 Әріп бойынша сүзгі", ["Барлығы"] + letters)
        
        # Фильтрация
        filtered_terms = [
            term for term in initial_terms
            if (topic_search.lower() in term.get('kk', '').lower()) and 
               (selected_letter == "Барлығы" or term.get('kk', '').upper().startswith(selected_letter))
        ]

        # 3. Сұрыптау
        sort_option = st.selectbox(
            "🔃 Сұрыптау",
            options=["А → Я (қаз)", "Я → А (қаз)", "Мысалдары барлар алдымен"],
            index=0
        )
        
        if sort_option == "А → Я (қаз)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''))
        elif sort_option == "Я → А (қаз)":
            filtered_terms.sort(key=lambda x: x.get('kk', ''), reverse=True)
        elif sort_option == "Мысалдары барлар алдымен":
            filtered_terms.sort(key=lambda x: bool(x.get('example')), reverse=True)

        # 4. Пагинация
        ITEMS_PER_PAGE = 15
        total_pages = max(1, (len(filtered_terms) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = st.number_input("📄 Бет", 
                              min_value=1, 
                              max_value=total_pages, 
                              value=1,
                              key="pagination")
        
        # Терминдерді көрсету
        start_idx = (page-1)*ITEMS_PER_PAGE
        paginated_terms = filtered_terms[start_idx : start_idx+ITEMS_PER_PAGE]
        
        st.write(f"🔢 Терминдер саны: {len(filtered_terms)}")
        st.caption(f"Бет {page} / {total_pages}")
        
        for term in paginated_terms:
            display_term_compact(term)
        
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
            for term in filtered_terms:
                display_term_compact(term)
                st.divider()
        else:
            st.info("🔍 Ештеңе табылған жоқ. Іздеу сұранысын өзгертіңіз.")

if __name__ == "__main__":
    main()
