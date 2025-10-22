import streamlit as st
from backend import df,header_styled, run_gsds, run_blast_and_get_rid
from pages.footer import base_footer
import pandas as pd

def gsds_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_gsds", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.rerun()
    
    header_styled("Gene Structure", "It provides the intronic-exonic organization of any gene.")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="gsds_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="gsds_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="gsds_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="gsds_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="gsds_Searchbutton1")

    if start_button:
        if tid:
            match = df[df["Transcript id"] == tid]
            if not match.empty:
                cds_seq = match["Cds Sequence"].values[0]
                gen_seq= match["Genomic Sequence"].values[0]
                if pd.notna(cds_seq) and cds_seq.strip() and pd.notna(gen_seq) and gen_seq.strip():
                    temp_cds = f">{tid}\n{cds_seq}"
                    temp_genomic = f">{tid}\n{gen_seq}"
                    con=st.container(border=True)
                    with con:
                        st.subheader("Gene Structure Results")
                        with st.spinner("Running GSDS...", show_time=True):
                            result_url = run_gsds(temp_cds,temp_genomic)
                            if result_url:
                                st.success(f"Results obtained!")
                                st.components.v1.iframe(src=result_url, height=800, scrolling=True)
                            else:
                                st.error("Failed to obtain results. Please try again.")
                else:
                    st.error(f"Sequence is empty for Gene ID: {tid}")
            else:
                st.error(f"No match found for Gene ID: {tid}")

        # CASE 2: Multiple Transcript IDs
        if mtid:
            temp_vars = {}
            not_found = []
            counter = 1

            for gene_id in mtid_list:
                match = df[df["Transcript id"] == gene_id]
                if not match.empty:
                    cds_seq = match["Cds Sequence"].values[0]
                    gen_seq = match["Genomic Sequence"].values[0]
                    con=st.container(border=True)
                    with con:
                        st.subheader("GSDS Results")
                        if pd.notna(cds_seq) and cds_seq.strip() and pd.notna(gen_seq) and gen_seq.strip():
                            var_name = f"temp_multi_id{counter}"
                            temp_vars[var_name] = f">{gene_id}\n{cds_seq}"
                            temp_vars[f"{var_name}_genomic"] = f">{gene_id}\n{gen_seq}"
                            with st.spinner(f"Running GSDS for {gene_id}...", show_time=True):
                                result_url = run_gsds(temp_vars[var_name], temp_vars[f"{var_name}_genomic"])
                                if result_url:
                                    with st.expander(f"GSDS Result for {gene_id}", expanded=True):
                                        st.components.v1.iframe(src=result_url, height=800, scrolling=True)
                                else:
                                    st.warning(f"GSDS failed or no results returned for Gene ID: {gene_id}")
                            counter += 1
                        else:
                            not_found.append(gene_id)
                else:
                    not_found.append(gene_id)

            if not_found:
                st.error(f"No match found for Gene ID(s): {', '.join(not_found)}")

        # CASE 3: Single LOC ID
        if locid:
            match = df[df["LOC ID"] == locid]
            if not match.empty:
                cds_seq = match["Cds Sequence"].values[0]
                gen_seq = match["Genomic Sequence"].values[0]
                if pd.notna(cds_seq) and cds_seq.strip() and pd.notna(gen_seq) and gen_seq.strip():
                    temp_id = f">{locid}\n{cds_seq}"
                    temp_genomic = f">{locid}\n{gen_seq}"
                    con=st.container(border=True)
                    with con:
                        st.subheader("Gene Structure Results")
                        with st.spinner("Running GSDS...", show_time=True):
                            result_url = run_gsds(temp_id, temp_genomic)
                            if result_url:
                                st.success(f"Results obtained!")
                                st.components.v1.iframe(src=result_url, height=800, scrolling=True)
                            else:
                                st.error("Failed to obtain results. Please try again.")
                else:
                    st.error(f"Sequence is empty for NCBI ID: {locid}")
            else:
                st.error(f"No match found for NCBI ID: {locid}")

        # CASE 4: Multiple LOC IDs
        if mlocid:
            temp_vars = {}
            not_found = []
            failed_blast = []
            counter = 1

            for loc in mlocid_list:
                match = df[df["LOC ID"] == loc]
                if not match.empty:
                    cds_seq = match["Cds Sequence"].values[0]
                    gen_seq = match["Genomic Sequence"].values[0]
                    con=st.container(border=True)
                    with con:
                        st.subheader("Gene Structure Results")
                        if pd.notna(cds_seq) and cds_seq.strip() and pd.notna(gen_seq) and gen_seq.strip():
                            var_name = f"temp_multi_id{counter}"
                            temp_vars[var_name] = f">{loc}\n{cds_seq}"
                            temp_vars[f"{var_name}_genomic"] = f">{loc}\n{gen_seq}"
                            # Run GSDS
                            with st.spinner(f"Running GSDS for {loc}...", show_time=True):
                                result_url = run_gsds(temp_vars[var_name], temp_vars[f"{var_name}_genomic"])

                                if result_url:
                                    st.success(f"Results obtained for {loc}")
                                    with st.expander(f"GSDS Result for {loc}", expanded=True):
                                        st.components.v1.iframe(src=result_url, height=800, scrolling=True)
                                else:
                                    failed_blast.append(loc)
                            counter += 1
                        else:
                            not_found.append(loc)
                else:
                    not_found.append(loc)

            if not_found:
                st.error(f"No match found or empty sequence for NCBI ID(s): {', '.join(not_found)}")

            if failed_blast:
                st.warning(f"GSDS failed or no results returned for NCBI ID(s): {', '.join(failed_blast)}")


    base_footer()
    return

if __name__ == "__main__":
    gsds_info_page()