import streamlit as st
from backend import process_locid, process_mlocid, df, show_orthologs_data, show_inparalogs_data, mlocid_error, header_styled
from pages.footer import base_footer

def orthologs_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    if "first_orthologs_visit" not in st.session_state:
        st.session_state["first_orthologs_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_orth", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_orthologs_visit"] = True
            st.rerun()
    
    header_styled("Orthologs/Paralogs", "Users can get the details about the conserveness in gene sequences among/within genome of various crop plants")
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.container(border=True)
        tid = c1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="orth_Tid_input1").strip(); mtid = c1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="orth_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)
    with col2:
        c2 = st.container(border=True)
        locid = c2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="orth_Locid_input1").strip()
        mlocid = c2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="orth_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)
    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc2:
        start_button = st.button("Search", use_container_width=True, key="orth_Searchbutton1")

    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_orthologs_visit", True):
        con= st.container(border=True)
        st.session_state["first_orthologs_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:
            with con:
                st.subheader("Ortholog")
                show_orthologs_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_orthologs_data(temp_list[0])
        con= st.container(border=True)
        if temp_list:
            with con:
                st.subheader("Paralog")
                show_inparalogs_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_inparalogs_data(temp_list[0])
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
        st.toast("Task completed successfully.")

    elif start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Ortholog")
                    show_orthologs_data(tid)
                    st.subheader("Paralog")
                    show_inparalogs_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
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
                    st.subheader("Ortholog")
                    show_orthologs_data(mtid_list, is_multi=True)
                    st.subheader("Paralog")
                    show_inparalogs_data(mtid_list, is_multi=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

            st.toast("Task completed successfully.")

        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Ortholog")
                    show_orthologs_data(tid)
                    st.subheader("Paralog")
                    show_inparalogs_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
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
                        st.subheader("Ortholog")
                        show_orthologs_data(mtid_list, is_multi=True)
                        st.subheader("Paralog")
                        show_inparalogs_data(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
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
    orthologs_info_page()