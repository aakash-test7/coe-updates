import streamlit as st
import pandas as pd
from backend import process_locid, process_mlocid, mlocid_error,header_styled,df,tf_df
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
            return True
        else:
            st.write("No matches found in Transcription Factor data for the given Gene IDs.")
            return False
def tf_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container()
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="tf_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="tf_mTid_input2").strip()

    with col2:
        con2 = st.container()
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="tf_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="tf_mLocid_input2").strip()

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="tf_Searchbutton1")

    if start_button:
        if tid:
            st.subheader("Transcription Factor Information")
            show_tf_info(tid, is_multi=False)
            with st.expander("Transcription Factors", expanded=True):
                st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://planttfdb.gao-lab.org/index.php?sp=Car" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)

        elif mtid:
            mtid_list = [tid.strip() for tid in mtid.replace(",", " ").split()]
            st.subheader("Transcription Factor Information")
            show_tf_info(mtid_list, is_multi=True)
            with st.expander("Transcription Factors", expanded=True):
                st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://planttfdb.gao-lab.org/index.php?sp=Car" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)


        elif locid:
            tid = process_locid(locid)
            if tid:
                st.subheader("Transcription Factor Information")
                show_tf_info(tid, is_multi=False)
                with st.expander("Transcription Factors", expanded=True):
                    st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://planttfdb.gao-lab.org/index.php?sp=Car" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)


        elif mlocid:
            available, rejected = mlocid_error(mlocid)
            if available:
                mtid = process_mlocid(",".join(available))
                mtid_list = [x.strip() for x in mtid.replace(",", " ").split()]
                st.subheader("Transcription Factor Information")
                show_tf_info(mtid_list, is_multi=True)
                with st.expander("Transcription Factors", expanded=True):
                    st.markdown("""<div style='display: flex; justify-content: center;'><iframe src="https://planttfdb.gao-lab.org/index.php?sp=Car" width="1000" height="700" style="border:none;"></iframe></div>""", unsafe_allow_html=True)


        st.toast("Task completed successfully.")
    else:
        st.write("Press the 'Search' button to begin ...")

    base_footer()
    return

if __name__ == "__main__":
    tf_info_page()
