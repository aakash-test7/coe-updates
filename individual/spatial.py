import streamlit as st
from backend import process_locid, process_mlocid, df, show_fpkm_matrix, mlocid_error,header_styled, fpkm_glossary, show_df28_matrix
from pages.footer import base_footer

def spatial_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
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

    con_btn1, con_btn2, con_btn3 = st.columns([2, 2, 2])
    with con_btn2:
        start_button = st.button("Search", use_container_width=True, key="spatial_Searchbutton1")

    if start_button:

        # Single Gene ID (tid)
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_matrix(tid)
                    show_df28_matrix(tid)
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
                con = st.container(border=True)
                with con:
                    st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_matrix(mtid_list, is_multi=True)
                    show_df28_matrix(mtid_list, is_multi=True)
                    fpkm_glossary()
            if not_found_ids:
                st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

            st.toast("Task completed successfully.")

        # Single NCBI ID (locid)
        elif locid:
            tid = process_locid(locid)
            matching_row = df[df['Transcript id'] == tid]
            if not matching_row.empty:
                con = st.container(border=True)
                with con:
                    st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_matrix(tid)
                    show_df28_matrix(tid)
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
                    con = st.container(border=True)
                    with con:
                        st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                        show_fpkm_matrix(mtid_list, is_multi=True)
                        show_df28_matrix(mtid_list, is_multi=True)
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