import streamlit as st
from backend import process_locid, process_mlocid, df, show_mirna_data, mlocid_error,header_styled
from pages.footer import base_footer

def mirna_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)

    if "first_mirna_visit" not in st.session_state:
        st.session_state["first_mirna_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_mirna", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_mirna_visit"] = True
            st.rerun()
    
    header_styled("miRNA Target", "Users can get the details about the putative miRNAs of the particular gene")
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.container(border=True)
        tid = c1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="mirna_Tid_input1").strip(); mtid = c1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="mirna_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)
    with col2:
        c2 = st.container(border=True)
        locid = c2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="mirna_Locid_input1").strip()
        mlocid = c2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="mirna_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc2:
        start_button = st.button("Search", use_container_width=True, key="mirna_Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_mirna_visit", True):
        con= st.container(border=True)
        st.session_state["first_mirna_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:
            with con:
                st.subheader("miRNA Target")
                show_mirna_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_mirna_data(temp_list[0])
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("PmiREN - https://pmiren.com")
                    st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
        st.toast("Task completed successfully.")
    elif start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("miRNA Target")
                    show_mirna_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("PmiREN - https://pmiren.com")
                        st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
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
                    st.subheader("miRNA Target")
                    show_mirna_data(mtid_list, is_multi=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("PmiREN - https://pmiren.com")
                        st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")
            st.toast("Task completed successfully.")
        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("miRNA Target")
                    show_mirna_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("PmiREN - https://pmiren.com")
                        st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                        st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
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
                        st.subheader("miRNA Target")
                        show_mirna_data(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("PmiREN - https://pmiren.com")
                            st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                            st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                            st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                            st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
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
    mirna_info_page()