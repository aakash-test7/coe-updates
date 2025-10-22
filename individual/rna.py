import streamlit as st
from backend import process_locid, process_mlocid, df, show_rna_data, show_lncrna_data, mlocid_error, header_styled
from pages.footer import base_footer

def rna_type_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    if "first_rna_visit" not in st.session_state:
        st.session_state["first_rna_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_rna", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_rna_visit"] = True
            st.rerun()
    
    header_styled("RNA type Search", "It gives details about the coding potential of RNA (mRNA or LncRNA)")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="rna_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="rna_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="rna_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="rna_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con_btn1, con_btn2, con_btn3 = st.columns([2, 2, 2])
    with con_btn2:
        start_button = st.button("Search", use_container_width=True, key="rna_Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_rna_visit", True):
        con= st.container(border=True)
        st.session_state["first_rna_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:
            with con:
                st.subheader("RNA")
                show_rna_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_rna_data(temp_list[0])

                st.subheader("lncRNA")
                show_lncrna_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_lncrna_data(temp_list[0])
        st.toast("Task completed successfully.")
    elif start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("RNA")
                    show_rna_data(tid)

                    st.subheader("lncRNA")
                    show_lncrna_data(tid)
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
                    st.subheader("RNA")
                    show_rna_data(mtid_list, is_multi=True)

                    st.subheader("lncRNA")
                    show_lncrna_data(mtid_list, is_multi=True)
            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

            st.toast("Task completed successfully.")

        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("RNA")
                    show_rna_data(tid)

                    st.subheader("lncRNA")
                    show_lncrna_data(tid)
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
                        st.subheader("RNA")
                        show_rna_data(mtid_list, is_multi=True)

                        st.subheader("lncRNA")
                        show_lncrna_data(mtid_list, is_multi=True)
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
    rna_type_page()