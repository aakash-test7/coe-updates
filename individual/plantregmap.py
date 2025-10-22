import streamlit as st
import pandas as pd
from backend import process_locid, process_mlocid, mlocid_error, header_styled, df, tf_df
from pages.footer import base_footer

def process_tid(tid, df):
    result = df[df['Transcript id'] == tid]
    if not result.empty:
        loc_id = result.iloc[0]['LOC ID']
        st.write(f"LOC ID for Transcript id {tid} is {loc_id}")
        return loc_id
    else:
        return None

def process_mtid(mtid, df):
    mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
    mtid_list = list(set(mtid_list))  # remove duplicates

    loc_ids = []
    for tid in mtid_list:
        loc_id = process_tid(tid, df)
        if loc_id:
            loc_ids.append(loc_id)

    result = ",".join(loc_ids)
    return result

def show_tf_info(tid, is_multi=False):
    """Display Transcription Factor info for Transcript ID(s) by matching Gene_ID in tf_df."""
    
    # Single input: Process a single Transcript ID
    if not is_multi:
        gene_id = process_tid(tid, df)
        
        if gene_id:  # If Gene ID was found for the given Transcript ID
            tf_matching_row = tf_df[tf_df['Gene_ID'] == gene_id]
            
            if not tf_matching_row.empty:
                st.dataframe(tf_matching_row[['TF_ID', 'Gene_ID', 'Family']])
                
                # Extract TF_ID values to display below with iframe
                tf_ids = tf_matching_row['TF_ID'].tolist()
                
                # Display each TF_ID with iframe
                for tf_id in tf_ids:
                    st.subheader(f"Transcription Factor: {tf_id}")
                    iframe_url = f"https://planttfdb.gao-lab.org/tf.php?sp=Car&did={tf_id}"
                    st.markdown(f"""<div style='display: flex; justify-content: center;'><iframe src="{iframe_url}" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

                st.write("\n")
                return True
            else:
                st.write(f"No match found for Gene ID: {gene_id} in Transcription Factor Data\n")
                return False
        else:
            st.write(f"No Gene ID found for Transcript ID: {tid}")
            return False
    
    # Multiple input: Process multiple Transcript IDs
    else:
        result = pd.DataFrame()
        
        # Process each Transcript ID in the list
        for t_id in tid:
            gene_id = process_tid(t_id, df)
            
            if gene_id:  # If Gene ID was found for the given Transcript ID
                tf_matching_row = tf_df[tf_df['Gene_ID'] == gene_id]
                
                if not tf_matching_row.empty:
                    temp_result = tf_matching_row[['TF_ID', 'Gene_ID', 'Family']]
                    result = pd.concat([result, temp_result], ignore_index=True)
        
        if not result.empty:
            result = result.drop_duplicates(subset=['Gene_ID'])
            st.dataframe(result)
            
            # Extract TF_ID values to display below with iframe
            tf_ids = result['TF_ID'].tolist()
            
            # Display each TF_ID with iframe
            for tf_id in tf_ids:
                st.subheader(f"Transcription Factor: {tf_id}")
                iframe_url = f"https://planttfdb.gao-lab.org/tf.php?sp=Car&did={tf_id}"
                st.markdown(f"""<div style='display: flex; justify-content: center;'><iframe src="{iframe_url}" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

            return True
        else:
            st.write("No matches found in Transcription Factor data for the given Gene IDs.")
            return False

def tf_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_tf", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.rerun()
    
    header_styled("Transcription Factors", "It provides detailed information about transcription factors binding to the selected gene.")
    
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="tf_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="tf_mTid_input2").strip()

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="tf_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="tf_mLocid_input2").strip()

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="tf_Searchbutton1")

    if start_button:
        if tid:
            con=st.container(border=True)
            with con:
                st.subheader("Transcription Factor Information")
                show_tf_info(tid, is_multi=False)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                    st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                    st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

        elif mtid:
            mtid_list = [tid.strip() for tid in mtid.replace(",", " ").split()]
            con=st.container(border=True)
            with con:
                st.subheader("Transcription Factor Information")
                show_tf_info(mtid_list, is_multi=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                    st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                    st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

        elif locid:
            tid = process_locid(locid)
            if tid:
                con=st.container(border=True)
                with con:
                    st.subheader("Transcription Factor Information")
                    show_tf_info(tid, is_multi=False)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                        st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                        st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

        elif mlocid:
            available, rejected = mlocid_error(mlocid)
            if available:
                mtid = process_mlocid(",".join(available))
                mtid_list = [x.strip() for x in mtid.replace(",", " ").split()]
                con=st.container(border=True)
                with con:
                    st.subheader("Transcription Factor Information")
                    show_tf_info(mtid_list, is_multi=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                        st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                        st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

        st.toast("Task completed successfully.")
    else:
        st.write("Press the 'Search' button to begin ...")

    base_footer()

if __name__ == "__main__":
    tf_info_page()
