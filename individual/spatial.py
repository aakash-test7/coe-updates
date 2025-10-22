import streamlit as st
from backend import process_locid, process_mlocid, df, show_fpkm_matrix, mlocid_error,header_styled, fpkm_glossary, show_df28_matrix, show_df28_log2, show_fpkm_log2, create_comparison_chart, create_comparison_chart_log2, combined_data, display_ml_model_prediction
from pages.footer import base_footer

def spatial_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    if "first_spatial_visit" not in st.session_state:
        st.session_state["first_spatial_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_spatial", type="tertiary",use_container_width=True):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_spatial_visit"] = True
            st.rerun()
    
    header_styled("Tissue Specific Expression Search", "It provides the information about the temporal expression among 32 different developmental stages")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ",placeholder="e.g., Ca_00001",key="spatial_Tid_input1").strip()

        mtid = con1.text_input("Enter multiple Gene IDs: ",placeholder="e.g., Ca_00001, Ca_00002",key="spatial_mTid_input2").strip()

        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ",placeholder="e.g., LOC101511858",key="spatial_Locid_input1").strip()

        mlocid = con2.text_input("Enter multiple NCBI IDs: ",placeholder="e.g., LOC101511858, LOC101496413",key="spatial_mLocid_input2").strip()

        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    # ML Model Prediction Search Section
    #st.markdown("---")
    with st.expander("ML Model Prediction Search - Find Genes by Tissue Expression Patterns", expanded=False):
        st.caption("Search genes based on ML-predicted tissue expression patterns. Perfect for exploring genes without knowing specific IDs!")
        
        # Define available ML prediction options
        ml_prediction_options = [
            "ST - Seed Tissue",
            "FP - Flower Parts",
            "FDS - Flower Developmental Stages",
            "GT - Green Tissue",
            "RT - Root Tissue"
        ]
        
        selected_predictions = st.multiselect(
            "Select Tissue Predictions (multiple allowed)",
            options=ml_prediction_options,
            placeholder="Choose one or more tissue types",
            key="spatial_ml_prediction_search"
        )
        c1,c2,c3=st.columns(3)
        if c2.button("Search by ML Predictions", use_container_width=True, key="spatial_ml_search_btn", type="secondary"):
            if selected_predictions:
                # Extract short codes (ST, FP, FDS, GT, RT) from selections
                prediction_codes = [pred.split(" - ")[0] for pred in selected_predictions]
                
                with st.spinner("Searching ML prediction database..."):
                    # Search combined_data for matching predictions
                    all_transcript_ids = set()
                    matches_info = []
                    
                    for prediction in prediction_codes:
                        matches = combined_data[
                            combined_data['Resultant'].astype(str).str.contains(prediction, case=False, na=False)
                        ]
                        if not matches.empty:
                            found_ids = matches['Transcript id'].unique().tolist()
                            all_transcript_ids.update(found_ids)
                            matches_info.append({
                                'prediction': prediction,
                                'count': len(found_ids),
                                'found_ids': found_ids  # Store all IDs for this prediction
                            })
                    
                    all_transcript_ids = list(all_transcript_ids)
                    
                if all_transcript_ids:
                    st.success(f"Found {len(all_transcript_ids)} total genes across selected tissue predictions!")
                    
                    # Display Gene IDs separately for each prediction
                    st.write("**Gene IDs by Tissue Type:**")
                    
                    for info in matches_info:
                        full_name = next(opt for opt in ml_prediction_options if opt.startswith(info['prediction']))
                        st.write(f"**{full_name}** - {info['count']} genes:")
                        gene_ids_str = ", ".join(info['found_ids'])
                        st.code(gene_ids_str, language="text")
                    
                    st.info("**Tip:** Copy any set of Gene IDs above and paste them into the 'Multiple Gene IDs' field, then click the Search button to view expression data!")
                else:
                    st.error("No genes found for the selected ML predictions!")
            else:
                st.warning("Please select at least one tissue prediction!")
    

    con_btn1, con_btn2, con_btn3 = st.columns([2, 2, 2])
    with con_btn2:
        start_button = st.button("Search", use_container_width=True, key="spatial_Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_spatial_visit", True):
        st.session_state["first_spatial_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:
            tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
            with tab1:
                con=st.container(border=True)
                with con:
                    st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_matrix(temp_list, is_multi=True) if len(temp_list) > 1 else show_fpkm_matrix(temp_list[0])
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                    show_df28_matrix(temp_list, is_multi=True) if len(temp_list) > 1 else show_df28_matrix(temp_list[0])
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                    create_comparison_chart(temp_list, is_multi=True) if len(temp_list) > 1 else create_comparison_chart(temp_list[0])
                    fpkm_glossary()
            
            # Display ML Model Prediction
            display_ml_model_prediction(temp_list)
            
            with tab2:
                con=st.container(border=True)
                with con:
                    st.subheader("log2(FPKM+1) Transformed Values")
                    show_fpkm_log2(temp_list, is_multi=True) if len(temp_list) > 1 else show_fpkm_log2(temp_list[0])
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                    show_df28_log2(temp_list, is_multi=True) if len(temp_list) > 1 else show_df28_log2(temp_list[0])
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                    create_comparison_chart_log2(temp_list, is_multi=True) if len(temp_list) > 1 else create_comparison_chart_log2(temp_list[0])
                    fpkm_glossary()
            
            # Display ML Model Prediction (already shown in tab1, but including for consistency)
            # Skipping here since it's already displayed after tab1
        
        st.toast("Task completed successfully.")
    elif start_button:

        # Single Gene ID (tid)
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
                with tab1:
                    con = st.container(border=True)
                    with con:
                        st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                        show_fpkm_matrix(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_matrix(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart(tid)
                        fpkm_glossary()
                
                # Display ML Model Prediction
                display_ml_model_prediction(tid)
                
                with tab2:
                    con = st.container(border=True)
                    with con:
                        st.subheader("log2(FPKM+1) Transformed Values")
                        show_fpkm_log2(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_log2(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart_log2(tid)
                        fpkm_glossary()
            else:
                st.error(f"No match found for Gene ID: {tid}")

            st.toast("Task completed successfully.")

        # Multiple Gene IDs (mtid)
        elif mtid:
            mtid_list = [gene_id.strip() for gene_id in mtid.replace(",", " ").split()]
            mtid_list.sort()

            matching_rows = df[df['Transcript id'].isin(mtid_list)]
            found_ids = matching_rows['Transcript id'].unique().tolist()
            not_found_ids = [x for x in mtid_list if x not in found_ids]

            if not matching_rows.empty:
                tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
                with tab1:
                    con = st.container(border=True)
                    with con:
                        st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                        show_fpkm_matrix(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_matrix(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart(mtid_list, is_multi=True)
                        fpkm_glossary()
                
                # Display ML Model Prediction
                display_ml_model_prediction(mtid_list)
                
                with tab2:
                    con = st.container(border=True)
                    with con:
                        st.subheader("log2(FPKM+1) Transformed Values")
                        show_fpkm_log2(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_log2(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart_log2(mtid_list, is_multi=True)
                        fpkm_glossary()
            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

            st.toast("Task completed successfully.")

        # Single NCBI ID (locid)
        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
                with tab1:
                    con = st.container(border=True)
                    with con:
                        st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                        show_fpkm_matrix(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_matrix(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart(tid)
                        fpkm_glossary()
                
                # Display ML Model Prediction
                display_ml_model_prediction(tid)
                
                with tab2:
                    con = st.container(border=True)
                    with con:
                        st.subheader("log2(FPKM+1) Transformed Values")
                        show_fpkm_log2(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                        show_df28_log2(tid)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                        create_comparison_chart_log2(tid)
                        fpkm_glossary()
            else:
                st.error(f"No match found for NCBI ID: {locid}")
            st.toast("Task completed successfully.")

        # Multiple NCBI IDs (mlocid)
        elif mlocid:
            available, rejected = mlocid_error(mlocid)
            if available:
                mtid = process_mlocid(",".join(available))
                mtid_list = [x.strip() for x in mtid.replace(",", " ").split()]
                mtid_list.sort()
                matching_rows = df[df['Transcript id'].isin(mtid_list)]
                if not matching_rows.empty:
                    tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
                    with tab1:
                        con = st.container(border=True)
                        with con:
                            st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                            show_fpkm_matrix(mtid_list, is_multi=True)
                            c1,c2=con.columns(2)
                            with c1.popover("Data Source", use_container_width=True):
                                st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                            with c2.popover("Research Article", use_container_width=True):
                                st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                            show_df28_matrix(mtid_list, is_multi=True)
                            c1,c2=con.columns(2)
                            with c1.popover("Data Source", use_container_width=True):
                                st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                            with c2.popover("Research Article", use_container_width=True):
                                st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                            create_comparison_chart(mtid_list, is_multi=True)
                            fpkm_glossary()
                    
                    # Display ML Model Prediction
                    display_ml_model_prediction(mtid_list)
                    
                    with tab2:
                        con = st.container(border=True)
                        with con:
                            st.subheader("log2(FPKM+1) Transformed Values")
                            show_fpkm_log2(mtid_list, is_multi=True)
                            c1,c2=con.columns(2)
                            with c1.popover("Data Source", use_container_width=True):
                                st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                            with c2.popover("Research Article", use_container_width=True):
                                st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                            show_df28_log2(mtid_list, is_multi=True)
                            c1,c2=con.columns(2)
                            with c1.popover("Data Source", use_container_width=True):
                                st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                            with c2.popover("Research Article", use_container_width=True):
                                st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                            create_comparison_chart_log2(mtid_list, is_multi=True)
                            fpkm_glossary()
                st.toast("Task completed successfully.")

            if rejected:
                st.error(f"No matches found for NCBI IDs: {', '.join(rejected)}")

        else:
            st.warning("Need either a Gene ID or NCBI ID to proceed.")

    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")

    base_footer()
    return

if __name__ == "__main__":
    spatial_info_page()