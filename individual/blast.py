import streamlit as st
from backend import df,header_styled, run_blast_and_get_rid
from pages.footer import base_footer
import pandas as pd

def blast_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        if st.button("← Back to Home", key="back_to_home_blast", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.rerun()
    
    header_styled("BLAST", "It blasts.")
    #con=st.container(border=True)
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="blast_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="blast_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="blast_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="blast_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)
    con=st.container(border=True)
    seq_input=con.text_input("Enter the Sequence: ", placeholder="e.g., ATGC...", key="blast_Seq_input1").strip()

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="blast_Searchbutton1")

    if start_button:
        if tid:
            match = df[df["Transcript id"] == tid]
            if not match.empty:
                cds_seq = match["Cds Sequence"].values[0]
                if pd.notna(cds_seq) and cds_seq.strip():
                    temp_id = cds_seq
                    con=st.container(border=True)
                    with con:
                        st.subheader("BLAST Results")
                        with st.spinner("Running BLAST...", show_time=True):
                            rid = run_blast_and_get_rid(temp_id)
                            if rid:
                                st.success(f"RID obtained: `{rid}`")
                                result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"

                                st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                            else:
                                st.error("Failed to obtain RID. Please try again.")
                else:
                    st.error(f"Cds Sequence is empty for Gene ID: {tid}")
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
                    con=st.container(border=True)
                    with con:
                        st.subheader("BLAST Results")
                        if pd.notna(cds_seq) and cds_seq.strip():
                            var_name = f"temp_multi_id{counter}"
                            temp_vars[var_name] = cds_seq
                            with st.spinner(f"Running BLAST for {gene_id}...", show_time=True):
                                rid = run_blast_and_get_rid(cds_seq)
                                if rid:
                                    result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"
                                    with st.expander(f"BLAST Result for {gene_id} (RID: {rid})", expanded=True):
                                        st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                                else:
                                    st.warning(f"BLAST failed or no RID returned for Gene ID: {gene_id}")
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
                if pd.notna(cds_seq) and cds_seq.strip():
                    temp_id = cds_seq
                    con=st.container(border=True)
                    with con:
                        st.subheader("BLAST Results")
                        with st.spinner("Running BLAST...", show_time=True):
                            rid = run_blast_and_get_rid(temp_id)
                            if rid:
                                st.success(f"RID obtained: `{rid}`")
                                result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"

                                st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                            else:
                                st.error("Failed to obtain RID. Please try again.")
                else:
                    st.error(f"Cds Sequence is empty for NCBI ID: {locid}")
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
                    con=st.container(border=True)
                    with con:
                        st.subheader("BLAST Results")
                        if pd.notna(cds_seq) and cds_seq.strip():
                            var_name = f"temp_multi_id{counter}"
                            temp_vars[var_name] = cds_seq
                            # Run BLAST
                            with st.spinner(f"Running BLAST for {loc}...", show_time=True):
                                rid = run_blast_and_get_rid(cds_seq)

                                if rid:
                                    st.success(f"RID obtained for {loc}: `{rid}`")
                                    result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"
                                    with st.expander(f"BLAST Result for {loc} (RID: {rid})", expanded=True):
                                        st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                                else:
                                    failed_blast.append(loc)
                            counter += 1
                        else:
                            not_found.append(loc)
                else:
                    not_found.append(loc)

            # Display errors after loop
            if not_found:
                st.error(f"No match found or empty sequence for NCBI ID(s): {', '.join(not_found)}")

            if failed_blast:
                st.warning(f"BLAST failed or no RID returned for NCBI ID(s): {', '.join(failed_blast)}")

        # CASE 5: Direct Sequence Input
        if seq_input:
            temp_id = seq_input
            con=st.container(border=True)
            with con:
                st.subheader("BLAST Results")
                with st.spinner("Running BLAST...", show_time=True):
                    rid = run_blast_and_get_rid(temp_id)
                    if rid:
                        st.success(f"RID obtained: `{rid}`")
                        result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"

                        st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                    else:
                        st.error("Failed to obtain RID. Please try again.")

    base_footer()
    return

if __name__ == "__main__":
    blast_info_page()