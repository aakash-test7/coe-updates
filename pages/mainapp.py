import streamlit as st
import time
import pandas as pd
from backend import user_input_menu, multi_user_input_menu, process_locid, process_mlocid, header_styled
from pages.footer import base_footer
from pages.security import connect_to_db

def home_page():        
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col1:
        con=st.container(border=False, key="con101hp")
        with con:
            if st.button("Browse", use_container_width=True, key="navBrowse", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "GENE-INFO"
                st.rerun()
        con=st.container(border=False, key="con102hp")
        with con:
            if st.button("Primer Design", use_container_width=True, key="navPrimer", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "PRIMER"
                st.rerun()
        con=st.container(border=False, key="con103hp")
        with con:
            if st.button("SNP Calling", use_container_width=True, key="navSNP", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "SNP-CALLING"
                st.rerun()
    col2.markdown(''
        '<style>'
        '    /* General Styles */'
        '    .hp-body {'
        '        font-family: Arial, sans-serif;'
        '        margin: 0;'
        '        padding: 0;'
        '        color: #f5d7be;'
        '    }'
        '    .hp-container {'
        '        max-width: 100%;'
        '        min-height: 500px;'
        '        background-color: #833c0d;'
        '        margin: 0 auto;'
        '        padding: 20px;'
        '        border-radius: 1rem;'#2rem
        '        transition: all 0.3s ease-in-out !important;'
        '        box-shadow: 0 4px 8px rgba(0,0,0,0.1);'
        '    }'
        ' .hp-container:hover {'
        '    background-color: rgba(197,91,17,1) !important;'
        '    transition: all 0.3s ease-in-out !important;'
        '}'
        '    /* Paragraph Styles */'
        '    .hp-paragraph {'
        '        font-size: 1rem;'
        '        line-height: 1.6;'
        '        margin-bottom: 20px;'
        '        text-align: justify; /* Text is now justified */'
        '    }'
        '    .hp-paragraph b {'
        '        color: #e74c3c;'
        '        font-weight: bold;'
        '    }'
        '    .hp-paragraph em {'
        '        font-style: italic;'
        '        text-decoration: underline;'
        '    }'
        '</style>'
        '<div class="hp-body">'
        '  <div class="hp-container">'
        '    <!-- Heading and Subheading -->'
        '    <p style="text-align: center; font-size: 3rem; margin-bottom: 5px; color: #fff; font-weight: bold;">Chickpea Omics Explorer</p>'
        '    <p style="text-align: center; font-size: 1.2rem; color: #fff; margin-bottom: 10px; font-weight: bold;">CHICKPEA (<i>Cicer arietinum</i> L.) DATABASE</p>'
        '    <!-- Paragraph with List and Special Effects -->'
        '    <br><p class="hp-paragraph">'
        '      Chickpea (<i>Cicer arietinum</i> L.), a major legume valued for its high protein content and predominantly cultivated in arid and semi-arid regions. With the advent of high throughput sequencing technologies vast amount of genomic and transcriptomic data have been generated. To effectively utilize this wealth of information, we developed AI-driven platform, the “CHICKPEA OMICS EXPLORER”. This interactive database integrates multiple genomic resources including Phytozome, NCBI, CicerSeq and the chickpea transcriptome database. It offers comprehensive tools for spatial-temporal gene expression profiling, motif discovery, RNA coding potential analysis, protein interaction networks, pathway enrichment analysis, SNP detection, and ortholog identification. By consolidating diverse datasets and analysis, the Chickpea Omics Explorer serves as a powerful resourse for trait dissection, molecular breeding and functional genomics research in chickpea.'
        '    </p>'
        '  </div>'
        '</div>'
        '', unsafe_allow_html=True)
    with col3:
        con=st.container(border=False, key="con04hp")
        with con:
            if st.button("Gene Structure", use_container_width=True, key="navGSDS", type="primary"):
                st.write("This feature is under development. Please check back later.")
                #st.session_state["programmatic_nav"] = True
                #st.session_state["current_page"] = "SNP-CALLING"
                #st.rerun()
        con=st.container(border=False, key="con05hp")
        with con:
            if st.button("Gene Map", use_container_width=True, key="navSNAP", type="primary"):
                st.write("This feature is under development. Please check back later.")
                #st.session_state["programmatic_nav"] = True
                #st.session_state["current_page"] = "GO-ANALYSIS"
                #st.rerun()
        con=st.container(border=False, key="con06hp")
        with con:
            if st.button("CRISPR Construct", use_container_width=True, key="navCRISPR", type="primary"):
                st.session_state["programmatic_nav"] = True
                st.session_state["current_page"] = "CRISPR"
                st.rerun()
    st.markdown("""
    <style>
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
        min-height: 150px !important;
        background-color: #833c0d !important;  /* Default background color */
        transition: all 0.3s ease-in-out !important;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background-color: rgba(197,91,17,1) !important;  /* Hover background color */
    }
    
    .stVerticalBlock.st-key-con03hp, .stVerticalBlock.st-key-con01hp, .stVerticalBlock.st-key-con02hp,  {
        background-color: #833c0d;
        padding: 20px;
        border-radius: 2rem;
        transition: all 0.3s ease-in-out;
    }
    .stVerticalBlock.st-key-con03hp:hover, .stVerticalBlock.st-key-con01hp:hover, .stVerticalBlock.st-key-con02hp:hover {
        background-color: rgba(197,91,17,1); 
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); 
        outline: none;
        transform: translateY(-2px);
    } 
    </style>""", unsafe_allow_html=True)
    base_footer()
    return

def search_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    if st.session_state.get('authenticated', False):
        username = st.session_state.get('username')
    header_styled("Search", "Users can get detailed genomic information by inserting Phytozome/NCBI gene IDs. The search is case sensitive. For example, entering Ca_00001 will provide detailed information including genomic sequence, transcript sequence, CDS, peptide sequence, promoter sequence, biochemical properties, protein-protein interaction, cellular localization, Gene Ontology and KEGG analysis, SNP calling, lncRNA, miRNA targets, transcription factors, orthologs/paralogs, and protein model prediction.")
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

    if start_button:
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
                
                #cursor.execute(query_mtid, (username, mtid))
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
                #cursor.execute(query_mlocid, (username, mlocid))
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

