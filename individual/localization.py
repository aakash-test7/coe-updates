import streamlit as st
from backend import process_locid, process_mlocid, df, show_cellular_Localization, mlocid_error, show_sequence_data_p, header_styled
from pages.footer import base_footer

def local_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)

    if "first_local_visit" not in st.session_state:
        st.session_state["first_local_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_local", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_local_visit"] = True
            st.rerun()
    
    header_styled("Localization Search", "It provides the probable cellular location of a gene expression and predicted on the basis of signal sequences")
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.container(border=True)
        tid = c1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="local_Tid_input1").strip(); mtid = c1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="local_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)
    with col2:
        c2 = st.container(border=True)
        locid = c2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="local_Locid_input1").strip()
        mlocid = c2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="local_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc2:
        start_button = st.button("Search", use_container_width=True, key="local_Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_local_visit", True):
        con= st.container(border=True)
        st.session_state["first_local_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:
            with con:
                st.subheader("Cellular-localization")
                show_cellular_Localization(temp_list, is_multi=True) if len(temp_list) > 1 else show_cellular_Localization(temp_list[0])
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                with c2.popover("Research Article", use_container_width=True):    
                    st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                    st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

        st.toast("Task completed successfully.")
    elif start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Cellular-localization")
                    show_cellular_Localization(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                    with c2.popover("Research Article", use_container_width=True):    
                        st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                        st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

            else:
                st.error(f"No match found for Gene ID: {tid}")
            st.toast("Task completed successfully.")
        elif mtid:
            mtid_list = [x.strip() for x in mtid.replace(",", " ").split()]
            mtid_list.sort()
            matching_rows = df[df['Transcript id'].isin(mtid_list)]
            found_ids = matching_rows['Transcript id'].unique().tolist()
            not_found_ids = [x for x in mtid_list if x not in found_ids]
            if not matching_rows.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Cellular-localization")
                    show_cellular_Localization(mtid_list, is_multi=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                    with c2.popover("Research Article", use_container_width=True):    
                        st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                        st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")
            st.toast("Task completed successfully.")
        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Cellular-localization")
                    show_cellular_Localization(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                    with c2.popover("Research Article", use_container_width=True):    
                        st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                        st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

            else:
                st.error(f"No match found for NCBI ID: {locid}")
            st.toast("Task completed successfully.")
        elif mlocid:
            available, rejected = mlocid_error(mlocid)
            if available:
                mtid = process_mlocid(",".join(available))
                mtid_list = [x.strip() for x in mtid.replace(",", " ").split()]
                mtid_list.sort()
                matching_rows = df[df['Transcript id'].isin(mtid_list)]
                if not matching_rows.empty:
                    con = st.container(border=True)
                    with con:
                        st.subheader("Cellular-localization")
                        show_cellular_Localization(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                        with c2.popover("Research Article", use_container_width=True):    
                            st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                            st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

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
    local_info_page()