import streamlit as st
import time
import pandas as pd
from backend import user_input_menu, multi_user_input_menu, process_locid, process_mlocid, header_styled, process_tid, df, prop_df, protein_df, cello_df, GO_df, df_28, pfam_df, miRNA_df, tf_df, orthologs_df, paralogs_df
from pages.footer import base_footer
from pages.security import connect_to_db

if "site_search_input_transcript" not in st.session_state:
    st.session_state["site_search_input_transcript"] = ""
if "site_search_input_loc" not in st.session_state:
    st.session_state["site_search_input_loc"] = ""

def sanitize_input(user_input):
    items = [item.strip() for item in user_input.replace(",", " ").split()]
    items = list(set([item for item in items if item]))
    return items

def check_data_availability(search_terms):
    """Check which data is available for the search terms and return availability flags"""
    availability = {
        'sequence_data': False,
        'biochemical_properties': False,
        'protein_ppi': False,
        'cellular_localization': False,
        'go_kegg': False,
        'fpkm_matrix': False,
        'df28_matrix': False,
        'pfam_matrix': False,
        'rna_data': False,
        'lncrna_data': False,
        'mirna_data': False,
        'transcription_factors': False,
        'orthologs': False,
        'paralogs': False
    }
    
    if isinstance(search_terms, str):
        search_terms = [search_terms]
    
    for term in search_terms:
        seq_match = df[(df['Transcript id'] == term) | (df['LOC ID'] == term)]
        if not seq_match.empty:
            sequence_cols = ['Cds Sequence', 'Peptide Sequence', 'Transcript Sequence', 'Genomic Sequence', 'Promoter Sequence']
            availability['sequence_data'] = any(
                col in seq_match.columns and not seq_match[col].isna().all() and any(seq_match[col].str.len() > 0)
                for col in sequence_cols
            )
            
            availability['fpkm_matrix'] = True
            availability['rna_data'] = 'mRNA' in seq_match.columns and not seq_match['mRNA'].isna().all()
            availability['lncrna_data'] = 'lncRNA' in seq_match.columns and not seq_match['lncRNA'].isna().all()
        
        # Biochemical properties
        prop_match = prop_df[prop_df['Transcript id'] == term]
        if not prop_match.empty:
            prop_cols = ['Total Amino Acids', 'Molecular Weight (Da)', 'Theoretical pI']
            availability['biochemical_properties'] = any(
                col in prop_match.columns and not prop_match[col].isna().all()
                for col in prop_cols
            )
        
        # Protein PPI data
        protein_match = protein_df[(protein_df['Transcript id'] == term) | (protein_df['preferredName'] == term)]
        if not protein_match.empty:
            protein_cols = ['identity', 'bitscore', 'preferredName']
            availability['protein_ppi'] = any(
                col in protein_match.columns and not protein_match[col].isna().all()
                for col in protein_cols
            )
        
        # Cellular localization
        cello_match = cello_df[cello_df['Transcript id'] == term]
        if not cello_match.empty:
            loc_cols = ['Extracellular', 'Plasma membrane', 'Cytoplasmic', 'Nuclear']
            availability['cellular_localization'] = any(
                col in cello_match.columns and not cello_match[col].isna().all()
                for col in loc_cols
            )
        
        # GO KEGG data
        GO_match = GO_df[GO_df['Transcript id'] == term]
        if not GO_match.empty:
            go_cols = ['GO (molecular function)', 'GO (cellular component)', 'KEGG Pathway']
            availability['go_kegg'] = any(
                col in GO_match.columns and not GO_match[col].isna().all()
                for col in go_cols
            )
        
        # DF28 matrix data
        df28_match = df_28[(df_28['Chickpea_Id'] == term) | (df_28['LOC ID'] == term)]
        if not df28_match.empty:
            expr_cols = ['Ger_Coleoptile', 'Rep_Buds', 'Rep_Flower', 'Veg_Leaf']
            availability['df28_matrix'] = any(
                col in df28_match.columns and not df28_match[col].isna().all()
                for col in expr_cols
            )
        
        # Pfam matrix data
        pfam_match = pfam_df[(pfam_df['Transcript id'] == term) | (pfam_df['LOC ID'] == term)]
        if not pfam_match.empty:
            pfam_cols = ['Pfam ID', 'Pfam Domain']
            availability['pfam_matrix'] = any(
                col in pfam_match.columns and not pfam_match[col].isna().all()
                for col in pfam_cols
            )
        
        # miRNA data
        mirna_match = miRNA_df[miRNA_df['Target_Acc.'] == term]
        if not mirna_match.empty:
            mirna_cols = ['Expectation', 'UPE$']
            availability['mirna_data'] = any(
                col in mirna_match.columns and not mirna_match[col].isna().all()
                for col in mirna_cols
            )
        
        # Transcription factors
        tf_match = tf_df[tf_df['Gene_ID'] == term]
        if not tf_match.empty:
            tf_cols = ['Family', 'TF_ID']
            availability['transcription_factors'] = any(
                col in tf_match.columns and not tf_match[col].isna().all()
                for col in tf_cols
            )
        
        if orthologs_df is not None and not orthologs_df.empty:
            def extract_gene_id(species_string):
                if '|' in species_string:
                    return species_string.split('|')[-1]  # Get part after '|'
                return species_string
            
            species_a_ids = orthologs_df['Species A'].astype(str).apply(extract_gene_id)
            species_b_ids = orthologs_df['Species B'].astype(str).apply(extract_gene_id)
            
            ortho_match = orthologs_df[
                (species_a_ids == term) | (species_b_ids == term)
            ]
            if not ortho_match.empty:
                availability['orthologs'] = True

        # Paralogs data - exact matching
        if paralogs_df is not None and not paralogs_df.empty:
            def extract_gene_id(species_string):
                if '|' in species_string:
                    return species_string.split('|')[-1]  # Get part after '|'
                return species_string
            
            species_a_ids = paralogs_df['Species A'].astype(str).apply(extract_gene_id)
            species_b_ids = paralogs_df['Species B'].astype(str).apply(extract_gene_id)
            
            para_match = paralogs_df[
                (species_a_ids == term) | (species_b_ids == term)
            ]
            if not para_match.empty:
                availability['paralogs'] = True
    
    return availability

def get_available_buttons(availability):
    """Return list of available data buttons based on availability flags"""
    buttons = []
    
    button_config = {
        'sequence_data': 'Sequence Data',
        'biochemical_properties': 'Biochemical Properties',
        'protein_ppi': 'Protein PPI',
        'cellular_localization': 'Cellular Localization',
        'go_kegg': 'GO & KEGG',
        'fpkm_matrix': 'FPKM Matrix',
        'df28_matrix': 'Expression Atlas',
        'rna_data': 'mRNA Data',
        'lncrna_data': 'lncRNA Data',
        'mirna_data': 'miRNA Targets',
        'transcription_factors': 'Transcription Factors',
        'orthologs': 'Orthologs',
        'paralogs': 'Paralogs'
    }
    
    for data_type, button_label in button_config.items():
        if availability.get(data_type, False):
            buttons.append(button_label)
    
    return buttons
def display_available_buttons(available_buttons, search_terms, is_multi=False):
    """Display available data buttons in a grid layout"""
    if not available_buttons:
        st.warning("No data found for the provided search terms.")
        return
    
    st.success(f"Found data for following categories:")
    
    if len(available_buttons) >= 2:
        if st.button("Comprehensive Search", use_container_width=True, key="btn_comprehensive_search"):
            st.session_state["programmatic_nav"] = True
            st.session_state["current_page"] = "SEARCH"
            st.rerun()
    
    for i, button_label in enumerate(available_buttons):
        if st.button(button_label, use_container_width=True, key=f"btn_{button_label}"):
            # Map button labels to page names
            page_mapping = {
                'Sequence Data': 'GENE-INFO',
                'Biochemical Properties': 'GENE-INFO', 
                'Protein PPI': 'PPI',
                'Cellular Localization': 'Localization',
                'GO & KEGG': 'GO-KEGG',
                'FPKM Matrix': 'Tissue Specific Expression',
                'Expression Atlas': 'Tissue Specific Expression',
                'mRNA Data': 'RNA-type',
                'lncRNA Data': 'RNA-type',
                'miRNA Targets': 'miRNA-target',
                'Transcription Factors': 'Transcription Factors',
                'Orthologs': 'ORTHOLOGS/PARALOGS',
                'Paralogs': 'ORTHOLOGS/PARALOGS'
            }
            
            page_name = page_mapping.get(button_label, 'SEARCH')  # Default to SEARCH
            
            st.session_state.selected_button = button_label
            st.session_state.search_terms = search_terms
            st.session_state.is_multi = is_multi
            st.session_state["programmatic_nav"] = True
            st.session_state["current_page"] = page_name
            st.rerun()

def process_search_terms(search_terms):
    """Process search terms and convert between Transcript ID and LOC ID if needed"""
    processed_terms = []
    loc_ids = []
    transcript_ids = []
    
    for term in search_terms:
        # Check if it's a Transcript ID (starts with Ca_)
        # Guard: ensure term is a string
        if not isinstance(term, str):
            term = str(term)

        if term.startswith('Ca_'):
            transcript_ids.append(term)
            # Try to find corresponding LOC ID
            loc_id = process_tid(term, df, show_output=False)
            if loc_id:
                loc_ids.append(loc_id)
        # Check if it's likely a LOC ID or other identifier
        else:
            loc_ids.append(term)
            # Try to find corresponding Transcript ID
            transcript_id = process_locid(term, show_output=False)
            if transcript_id:
                transcript_ids.append(transcript_id)
    
    # Clean and deduplicate returned IDs. This avoids mixing floats/NaNs with strings
    def _clean_and_dedupe(id_list):
        cleaned = []
        for x in id_list:
            if x is None:
                continue
            try:
                if pd.isna(x):
                    continue
            except Exception:
                pass
            s = str(x).strip()
            if not s:
                continue
            if s.lower() == 'nan':
                continue
            cleaned.append(s)
        return sorted(list(set(cleaned)))

    transcript_ids = _clean_and_dedupe(transcript_ids)
    loc_ids = _clean_and_dedupe(loc_ids)

    return transcript_ids, loc_ids

def home_page():        
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    l1,l2,l3=st.columns([1,3,1])           
    l2.markdown("""<div style='text-align: center; margin-bottom: -50px;'><h2 style='margin: 0;'>Site Search</h2></div>""",unsafe_allow_html=True)

    home_input=l2.text_input(label=" ",value="",placeholder="Ca_00001, Ca_00002, LOC101511858, LOC101496413 ...",key="search_home_input",help="Search by Phytozome Gene ID or NCBI ID")
    c1,c2,col3=l2.columns([1,3,1])
    home_button_search = c2.button("Search", use_container_width=True, key="home_search_button", type="secondary")
                    
    col1,col2,col3=st.columns([1,3,1])
    with col1:
        con=st.container(border=False, key="con101hp")
        with con:
            if st.button("Browse", use_container_width=True, key="navBrowse", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "GENE-INFO"
                st.rerun()
        con=st.container(border=False, key="con102hp")
        with con:
            #if st.button("Primer Design", use_container_width=True, key="navPrimer", type="primary"):
            #    st.session_state["programmatic_nav"] = True
            #    st.session_state["current_page"] = "PRIMER"
            #    st.rerun()
            if st.button("BLAST", use_container_width=True, key="navBlast", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "BLAST"
                st.rerun()
        con=st.container(border=False, key="con103hp")
        with con:
            if st.button("SNP Calling", use_container_width=True, key="navSNP", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "SNP-CALLING"
                st.rerun()
    
    col2.markdown('''
        <style>
            /* General Styles */
            .hp-body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #f5d7be;
            }
            .hp-container {
                max-width: 100%;
                min-height: 520px;
                max-height: 520px;  /* Original max-height */
                background-color: #833c0d;
                margin: 0 auto;
                padding: 20px;
                overflow-y: auto;
                overflow-x: hidden; /* Disable horizontal scroll */
                border-radius: 1rem;
                transition: all 0.3s ease-in-out !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .hp-container:hover {
                background-color: rgba(197,91,17,1) !important;
                transition: all 0.3s ease-in-out !important;
            }
            /* Paragraph Styles */
            .hp-paragraph {
                font-size: 1rem;
                line-height: 1.6;
                margin-bottom: 20px;
                text-align: justify; /* Text is now justified */
            }
            .hp-paragraph b {
                color: #e74c3c;
                font-weight: bold;
            }
            .hp-paragraph em {
                font-style: italic;
                text-decoration: underline;
            }
            
            /* Media query for small screens */
            @media (max-width: 768px) {
                .hp-container {
                    max-height: none;  /* Remove max-height for small screens */
                    overflow-x: hidden; /* Ensure no horizontal overflow */
                }
            }
        </style>
        <div class="hp-body">
          <div class="hp-container">
            <!-- Heading and Subheading -->
            <p style="text-align: center; font-size: 3rem; margin-bottom: 5px; color: #fff; font-weight: bold;">Chickpea Omics Explorer</p>
            <p style="text-align: center; font-size: 1.2rem; color: #fff; margin-bottom: 10px; font-weight: bold;">CHICKPEA (<i>Cicer arietinum</i> L.) DATABASE</p>
            <!-- Paragraph with List and Special Effects -->
            <br><p class="hp-paragraph">
              Chickpea (<i>Cicer arietinum</i> L.), a major legume valued for its high protein content and predominantly cultivated in arid and semi-arid regions. With the advent of high throughput sequencing technologies, vast amounts of genomic and transcriptomic data have been generated. To effectively utilize this wealth of information, we developed an AI-driven platform, the “CHICKPEA OMICS EXPLORER”. This interactive database integrates multiple genomic resources including Phytozome, NCBI, CicerSeq, and the chickpea transcriptome database. It offers comprehensive tools for spatial-temporal gene expression profiling, motif discovery, RNA coding potential analysis, protein interaction networks, pathway enrichment analysis, SNP detection, and ortholog identification. By consolidating diverse datasets and analysis, the Chickpea Omics Explorer serves as a powerful resource for trait dissection, molecular breeding, and functional genomics research in chickpea.
            </p>
          </div>
        </div>
    ''', unsafe_allow_html=True)
    with col3:
        con=st.container(border=False, key="con04hp")
        with con:
            if st.button("Query Search", use_container_width=True, key="navQuery", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "QUERY"
                st.rerun()
        con=st.container(border=False, key="con05hp")
        with con:
            if st.button("Gene Structure", use_container_width=True, key="navGSDS", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "GSDS"
                st.rerun()
            #if st.button("Primer Design", use_container_width=True, key="navPrimer", type="primary"):
            #    st.session_state["programmatic_nav"] = True
            #    st.session_state["current_page"] = "PRIMER"
            #    st.rerun()
            
        con=st.container(border=False, key="con06hp")
        with con:
            #if st.button("CRISPR Construct", use_container_width=True, key="navCRISPR", type="primary"):
            #    st.session_state["programmatic_nav"] = True
            #    st.session_state["current_page"] = "CRISPR"
            #    st.rerun()
            if st.button("Tools", use_container_width=True, key="navTools", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "TOOLS"
                st.rerun()
    st.markdown("""
    <style>
        .st-key-search_home_input input {
            background-color: #FCD3AC;
            color: #000 !important;
        }
        .st-key-search_home_input input::placeholder {
            color: #2c2d2d !important;
        }
    [data-testid="stBaseButton-primary"] div[data-testid="stMarkdownContainer"] p {
        font-size: 2.5rem !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        color: #fff !important;  /* Font color */
    }

    /* Container styling for proper centering */
    [data-testid="stBaseButton-primary"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 160px !important;
        background-color: #833c0d !important;  /* Default background color */
        transition: all 0.3s ease-in-out !important;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background-color: rgba(197,91,17,1) !important;  /* Hover background color */
    }
    .st-key-con101hp, .st-key-con04hp {
                margin-top: 0rem;
    }    
    .st-key-con03hp, .st-key-con01hp, .st-key-con02hp,  {
        background-color: #833c0d;
        padding: 20px;
        border-radius: 2rem;
        transition: all 0.3s ease-in-out;
    }
    .st-key-con03hp:hover, .st-key-con01hp:hover, .st-key-con02hp:hover {
        background-color: rgba(197,91,17,1); 
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); 
        outline: none;
        transform: translateY(-2px);
    } 
    </style>""", unsafe_allow_html=True)
    base_footer()
    #if home_button_search:
    if home_input:
        search_terms = sanitize_input(home_input)
        if search_terms:
            ti,li = process_search_terms(search_terms)
            st.session_state["site_search_input_transcript"] = ti
            st.session_state["site_search_input_loc"] = li

            with st.spinner("Checking data availability..."):
                availability = check_data_availability(ti)
            
            is_multi = len(ti) > 1
            available_buttons = get_available_buttons(availability)
            
            with c2.popover("Available Data", use_container_width=True):
                display_available_buttons(available_buttons, ti, is_multi)
    return

def search_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    if st.session_state.get('authenticated', False):
        username = st.session_state.get('username')
    if "first_search_visit" not in st.session_state:
        st.session_state["first_search_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        if st.button("← Back to Home", key="back_to_home_spatial", type="primary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_search_visit"] = True
            st.rerun()
    header_styled("Search", "Users can get detailed genomic information by inserting Phytozome/NCBI gene IDs. The search is case sensitive. For example, entering Ca_00001 will provide detailed information including genomic sequence, transcript sequence, CDS, protein sequence, promoter sequence, biochemical properties, protein-protein interaction, cellular localization, Gene Ontology and KEGG analysis, SNP calling, lncRNA, miRNA targets, transcription factors, orthologs/paralogs, and protein model prediction.")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_search_visit", True):
        con = st.container(border=True)
        st.session_state["first_search_visit"] = False
        if not st.session_state.get("logged_in", False):
            with con:
                st.info("You need to login to perform this action. Redirecting to login page in 5 seconds...")
                time.sleep(5)
                st.session_state["redirect_to_login"] = True
                st.rerun()
        else:
            temp_list = st.session_state.get("site_search_input_transcript")
            temp_list = " ".join(temp_list)
            st.session_state["site_search_input_transcript"] = []
            mtid_list = [item.strip() for item in temp_list.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)
            with con:
                st.subheader("Search Results")
                result = multi_user_input_menu(mtid)
                st.write(result)
            st.toast("Task completed successfully.")

    elif start_button:
        if not st.session_state.get("logged_in", False):
            if tid or mtid or locid or mlocid:
                st.warning("You need to login to perform this action. Redirecting to login page in 5 seconds...")
                time.sleep(5)
                st.session_state["redirect_to_login"] = True
                st.rerun()
        else:
            conn = connect_to_db()
            cursor = conn.cursor()
            if tid:
                if 1 <= len(tid) <= 20:
                    result = user_input_menu(tid)
                    st.write(result)
                    st.toast("Task completed successfully.")
                    query_tid = """
                    INSERT INTO History (Username, tid)
                    VALUES (%s, %s)
                    """
                    cursor.execute(query_tid, (username, tid))
                else:
                    st.warning("Gene ID must be at most 20 characters.")
            elif mtid:
                result = multi_user_input_menu(mtid)
                st.write(result)
                chunk_size = 255
                st.toast("Task completed successfully.")
                query_mtid = """
                INSERT INTO History (Username, mtid)
                VALUES (%s, %s)
                """
                for i in range(0, len(mtid), chunk_size):
                    chunk = mtid[i:i + chunk_size]
                    cursor.execute(query_mtid, (username, chunk))
                
            elif locid:
                if 1 <= len(locid) <= 20:
                    tid = process_locid(locid)
                    result = user_input_menu(tid)
                    st.write(result)
                    st.toast("Task completed successfully.")
                    query_locid = """
                    INSERT INTO History (Username, locid)
                    VALUES (%s, %s)
                    """
                    cursor.execute(query_locid, (username, locid))
                else:
                    st.warning("NCBI ID must be at most 20 characters.")
            elif mlocid:
                mtid = process_mlocid(mlocid)
                result = multi_user_input_menu(mtid)
                st.write(result)
                chunk_size = 255
                st.toast("Task completed successfully.")
                query_mlocid = """
                INSERT INTO History (Username, mlocid)
                VALUES (%s, %s)
                """
                for i in range(0, len(mlocid), chunk_size):
                    chunk = mlocid[i:i + chunk_size]
                    cursor.execute(query_mlocid, (username, chunk))
            else:
                st.warning("Need either a Gene ID or NCBI ID to proceed.")
            conn.commit()
            conn.close()
    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")
    c1,c2,c3,c4=st.columns([2,3,3,2])
    if st.session_state.get('authenticated', False):
        if c2.button("History", key="History_search",use_container_width=True):
            conn2= connect_to_db()
            cursor2= conn2.cursor()
            st.write(f"History for {username} :-")
            cursor2.execute("SELECT * FROM History WHERE Username = %s", (username,))
            rows = cursor2.fetchall()
            column_names = [desc[0] for desc in cursor2.description]
            df = pd.DataFrame(rows, columns=column_names)
            st.dataframe(df)
            conn2.close()
    if st.session_state.get('authenticated', False):
        if c3.button("Logout", key="logout_search",use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.success("You have been logged out successfully!")
            time.sleep(2)
            st.rerun()
    base_footer()
    return

