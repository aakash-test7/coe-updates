import streamlit as st
from backend import process_locid, process_mlocid, df, show_sequence_data_p, mlocid_error,header_styled
from pages.footer import base_footer

def crispr_info_page():
    header_styled("CRISPR Construct Design", "It provides detailed information about the region to be edited for construct design purpose.")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="crispr_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="crispr_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="crispr_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="crispr_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="crispr_Searchbutton1")

    if start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con=st.container(border=True)
                with con:
                    st.subheader("Sequence data")
                    show_sequence_data_p(tid)

                    with st.expander("CRISPR Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://chopchop.cbu.uib.no/#" height="800" width="100%" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

            else:
                st.error(f"No match found for Gene ID: {tid}")

            st.toast("Task completed successfully.")
            
        elif mtid:
            mtid_list = [tid.strip() for tid in mtid.replace(",", " ").split()]
            mtid_list.sort()

            matching_rows = df[df['Transcript id'].isin(mtid_list)]
            found_ids = matching_rows['Transcript id'].unique().tolist()
            not_found_ids = [x for x in mtid_list if x not in found_ids]

            if not matching_rows.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("\nSequences data")
                    show_sequence_data_p(mtid_list, is_multi=True)

                    with st.expander("CRISPR Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://chopchop.cbu.uib.no/#" width="100%" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

            st.toast("Task completed successfully.")
            
        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con=st.container(border=True)
                with con:
                    st.subheader("Sequence data")
                    show_sequence_data_p(tid)

                    with st.expander("CRISPR Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://chopchop.cbu.uib.no/#" width="100%" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

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
                        st.subheader("\nSequences data")
                        show_sequence_data_p(mtid_list, is_multi=True)

                        with st.expander("CRISPR Design", expanded=True):
                            st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://chopchop.cbu.uib.no/#" width="100%" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

                st.toast("Task completed successfully.")
            if rejected:
                st.error(f"No matches found for NCBI IDs: {', '.join(rejected)}")

            st.toast("Task completed successfully.")
            
    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")

    base_footer()
    return

if __name__ == "__main__":
    crispr_info_page()