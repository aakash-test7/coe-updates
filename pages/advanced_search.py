import streamlit as st
import pandas as pd
from backend import (
    df, protein_df, process_tid, process_locid,
    show_sequence_data, show_biochemical_properties, show_protein_ppi_data,
    show_cellular_Localization, show_go_kegg_data, show_fpkm_matrix,
    show_df28_matrix, show_pfam_matrix, show_snp_data, show_rna_data,
    show_lncrna_data, show_mirna_data, show_tf_info, show_orthologs_data,
    show_inparalogs_data, show_fpkm_log2, show_df28_log2,
    create_comparison_chart, create_comparison_chart_log2,
    run_blast_and_get_rid, run_gsds, run_blast_and_get_primer, show_sequence_data_p,
    header_styled, pfam_df, GO_df, cello_df, combined_data
)

# Available functions/operations
AVAILABLE_OPERATIONS = {
    "Sequence Data": show_sequence_data,
    "Biochemical Properties": show_biochemical_properties,
    "Protein-Protein Interaction (PPI)": show_protein_ppi_data,
    "Cellular Localization": show_cellular_Localization,
    "GO-KEGG Analysis": show_go_kegg_data,
    "FPKM Matrix": show_fpkm_matrix,
    "FPKM Log2 Transformed": show_fpkm_log2,
    "28 Tissues Matrix": show_df28_matrix,
    "28 Tissues Log2": show_df28_log2,
    "FPKM Comparison Chart": create_comparison_chart,
    "FPKM Log2 Comparison Chart": create_comparison_chart_log2,
    "Pfam Domain": show_pfam_matrix,
    "SNP Calling": show_snp_data,
    "mRNA Data": show_rna_data,
    "lncRNA Data": show_lncrna_data,
    "miRNA Target": show_mirna_data,
    "Transcription Factor": show_tf_info,
    "Orthologs": show_orthologs_data,
    "Paralogs": show_inparalogs_data,
    "BLAST": "blast",  # Special handling
    "Gene Structure (GSDS)": "gsds",  # Special handling
    "Primer Design (Cloning)": "primer_cloning",  # Special handling
    "Primer Design (qRT-PCR)": "primer_qrt",  # Special handling
    "CRISPR Design": "crispr",  # Special handling
}

def convert_to_transcript_ids(input_ids, id_type):
    """Convert LOC IDs to Transcript IDs if needed"""
    transcript_ids = []
    not_found = []
    
    id_list = [item.strip() for item in input_ids.replace(",", " ").split() if item.strip()]
    
    for gene_id in id_list:
        if id_type == "Transcript ID (Ca_XXXXX)":
            # Already transcript ID
            if gene_id in df['Transcript id'].values:
                transcript_ids.append(gene_id)
            else:
                not_found.append(gene_id)
        else:  # LOC ID
            # Convert LOC ID to Transcript ID
            tid = process_locid(gene_id, show_output=False)
            if tid:
                transcript_ids.append(tid)
            else:
                not_found.append(gene_id)
    
    return transcript_ids, not_found

def search_by_pfam(search_terms):
    """
    Search Pfam dataframe by Pfam ID, Pfam Domain, or Pfam name
    Returns list of unique Transcript IDs and matching info
    """
    transcript_ids = set()
    matches_info = []
    
    # Split search terms
    terms = [term.strip() for term in search_terms.replace(",", " ").split() if term.strip()]
    
    for term in terms:
        # Search across Pfam ID, Pfam Domain, and Pfam name columns
        term_lower = term.lower()
        
        # Case-insensitive search in all relevant columns
        matches = pfam_df[
            (pfam_df['Pfam ID'].astype(str).str.lower().str.contains(term_lower, na=False)) |
            (pfam_df['Pfam Domain'].astype(str).str.lower().str.contains(term_lower, na=False)) |
            (pfam_df['Pfam name'].astype(str).str.lower().str.contains(term_lower, na=False))
        ]
        
        if not matches.empty:
            found_ids = matches['Transcript id'].unique().tolist()
            transcript_ids.update(found_ids)
            matches_info.append({
                'term': term,
                'count': len(found_ids),
                'found_ids': found_ids,  # Store the actual IDs
                'sample_matches': matches[['Pfam ID', 'Pfam Domain', 'Pfam name']].drop_duplicates().head(3).to_dict('records')
            })
    
    return list(transcript_ids), matches_info

def search_by_go_kegg(search_terms):
    """
    Search GO_df by Gene symbol or Short description
    Returns list of unique Transcript IDs and matching info
    """
    transcript_ids = set()
    matches_info = []
    
    # Split search terms
    terms = [term.strip() for term in search_terms.replace(",", " ").split() if term.strip()]
    
    for term in terms:
        # Search in both Gene symbol and Short description
        term_lower = term.lower()
        
        # Case-insensitive search
        matches = GO_df[
            (GO_df['Gene symbol'].astype(str).str.lower().str.contains(term_lower, na=False)) |
            (GO_df['Short description'].astype(str).str.lower().str.contains(term_lower, na=False))
        ]
        
        if not matches.empty:
            found_ids = matches['Transcript id'].unique().tolist()
            transcript_ids.update(found_ids)
            matches_info.append({
                'term': term,
                'count': len(found_ids),
                'found_ids': found_ids,  # Store the actual IDs
                'sample_matches': matches[['Gene symbol', 'Short description']].drop_duplicates().head(3).to_dict('records')
            })
    
    return list(transcript_ids), matches_info

def search_by_localization(selected_locations):
    """
    Search cello_df by Most-likely-Location
    Returns list of unique Transcript IDs and matching info
    """
    transcript_ids = set()
    matches_info = []
    
    for location in selected_locations:
        # Search in #Most-likely-Location column
        matches = cello_df[
            cello_df['#Most-likely-Location'].astype(str).str.strip() == location
        ]
        
        if not matches.empty:
            found_ids = matches['Transcript id'].unique().tolist()
            transcript_ids.update(found_ids)
            matches_info.append({
                'term': location,
                'count': len(found_ids),
                'found_ids': found_ids,
                'sample_matches': matches[['Transcript id', '#Most-likely-Location']].head(3).to_dict('records')
            })
    
    return list(transcript_ids), matches_info

def search_by_ml_prediction(selected_predictions):
    """
    Search combined_data by ML model predictions in Resultant column
    Returns list of unique Transcript IDs and matching info
    """
    transcript_ids = set()
    matches_info = []
    
    for prediction in selected_predictions:
        # Search for genes where Resultant contains the prediction
        # Handle both single predictions and comma-separated multiple predictions
        matches = combined_data[
            combined_data['Resultant'].astype(str).str.contains(prediction, case=False, na=False)
        ]
        
        if not matches.empty:
            found_ids = matches['Transcript id'].unique().tolist()
            transcript_ids.update(found_ids)
            matches_info.append({
                'term': prediction,
                'count': len(found_ids),
                'found_ids': found_ids,
                'sample_matches': matches[['Transcript id', 'Resultant', 'Total Difference']].head(3).to_dict('records')
            })
    
    return list(transcript_ids), matches_info

def get_transcript_ids_from_dataframe(data, id_column='Transcript id'):
    """Extract unique transcript IDs from a result dataframe"""
    if isinstance(data, pd.DataFrame):
        if id_column in data.columns:
            return set(data[id_column].unique())
        elif 'Transcript id' in data.columns:
            return set(data['Transcript id'].unique())
    return set()

def handle_blast_operation(transcript_ids):
    """Handle BLAST operation for transcript IDs"""
    for tid in transcript_ids:
        match = df[df["Transcript id"] == tid]
        if not match.empty:
            cds_seq = match["Cds Sequence"].values[0]
            if pd.notna(cds_seq) and cds_seq.strip():
                st.subheader(f"BLAST Results for {tid}")
                with st.spinner(f"Running BLAST for {tid}..."):
                    rid = run_blast_and_get_rid(cds_seq)
                    if rid:
                        st.success(f"RID obtained: `{rid}`")
                        result_url = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID={rid}"
                        with st.expander(f"BLAST Result for {tid}", expanded=(len(transcript_ids) == 1)):
                            st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                    else:
                        st.error(f"Failed to obtain RID for {tid}")
            else:
                st.warning(f"No CDS sequence available for {tid}")
        else:
            st.error(f"Transcript ID {tid} not found in database")

def handle_gsds_operation(transcript_ids):
    """Handle Gene Structure (GSDS) operation for transcript IDs"""
    for tid in transcript_ids:
        match = df[df["Transcript id"] == tid]
        if not match.empty:
            cds_seq = match["Cds Sequence"].values[0]
            gen_seq = match["Genomic Sequence"].values[0]
            if pd.notna(cds_seq) and cds_seq.strip() and pd.notna(gen_seq) and gen_seq.strip():
                temp_cds = f">{tid}\n{cds_seq}"
                temp_genomic = f">{tid}\n{gen_seq}"
                st.subheader(f"Gene Structure for {tid}")
                with st.spinner(f"Running GSDS for {tid}..."):
                    result_url = run_gsds(temp_cds, temp_genomic)
                    if result_url:
                        with st.expander(f"GSDS Result for {tid}", expanded=(len(transcript_ids) == 1)):
                            st.components.v1.iframe(src=result_url, height=800, scrolling=True)
                    else:
                        st.error(f"Failed to obtain GSDS results for {tid}")
            else:
                st.warning(f"No sequence data available for {tid}")
        else:
            st.error(f"Transcript ID {tid} not found in database")

def handle_primer_cloning_operation(transcript_ids):
    """Handle Primer Design (Cloning) operation for transcript IDs"""
    st.subheader("Genomic Sequences for Primer Design (Cloning)")
    show_sequence_data_p(transcript_ids if len(transcript_ids) > 1 else transcript_ids[0], 
                        is_multi=(len(transcript_ids) > 1))
    
    with st.expander("Primer3Plus Design Tool", expanded=True):
        st.info("Copy the genomic sequence above and paste it into the Primer3Plus tool below")
        st.markdown("""<div style='display: flex; justify-content: center;'>
                    <iframe src="https://www.primer3plus.com/" width="100%" height="700" style="border:none;"></iframe>
                    </div>""", unsafe_allow_html=True)

def handle_primer_qrt_operation(transcript_ids):
    """Handle Primer Design (qRT-PCR) operation for transcript IDs"""
    for tid in transcript_ids:
        match = df[df["Transcript id"] == tid]
        if not match.empty:
            cds_seq = match["Cds Sequence"].values[0]
            if pd.notna(cds_seq) and cds_seq.strip():
                st.subheader(f"Primer Design (qRT-PCR) for {tid}")
                with st.spinner(f"Designing primers for {tid}..."):
                    job_id = run_blast_and_get_primer(cds_seq)
                    if job_id:
                        st.success(f"JOB ID obtained: `{job_id}`")
                        result_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={job_id}"
                        with st.expander(f"Primer Design Result for {tid}", expanded=(len(transcript_ids) == 1)):
                            st.components.v1.iframe(src=result_url, height=1000, scrolling=True)
                    else:
                        st.error(f"Failed to obtain JOB ID for {tid}")
            else:
                st.warning(f"No CDS sequence available for {tid}")
        else:
            st.error(f"Transcript ID {tid} not found in database")

def handle_crispr_operation(transcript_ids):
    """Handle CRISPR Design operation for transcript IDs"""
    st.subheader("Genomic Sequences for CRISPR Design")
    show_sequence_data_p(transcript_ids if len(transcript_ids) > 1 else transcript_ids[0], 
                        is_multi=(len(transcript_ids) > 1))
    
    with st.expander("CHOPCHOP CRISPR Design Tool", expanded=True):
        st.info("Copy the genomic sequence above and paste it into the CHOPCHOP tool below")
        st.markdown("""<div style='display: flex; justify-content: center;'>
                    <iframe src="https://chopchop.cbu.uib.no/#" height="800" width="100%" style="border:none;"></iframe>
                    </div>""", unsafe_allow_html=True)

def execute_operation(transcript_ids, operation_name):
    """Execute the selected operation on transcript IDs"""
    operation_func = AVAILABLE_OPERATIONS[operation_name]
    
    # Handle special operations (BLAST, GSDS, Primer, CRISPR)
    if operation_func == "blast":
        handle_blast_operation(transcript_ids)
        return None
    elif operation_func == "gsds":
        handle_gsds_operation(transcript_ids)
        return None
    elif operation_func == "primer_cloning":
        handle_primer_cloning_operation(transcript_ids)
        return None
    elif operation_func == "primer_qrt":
        handle_primer_qrt_operation(transcript_ids)
        return None
    elif operation_func == "crispr":
        handle_crispr_operation(transcript_ids)
        return None
    
    # Handle regular operations
    is_multi = len(transcript_ids) > 1
    
    # Handle special cases for functions with different parameters
    if operation_name in ["28 Tissues Matrix", "28 Tissues Log2", "Pfam Domain"]:
        return operation_func(transcript_ids if is_multi else transcript_ids[0], 
                            is_multi=is_multi, by_tid=True)
    elif operation_name in ["FPKM Comparison Chart", "FPKM Log2 Comparison Chart"]:
        return operation_func(transcript_ids, is_multi=True)
    elif operation_name in ["FPKM Log2 Transformed", "28 Tissues Log2"]:
        return operation_func(transcript_ids if is_multi else transcript_ids[0], 
                            is_multi=is_multi)
    else:
        return operation_func(transcript_ids if is_multi else transcript_ids[0], 
                            is_multi=is_multi)

def perform_set_operation(set_a, set_b, operation):
    """Perform set operations on transcript ID sets"""
    if operation == "Union (A ∪ B)":
        return set_a.union(set_b)
    elif operation == "Intersection (A ∩ B)":
        return set_a.intersection(set_b)
    elif operation == "Difference (A - B)":
        return set_a.difference(set_b)
    elif operation == "Difference (B - A)":
        return set_b.difference(set_a)
    elif operation == "Symmetric Difference (A △ B)":
        return set_a.symmetric_difference(set_b)
    return set()

#st.set_page_config(page_title="Advanced Search Strategy", layout="wide")
def advanced_search():
    # Initialize session state for search queries (MUST be at the top of the function)
    if 'search_queries' not in st.session_state:
        st.session_state.search_queries = []

    if 'result_cache' not in st.session_state:
        st.session_state.result_cache = {}
    
    if 'pending_combined_result' not in st.session_state:
        st.session_state.pending_combined_result = None
    
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    
    # Show "Back to Home" button if navigation was programmatic
    
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_snp", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.rerun()

    header_styled("Query Search","description")

    # ============= UI =============
    #st.title("Advanced Multi-Query Search Strategy")

    #st.markdown("""
    #### How to Use:
    #1. **Add Search Queries**: Enter Gene IDs (Transcript ID or LOC ID) and select the operation you want to perform
    #2. **Execute Searches**: Each search will be stored with a unique label (Query A, B, C, etc.)
    #3. **Combine Results**: Use set operations (Union, Intersection, Difference) to combine multiple query results
    #4. **Chain Operations**: Continue adding more searches and combinations as needed
    #""")
    #st.markdown("---")
    with st.expander("Tutorial",expanded=False):
        st.video("https://youtu.be/wkvhZbtgfvY")
    # ============= Add New Search Query =============
    st.header("Add New Search Query")
    
    # Search Type Selection at the top
    st.subheader("Step 1: Select Search Type")
    search_type = st.radio(
        "Choose your search method",
        ["Direct ID Search", "Pfam Domain Search", "Gene Symbol/Description Search", "Cellular Localization Search", "ML Model Prediction Search"],
        horizontal=False,
        key="search_type",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.subheader("Step 2: Configure Search Parameters")
    
    con=st.container(border=True)
    
    if search_type == "Direct ID Search":
        # Original direct ID search with cleaner layout
        col1, col2 = con.columns(2)

        with col1:
            input_ids = st.text_area(
                "Enter Gene IDs",
                placeholder="Ca_00001, Ca_00002 or LOC101511858, ARF1",
                height=132,
                key="input_ids",
                help="Enter gene IDs separated by comma or space"
            )

        with col2:
            id_type = st.radio(
                "ID Type",
                ["Transcript ID (Ca_XXXXX)", "LOC ID"],
                key="id_type"
            )
            
            operation = st.selectbox(
                "Operation",
                list(AVAILABLE_OPERATIONS.keys()),
                key="operation"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,2,1])
        if c2.button("Add Search Query", type="primary", use_container_width=True, key="add_direct_search"):
            if input_ids.strip():
                transcript_ids, not_found = convert_to_transcript_ids(input_ids, id_type)
                
                if transcript_ids:
                    query_label = f"Query {chr(65 + len(st.session_state.search_queries))}"  # A, B, C, etc.
                    
                    st.session_state.search_queries.append({
                        'label': query_label,
                        'input_ids': input_ids,
                        'id_type': id_type,
                        'transcript_ids': transcript_ids,
                        'operation': operation,
                        'not_found': not_found,
                        'search_type': 'Direct ID'
                    })
                    
                    st.success(f"Added {query_label}: {len(transcript_ids)} transcript ID(s) with operation '{operation}'")
                    
                    if not_found:
                        st.warning(f"Not found: {', '.join(not_found)}")
                else:
                    st.error("No valid transcript IDs found!")
            else:
                st.error("Please enter at least one Gene ID!")
    
    elif search_type == "Pfam Domain Search":
        # Pfam domain search with cleaner layout
        col1, col2 = con.columns(2)
        
        with col1:
            pfam_search = st.text_input(
                "Enter Pfam Search Terms",
                placeholder="PF03372, Exo_endo_phos, Endonuclease",
                key="pfam_search",
                help="Search by Pfam ID, Domain, or Name"
            )
            st.caption("Searches across Pfam ID, Pfam Domain, and Pfam name columns")
        
        with col2:
            operation = st.selectbox(
                "Operation",
                list(AVAILABLE_OPERATIONS.keys()),
                key="operation_pfam"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,2,1])
        if c2.button("Search & Add Query", type="primary", use_container_width=True, key="pfam_search_btn"):
            if pfam_search.strip():
                with st.spinner("Searching Pfam database..."):
                    transcript_ids, matches_info = search_by_pfam(pfam_search)
                
                if transcript_ids:
                    query_label = f"Query {chr(65 + len(st.session_state.search_queries))}"
                    
                    st.session_state.search_queries.append({
                        'label': query_label,
                        'input_ids': pfam_search,
                        'id_type': 'Pfam Search',
                        'transcript_ids': transcript_ids,
                        'operation': operation,
                        'not_found': [],
                        'search_type': 'Pfam Domain',
                        'matches_info': matches_info
                    })
                    
                    st.success(f"Added {query_label}: Found {len(transcript_ids)} transcript IDs with operation '{operation}'")
                    
                    # Show match details
                    #with st.expander("Search Results Details", expanded=True):
                    #    for info in matches_info:
                    #        st.write(f"**Term: '{info['term']}'** - {info['count']} genes found")
                    #        for match in info['sample_matches']:
                    #            st.text(f"  • {match.get('Pfam ID', 'N/A')} | {match.get('Pfam Domain', 'N/A')} | {match.get('Pfam name', 'N/A')}")
                else:
                    st.error("No matching genes found for the search terms!")
            else:
                st.error("Please enter at least one search term!")
    
    elif search_type == "Gene Symbol/Description Search":
        # GO-KEGG search with cleaner layout
        col1, col2 = con.columns(2)
        
        with col1:
            go_search = st.text_input(
                "Enter Gene Symbol or Description",
                placeholder="ARF, auxin, kinase, receptor",
                key="go_search",
                help="Search by gene symbol or description keywords"
            )
            st.caption("Searches across Gene Symbol and Short Description columns")
        
        with col2:
            operation = st.selectbox(
                "Operation",
                list(AVAILABLE_OPERATIONS.keys()),
                key="operation_go"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,2,1])
        if c2.button("Search & Add Query", type="primary", use_container_width=True, key="go_search_btn"):
            if go_search.strip():
                with st.spinner("Searching GO-KEGG database..."):
                    transcript_ids, matches_info = search_by_go_kegg(go_search)
                
                if transcript_ids:
                    query_label = f"Query {chr(65 + len(st.session_state.search_queries))}"
                    
                    st.session_state.search_queries.append({
                        'label': query_label,
                        'input_ids': go_search,
                        'id_type': 'GO-KEGG Search',
                        'transcript_ids': transcript_ids,
                        'operation': operation,
                        'not_found': [],
                        'search_type': 'Gene Symbol/Description',
                        'matches_info': matches_info
                    })
                    
                    st.success(f"Added {query_label}: Found {len(transcript_ids)} transcript IDs with operation '{operation}'")
                    
                    # Show match details
                    #with st.expander("Search Results Details", expanded=True):
                    #    for info in matches_info:
                    #        st.write(f"**Term: '{info['term']}'** - {info['count']} genes found")
                    #        for match in info['sample_matches']:
                    #            st.text(f"  • {match.get('Gene symbol', 'N/A')} | {match.get('Short description', 'N/A')}")
                else:
                    st.error("No matching genes found for the search terms!")
            else:
                st.error("Please enter at least one search term!")
    
    elif search_type == "Cellular Localization Search":
        # Cellular localization search with cleaner layout
        col1, col2 = con.columns(2)
        
        # Define available localization options
        localization_options = [
            "Extracellular",
            "Plasma membrane",
            "Cytoplasmic",
            "Cytoskeletal",
            "ER",
            "Golgi",
            "Lysosomal",
            "Mitochondrial",
            "Chloroplast",
            "Peroxisomal",
            "Vacuole",
            "Nuclear"
        ]
        
        with col1:
            selected_locations = st.multiselect(
                "Select Cellular Locations",
                options=localization_options,
                placeholder="Choose one or more locations",
                key="localization_search",
                help="Select multiple cellular compartments to search"
            )
            st.caption("Searches genes by their most-likely cellular location")
        
        with col2:
            operation = st.selectbox(
                "Operation",
                list(AVAILABLE_OPERATIONS.keys()),
                key="operation_localization"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,2,1])
        if c2.button("Search & Add Query", type="primary", use_container_width=True, key="localization_search_btn"):
            if selected_locations:
                with st.spinner("Searching cellular localization database..."):
                    transcript_ids, matches_info = search_by_localization(selected_locations)
                
                if transcript_ids:
                    query_label = f"Query {chr(65 + len(st.session_state.search_queries))}"
                    
                    # Create input display string
                    input_display = ", ".join(selected_locations)
                    
                    st.session_state.search_queries.append({
                        'label': query_label,
                        'input_ids': input_display,
                        'id_type': 'Localization Search',
                        'transcript_ids': transcript_ids,
                        'operation': operation,
                        'not_found': [],
                        'search_type': 'Cellular Localization',
                        'matches_info': matches_info
                    })
                    
                    st.success(f"Added {query_label}: Found {len(transcript_ids)} transcript IDs with operation '{operation}'")
                    
                    # Show match details
                    #with st.expander("Search Results Details", expanded=True):
                    #    for info in matches_info:
                    #        st.write(f"**Location: '{info['term']}'** - {info['count']} genes found")
                    #        if 'found_ids' in info and info['found_ids']:
                    #            # Show first 5 sample IDs
                    #            sample_ids = info['found_ids'][:5]
                    #            st.text(f"  Sample IDs: {', '.join(sample_ids)}")
                    #            if len(info['found_ids']) > 5:
                    #                st.caption(f"  ... and {len(info['found_ids']) - 5} more")
                else:
                    st.error("No genes found for the selected locations!")
            else:
                st.error("Please select at least one cellular location!")
    
    else:  # ML Model Prediction Search
        # ML model prediction search with cleaner layout
        col1, col2 = con.columns(2)
        
        # Define available ML prediction options
        ml_prediction_options = [
            "ST - Seed Tissue",
            "FP - Flower Parts",
            "FDS - Flower Developmental Stages",
            "GT - Green Tissue",
            "RT - Root Tissue"
        ]
        
        with col1:
            selected_predictions = st.multiselect(
                "Select ML Model Predictions",
                options=ml_prediction_options,
                placeholder="Choose one or more tissue predictions",
                key="ml_prediction_search",
                help="Select tissue types based on ML predictions"
            )
            st.caption("Searches genes by their ML-predicted tissue expression patterns")
        
        with col2:
            operation = st.selectbox(
                "Operation",
                list(AVAILABLE_OPERATIONS.keys()),
                key="operation_ml"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,2,1])
        if c2.button("Search & Add Query", type="primary", use_container_width=True, key="ml_search_btn"):
            if selected_predictions:
                # Extract short codes (ST, FP, FDS, GT, RT) from selections
                prediction_codes = [pred.split(" - ")[0] for pred in selected_predictions]
                
                with st.spinner("Searching ML prediction database..."):
                    transcript_ids, matches_info = search_by_ml_prediction(prediction_codes)
                
                if transcript_ids:
                    query_label = f"Query {chr(65 + len(st.session_state.search_queries))}"
                    
                    # Create input display string
                    input_display = ", ".join(selected_predictions)
                    
                    st.session_state.search_queries.append({
                        'label': query_label,
                        'input_ids': input_display,
                        'id_type': 'ML Prediction Search',
                        'transcript_ids': transcript_ids,
                        'operation': operation,
                        'not_found': [],
                        'search_type': 'ML Model Prediction',
                        'matches_info': matches_info
                    })
                    
                    st.success(f"Added {query_label}: Found {len(transcript_ids)} transcript IDs with operation '{operation}'")
                    
                    # Show match details
                    #with st.expander("Search Results Details", expanded=True):
                    #    for info in matches_info:
                    #        st.write(f"**Prediction: '{info['term']}'** - {info['count']} genes found")
                    #        if 'found_ids' in info and info['found_ids']:
                    #            # Show first 5 sample IDs
                    #            sample_ids = info['found_ids'][:5]
                    #            st.text(f"  Sample IDs: {', '.join(sample_ids)}")
                    #            if len(info['found_ids']) > 5:
                    #                st.caption(f"  ... and {len(info['found_ids']) - 5} more")
                else:
                    st.error("No genes found for the selected ML predictions!")
            else:
                st.error("Please select at least one ML prediction!")

    # ============= Display Current Search Queries =============
    if st.session_state.search_queries:
        st.markdown("---")
        st.header("Current Search Queries")
        
        for i, query in enumerate(st.session_state.search_queries):
            # Check if this query came from a set operation
            is_combined = 'source' in query
            search_type_icon = " "
            if query.get('search_type') == 'Pfam Domain':
                search_type_icon = " "
            elif query.get('search_type') == 'Gene Symbol/Description':
                search_type_icon = " "
            elif query.get('search_type') == 'Cellular Localization':
                search_type_icon = " "
            elif query.get('search_type') == 'ML Model Prediction':
                search_type_icon = " "
            
            with st.expander(f"{query['label']}: {query['operation']}" + (" 🔗" if is_combined else "") + search_type_icon, expanded=True):
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.write(f"**Search Type:** {query.get('search_type', 'Direct ID')}")
                    st.write(f"**Input:** {query['input_ids'][:100]}{'...' if len(query['input_ids']) > 100 else ''}")
                    st.write(f"**ID Type:** {query['id_type']}")
                    st.write(f"**Transcript IDs:** {', '.join(query['transcript_ids'][:5])}{'...' if len(query['transcript_ids']) > 5 else ''}")
                    st.write(f"**Count:** {len(query['transcript_ids'])} genes")
                    
                    # Show search results if available
                    if 'matches_info' in query and query['matches_info']:
                        with st.expander("Search Details", expanded=False):
                            for info in query['matches_info']:
                                st.write(f"**Term: '{info['term']}'** - {info['count']} genes found")
                                
                                # Display the Transcript IDs
                                if 'found_ids' in info and info['found_ids']:
                                    ids_to_show = info['found_ids'][:20]  # Show first 20 IDs
                                    st.text(f"IDs: {', '.join(ids_to_show)}")
                                    if len(info['found_ids']) > 20:
                                        st.caption(f"... and {len(info['found_ids']) - 20} more")
                                st.markdown("---")
                    
                    if is_combined:
                        st.info(f"Source: {query['source']}")
                
                with col2:
                    st.write(f"**Operation:**")
                    st.info(query['operation'])
                
                with col3:
                    if st.button(f"Remove", key=f"remove_{i}",use_container_width=True):
                        st.session_state.search_queries.pop(i)
                        st.rerun()
                    
                    if st.button(f"Execute", key=f"execute_{i}", type="primary", use_container_width=True):
                        st.session_state[f"execute_query_{i}"] = True
                        st.rerun()
                
                # Execute if requested
                if st.session_state.get(f"execute_query_{i}", False):
                    st.markdown("---")
                    st.subheader(f"Results for {query['label']}")
                    
                    with st.spinner(f"Executing {query['operation']}..."):
                        try:
                            result = execute_operation(query['transcript_ids'], query['operation'])
                            
                            # Store transcript IDs for set operations
                            if isinstance(result, pd.DataFrame):
                                query['result_ids'] = get_transcript_ids_from_dataframe(result)
                            else:
                                query['result_ids'] = set(query['transcript_ids'])
                            
                            st.success(f"Execution completed for {query['label']}")
                        except Exception as e:
                            st.error(f"Error executing {query['label']}: {str(e)}")
                    
                    # Reset execution flag
                    st.session_state[f"execute_query_{i}"] = False

        # ============= Clear All Queries =============
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Clear All Queries", type="secondary", use_container_width=True):
                st.session_state.search_queries = []
                st.session_state.result_cache = {}
                st.rerun()

    # ============= Combine Queries with Set Operations =============
    if len(st.session_state.search_queries) >= 2:
        st.markdown("---")
        st.header("Combine Queries with Set Operations")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            query_a_idx = st.selectbox(
                "Select First Query (A)",
                range(len(st.session_state.search_queries)),
                format_func=lambda x: st.session_state.search_queries[x]['label'],
                key="query_a"
            )
        
        with col2:
            set_operation = st.selectbox(
                "Set Operation",
                ["Union (A ∪ B)", "Intersection (A ∩ B)", "Difference (A - B)", 
                "Difference (B - A)", "Symmetric Difference (A △ B)"],
                key="set_op"
            )
        
        with col3:
            query_b_idx = st.selectbox(
                "Select Second Query (B)",
                range(len(st.session_state.search_queries)),
                format_func=lambda x: st.session_state.search_queries[x]['label'],
                key="query_b"
            )
        
        combined_operation = st.selectbox(
            "Select Operation for Combined Result",
            list(AVAILABLE_OPERATIONS.keys()),
            key="combined_operation"
        )
        
        c1,c2,c3,c4,c5=st.columns([1,1,4,1,1])
        if c3.button("Combine and Execute", type="primary", use_container_width=True):
            query_a = st.session_state.search_queries[query_a_idx]
            query_b = st.session_state.search_queries[query_b_idx]
            
            # Get transcript ID sets
            set_a = set(query_a['transcript_ids'])
            set_b = set(query_b['transcript_ids'])
            
            # Perform set operation
            result_set = perform_set_operation(set_a, set_b, set_operation)
            
            if result_set:
                # Store the result for potential saving
                st.session_state.pending_combined_result = {
                    'result_set': list(result_set),
                    'operation': combined_operation,
                    'source': f"{query_a['label']} {set_operation} {query_b['label']}",
                    'set_operation': set_operation
                }
                st.rerun()
            else:
                st.warning("The set operation resulted in an empty set!")
        
        # Display and execute the pending combined result
        if st.session_state.pending_combined_result:
            result_data = st.session_state.pending_combined_result
            result_set = result_data['result_set']
            combined_op = result_data['operation']
            source_info = result_data['source']
            
            st.success(f"{result_data['set_operation']}: Found {len(result_set)} genes")
            
            # Display resulting transcript IDs
            with st.expander("Resulting Transcript IDs", expanded=True):
                st.write(", ".join(sorted(result_set)))
            
            # Execute operation on combined result
            st.subheader(f"Executing '{combined_op}' on Combined Result")
            
            with st.spinner(f"Executing {combined_op}..."):
                try:
                    result = execute_operation(result_set, combined_op)
                    st.success(f"Execution completed!")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            # Always show the "Save as New Query" button after execution
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                save_col1, save_col2 = st.columns([1, 1])
                
                with save_col1:
                    if st.button("Save as New Query", use_container_width=True, type="primary"):
                        new_label = f"Query {chr(65 + len(st.session_state.search_queries))}"
                        st.session_state.search_queries.append({
                            'label': new_label,
                            'input_ids': ', '.join(result_set),
                            'id_type': 'Transcript ID (Ca_XXXXX)',
                            'transcript_ids': result_set,
                            'operation': combined_op,
                            'not_found': [],
                            'source': source_info
                        })
                        st.success(f"Saved as {new_label}")
                        st.session_state.pending_combined_result = None
                        st.rerun()
                
                with save_col2:
                    if st.button("Clear Result", use_container_width=True, type="secondary"):
                        st.session_state.pending_combined_result = None
                        st.rerun()

    # ============= Statistics =============
    if st.session_state.search_queries:
        st.markdown("---")
        st.header("Query Statistics")
        
        total_queries = len(st.session_state.search_queries)
        total_transcript_ids = sum(len(q['transcript_ids']) for q in st.session_state.search_queries)
        unique_transcript_ids = len(set().union(*[set(q['transcript_ids']) for q in st.session_state.search_queries]))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Queries", total_queries)
        col2.metric("Total Transcript IDs", total_transcript_ids)
        col3.metric("Unique Transcript IDs", unique_transcript_ids)
        
        operations_count = {}
        for query in st.session_state.search_queries:
            op = query['operation']
            operations_count[op] = operations_count.get(op, 0) + 1
        
        with st.expander("Operations Breakdown"):
            for op, count in operations_count.items():
                st.write(f"**{op}:** {count} queries")
    return

if __name__ == "__main__":
    advanced_search()

