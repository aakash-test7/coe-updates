import streamlit as st
from backend import process_locid, process_mlocid, df, show_sequence_data_p, mlocid_error,header_styled,show_sequence_data_cds,run_blast_and_get_primer
from pages.footer import base_footer
import pandas as pd
def primer_cloning():
    col1, col2 = st.columns(2)
    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="primer_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="primer_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="primer_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="primer_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="primer_Searchbutton1")

    if start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con=st.container(border=True)
                with con:
                    st.subheader("Sequence data")
                    show_sequence_data_p(tid)

                    with st.expander("Primer Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://www.primer3plus.com/" width="80%" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

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
                    with st.expander("Primer Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://www.primer3plus.com/" width="900" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

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
                    with st.expander("Primer Design", expanded=True):
                        st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://www.primer3plus.com/" width="900" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

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

                        with st.expander("Primer Design", expanded=True):
                            st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://www.primer3plus.com/" width="900" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

                st.toast("Task completed successfully.")
            if rejected:
                st.error(f"No matches found for NCBI IDs: {', '.join(rejected)}")

            st.toast("Task completed successfully.")
            
    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")

    return

def primer_qrt():
    col1, col2 = st.columns(2)
    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="ginfo_Tid_input1_cds").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="ginfo_mTid_input2_cds").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="ginfo_Locid_input1_cds").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="ginfo_mLocid_input2_cds").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)
    con=st.container(border=True)
    seq_input=con.text_area("Enter the Sequence: ", placeholder="e.g., ATGC...", key="primer_Seq_input1", height=100).strip()

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="ginfo_Searchbutton1")

    if start_button:
        if tid:
            match = df[df["Transcript id"] == tid]
            if not match.empty:
                cds_seq = match["Cds Sequence"].values[0]
                if pd.notna(cds_seq) and cds_seq.strip():
                    temp_id = cds_seq
                    con=st.container(border=True)
                    with con:
                        st.subheader("Primer Design")
                        with st.spinner("Designing Primer...", show_time=True):
                            rid = run_blast_and_get_primer(temp_id)
                            if rid:
                                st.success(f"JOB ID obtained: `{rid}`")
                                result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={rid}"

                                st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                            else:
                                st.error("Failed to obtain JOB ID. Please try again.")
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
                        st.subheader("Primer Design")
                        if pd.notna(cds_seq) and cds_seq.strip():
                            var_name = f"temp_multi_id{counter}"
                            temp_vars[var_name] = cds_seq
                            with st.spinner(f"Designing Primer for {gene_id}...", show_time=True):
                                rid = run_blast_and_get_primer(cds_seq)
                                if rid:
                                    result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={rid}"
                                    with st.expander(f"Primer Design Result for {gene_id} (JOB ID: {rid})", expanded=True):
                                        st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                                else:
                                    st.warning(f"Primer Design failed or no JOB ID returned for Gene ID: {gene_id}")
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
                        st.subheader("Primer Design")
                        with st.spinner("Designing Primer...", show_time=True):
                            rid = run_blast_and_get_primer(temp_id)
                            if rid:
                                st.success(f"JOB ID obtained: `{rid}`")
                                result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={rid}"

                                st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                            else:
                                st.error("Failed to obtain JOB ID. Please try again.")
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
                                rid = run_blast_and_get_primer(cds_seq)

                                if rid:
                                    st.success(f"JOB ID obtained for {loc}: `{rid}`")
                                    result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={rid}"
                                    with st.expander(f"Designing Primer for {loc} (JOB ID: {rid})", expanded=True):
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
                st.warning(f"Primer Design failed or no JOB ID returned for NCBI ID(s): {', '.join(failed_blast)}")
        
        # CASE 5: Direct Sequence Input
        if seq_input:
            temp_id = seq_input
            con=st.container(border=True)
            with con:
                st.subheader("Primer Design")
                with st.spinner("Designing Primer...", show_time=True):
                    rid = run_blast_and_get_primer(temp_id)
                    if rid:
                        st.success(f"JOB ID obtained: `{rid}`")
                        result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={rid}"

                        st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                    else:
                        st.error("Failed to obtain JOB ID. Please try again.")

    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")
    return

def primer_info_page():
    header_styled("PRIMER Designing for Gene Cloning and Expression Analysis", "Enter the Gene ID or NCBI ID to fetch the target sequence and then paste the nucleotide sequence in the Primer design Template section and get the set of primers just clicking Pick primers.")
    if 'active_primer' not in st.session_state:
        st.session_state.active_primer = 'Cloning'
    
    def set_active_primer(tab_name):
        st.session_state.active_primer = tab_name

    c2,col1,c3 ,col2, col4 = st.columns([1,4,1,4,1])
    if col1.button("Cloning", key="btn_loning",use_container_width=True):
        set_active_primer('Cloning')
        st.rerun()
    if col2.button("qRT-PCR", key="btn_qrt",use_container_width=True):
        set_active_primer('QRT')
        st.rerun()
    
    if st.session_state.active_primer == "Cloning":
        primer_cloning()
    elif st.session_state.active_primer == "QRT":
        primer_qrt()

    base_footer()
    return

if __name__ == "__main__":
    primer_info_page()