import pandas as pd
import requests
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import base64
import time
import streamlit as st
import os
from google.cloud import storage
import io
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from streamlit.components.v1 import html as st_components_html
from google.oauth2 import service_account
from datetime import timedelta
import re 

secrets = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(secrets)

def generate_signed_url(blob_name):
    """Generates a signed URL to access a file in GCS."""
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if not blob.exists():
            print(f"File {blob_name} does not exist in bucket {bucket_name}")  # Debugging
            return None
        url = blob.generate_signed_url(expiration=timedelta(hours=1), method='GET')
        print(f"Generated signed URL for {blob_name}: {url}")  # Debugging
        return url
    except Exception as e:
        print(f"Error generating signed URL for {blob_name}: {e}")  # Debugging
        return None

# Initialize the Google Cloud Storage client
client = storage.Client(credentials=credentials)

bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "chickpea-2025")

def read_excel_from_gcs(bucket_name, blob_name, header=0):
    """Reads an Excel file from Google Cloud Storage and returns it as a DataFrame."""
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        data = blob.download_as_bytes()
        return pd.read_excel(io.BytesIO(data), header=header)
    
    except Exception as e:
        print(f"Error reading Excel file {blob_name} from GCS: {e}")
        return None

# ===================== Floating Section Navbar Helpers =====================
# Theme (mirrors Streamlit config like variables)
NAVBAR_THEME = {
    "primary": "#833c0d",
    "bg": "#fbe5d6",
    "accent": "#c55b11",
    "text": "#000000",
    "hover": "#a84d12",
}

def _inject_navbar_styles():
    """Inject CSS & JS to support a floating right-side navbar.
    The navbar container itself is created separately via render_section_navbar.
    """
    # Always inject styles to ensure they persist across reruns
    css = f"""
    <style>
    /* Root palette for easy overrides */
    :root {{
        --nav-primary: {NAVBAR_THEME['primary']};
        --nav-bg: {NAVBAR_THEME['bg']};
        --nav-accent: {NAVBAR_THEME['accent']};
        --nav-text: {NAVBAR_THEME['text']};
        --nav-hover: {NAVBAR_THEME['hover']};
    }}

    .floating-nav-wrapper {{
        position: fixed;
        top: 90px; /* below Streamlit header */
        right: 18px;
        z-index: 9999;
        max-height: 75vh;
        width: 250px;
        display: flex;
        flex-direction: column;
        background: var(--nav-bg);
        border: 1px solid var(--nav-accent);
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        padding: 12px 12px 14px 12px;
        font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
        backdrop-filter: blur(3px);
    }}

    /* Collapse (CSS-only) */
    .floating-nav-toggle-checkbox {{
        position: absolute;
        left: -10000px;
        opacity: 0;
    }}
    .floating-nav-toggle-label {{
        position: absolute;
        top: 8px;
        right: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 26px;
        border-radius: 6px;
        background: var(--nav-primary);
        color: #fff;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        user-select: none;
        transition: background .2s;
    }}
    .floating-nav-toggle-label:hover {{ background: var(--nav-hover); }}

    /* Collapsed state rules */
    .floating-nav-toggle-checkbox:checked ~ .floating-nav-list {{ display: none; }}
    .floating-nav-toggle-checkbox:checked ~ .floating-nav-header span {{ opacity: .85; }}
    .floating-nav-toggle-checkbox:checked + label::after {{ content: "☰"; }}
    .floating-nav-toggle-label::after {{ content: "×"; line-height: 1; }}

    .floating-nav-header {{
        font-size: 15px;
        font-weight: 600;
        color: var(--nav-primary);
        letter-spacing: .5px;
        margin: 0 0 4px 0;
        display: block;
    }}

    /* Search removed */

    .floating-nav-list {{
        list-style: none;
        margin: 0;
        padding: 0;
        overflow-y: auto;
        scrollbar-width: thin;
    }}
    .floating-nav-list::-webkit-scrollbar {{ width: 6px; }}
    .floating-nav-list::-webkit-scrollbar-track {{ background: transparent; }}
    .floating-nav-list::-webkit-scrollbar-thumb {{ background: var(--nav-accent); border-radius: 10px; }}

    .floating-nav-item a {{
        display: block;
        padding: 7px 9px 7px 10px; 
        margin: 2px 0;
        border-radius: 6px;
        text-decoration: none !important;
        color: var(--nav-text) !important;
        font-size: 13px;
        line-height: 1.25;
        background: rgba(255,255,255,.55);
        border: 1px solid transparent;
        transition: background .18s, color .18s, border-color .18s;
        position: relative;
    }}
    .floating-nav-item a:hover {{
        background: var(--nav-primary);
        color: #fff !important;
        border-color: var(--nav-primary);
    }}
    .floating-nav-item.active a {{
        background: var(--nav-primary);
        color: #fff !important;
        border-color: var(--nav-primary);
    }}

    /* Collapse button removed */

    @media (max-width: 1250px) {{
        .floating-nav-wrapper {{
            width: 210px;
        }}
    }}
    @media (max-width: 1000px) {{
        .floating-nav-wrapper {{
            top: auto;
            bottom: 15px;
            right: 15px;
            width: 190px;
            max-height: 60vh;
            padding: 10px 10px;
        }}
    }}
    @media (max-width: 900px) {{
        .floating-nav-wrapper {{
            position: fixed;
            right: 10px;
            bottom: 10px;
            top: auto;
            width: 180px;
            transform: translateY(0);
        }}
        .floating-nav-wrapper.minimized {{
            height: auto;
            max-height: none;
        }}
    }}

    /* Pulse indicator for active section */
    .floating-nav-item a .dot {{
        width: 6px; height: 6px; border-radius: 50%; background: var(--nav-accent);
        display: inline-block; margin-right: 6px; transition: background .25s;
    }}
    .floating-nav-item.active a .dot {{ background: #fff; }}

    /* Smooth scroll behavior for page */
    html {{ scroll-behavior: smooth; }}
    </style>
    """

    js = """
    <script>
    // Observe headings to highlight active nav item
    const activateObserver = () => {
        const nav = document.querySelector('.floating-nav-list');
        if(!nav) return;
        const links = nav.querySelectorAll('a[data-target]');
        const map = {};
        links.forEach(a => { map[a.getAttribute('data-target')] = a.parentElement; });

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if(entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    Object.values(map).forEach(li => li.classList.remove('active'));
                    if(map[id]) map[id].classList.add('active');
                }
            });
        }, { rootMargin: '0px 0px -65% 0px', threshold: [0, 1.0] });

        Object.keys(map).forEach(id => {
            const el = document.getElementById(id);
            if(el) observer.observe(el);
        });
    };

    window.addEventListener('load', () => { activateObserver(); });
    </script>
    """
    st.markdown(css + js, unsafe_allow_html=True)

def render_section_navbar(sections, title="Quick Navigation"):
    """Render the floating navigation panel.
    sections: list of tuples (id, label)
    """
    _inject_navbar_styles()
    items_html = []
    for sid, label in sections:
        items_html.append(
            f"<li class='floating-nav-item' data-label='{label.lower()}'><a data-target='{sid}' href='#{sid}'><span class='dot'></span>{label}</a></li>"
        )
    html_block = f"""
    <div class='floating-nav-wrapper'>
        <input type='checkbox' id='floating-nav-cbx' class='floating-nav-toggle-checkbox' />
        <label for='floating-nav-cbx' class='floating-nav-toggle-label'></label>
        <div class='floating-nav-header'>
            <span>{title}</span>
        </div>
        <ul class='floating-nav-list'>
            {''.join(items_html)}
        </ul>
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)

def section_anchor(section_id):
    """Insert an HTML anchor target with spacing above to avoid header overlap."""
    st.markdown(f"<div id='{section_id}' style='position:relative; top:-75px;'></div>", unsafe_allow_html=True)

# =================== End Floating Section Navbar Helpers ===================

def _slugify(label: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '-' for c in label).strip('-').replace('--','-')

df = read_excel_from_gcs(bucket_name, "Data/FPKM_Matrix(Ca).xlsx")
miRNA_df = read_excel_from_gcs(bucket_name, "Data/8.xlsx")
protein_df = read_excel_from_gcs(bucket_name, "Data/9.xlsx")
combined_data = read_excel_from_gcs(bucket_name, "Data/7.xlsx")
GO_df = read_excel_from_gcs(bucket_name, "Data/10.xlsx")
cello_df = read_excel_from_gcs(bucket_name, "Data/13.xlsx")
tsi_df=read_excel_from_gcs(bucket_name, "Data/12.xlsx")
prop_df=read_excel_from_gcs(bucket_name,"Data/16.xlsx")
tf_df=read_excel_from_gcs(bucket_name,"Data/17.xlsx")
pfam_df=read_excel_from_gcs(bucket_name,"Data/18.xlsx")
df_28=read_excel_from_gcs(bucket_name,"Data/19.xlsx")

def normalize_data(data):
    return data.applymap(lambda x: np.log2(x) if x > 0 else 0)

def format_sequence2(seq):
    if isinstance(seq, float) and np.isnan(seq):
        return ''
    
    return '\n'.join('\t\t ' + ' '.join([seq[i:i+6] for i in range(j, min(j + 90, len(seq)), 6)]) for j in range(0, len(seq), 90))

def format_sequence(seq):    
    return seq

def get_string_network_link(protein_transcript):

    api_url = "https://string-db.org/api/tsv/get_link?"

    params = {
        'identifiers': protein_transcript,
        'species': 3827,
        'format': 'json'
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.text.strip()
    else:
        return f"Error: {response.status_code}"

def read_orthologs_from_gcs(bucket_name, blob_name):
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        orthologs_data = []
        with blob.open("r") as infile:
            for line in infile:
                columns = line.strip().split()
                if len(columns) >= 3:
                    species_a, species_b, score = columns[0], columns[1], columns[2]
                    orthologs_data.append((species_a, species_b, score))
        return pd.DataFrame(orthologs_data, columns=["Species A", "Species B", "Score"])
    except Exception as e:
        print(f"Error loading orthologs data: {e}")
        return None

def read_paralogs_from_gcs(bucket_name, blob_name):
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        paralogs_data = []
        with blob.open("r") as infile:
            for line in infile:
                columns = line.strip().split()
                if len(columns) >= 3:
                    species_a, species_b, score = columns[0], columns[1], columns[2]
                    paralogs_data.append((species_a, species_b, score))
        return pd.DataFrame(paralogs_data, columns=["Species A", "Species B", "Score"])
    except Exception as e:
        print(f"Error loading paralogs data: {e}")
        return None

orthologs_df = read_orthologs_from_gcs(bucket_name, "Data/14.txt")
paralogs_df = read_paralogs_from_gcs(bucket_name, "Data/15.txt")

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920, 1200")
    options.add_argument('--disable-dev-shm-usage')
    #driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    return driver

def automate_Cultivated_task(tid):
    driver = web_driver()
    driver.get("https://cegresources.icrisat.org/cicerseq/?page_id=3605")
    time.sleep(3)

    gene_id_dropdown = Select(driver.find_element(By.NAME, "select_crop"))
    gene_id_dropdown.select_by_value("cultivars")

    radio_button = driver.find_element(By.ID, "gene_snp")
    radio_button.click()

    gene_id_dropdown = Select(driver.find_element(By.NAME, "key1"))
    gene_id_dropdown.select_by_value("GeneID")

    intergenic_dropdown = Select(driver.find_element(By.NAME, "key4"))
    intergenic_dropdown.select_by_value("intergenic")

    input_field = driver.find_element(By.ID, "tmp1")
    input_field.clear()
    input_field.send_keys(tid) #Ca_00004

    search_button = driver.find_element(By.NAME, "submit")
    search_button.click()

    time.sleep(5)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    return page_source

def automate_Wild_task(tid):
    driver = web_driver()
    driver.get("https://cegresources.icrisat.org/cicerseq/?page_id=3605")
    time.sleep(3)

    gene_id_dropdown = Select(driver.find_element(By.NAME, "select_crop"))
    gene_id_dropdown.select_by_value("wild")

    radio_button = driver.find_element(By.ID, "wgene_snp")
    radio_button.click()

    gene_id_dropdown = Select(driver.find_element(By.NAME, "key2"))
    gene_id_dropdown.select_by_value("GeneID")

    intergenic_dropdown = Select(driver.find_element(By.NAME, "key4"))
    intergenic_dropdown.select_by_value("intergenic")

    input_field = driver.find_element(By.ID, "tmp3")
    input_field.clear()
    input_field.send_keys(tid) #Ca_00004

    search_button = driver.find_element(By.NAME, "submitw")
    search_button.click()

    time.sleep(5)

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    return page_source


def show_sequence_data(tid, is_multi=False):
    """Display sequence data for a transcript ID."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            cds_code = format_sequence(matching_row['Cds Sequence'].values[0])
            peptide_code = format_sequence(matching_row['Peptide Sequence'].values[0])
            transcript_code = format_sequence(matching_row['Transcript Sequence'].values[0])
            gene_code = format_sequence(matching_row['Genomic Sequence'].values[0])
            promote_code = format_sequence(matching_row['Promoter Sequence'].values[0])
            genomic_coordinates = matching_row['Genomic Coordinates'].values[0]
            loc_id = matching_row['LOC ID'].values[0]


            # Display as code block with copy functionality
            with st.expander(f"Genomic Sequence (Genomic Coordinates - {genomic_coordinates})"):
                st.code(gene_code, language="text")
            with st.expander("Transcript Sequence"):
                st.code(transcript_code, language="text")
            with st.expander("CDS Sequence"):
                st.code(cds_code, language="text")
            with st.expander("Protein Sequence"):
                st.code(peptide_code, language="text")
            with st.expander("Promoter Sequence (Genomic Sequences 2kb upstream to the transcription start site)"):
                st.code(promote_code, language="text")

            combined_file_content = (
                f">{tid}|{loc_id} Genomic Sequence\n{gene_code}\n\n"
                f">{tid}|{loc_id} Transcript Sequence\n{transcript_code}\n\n"
                f">{tid}|{loc_id} CDS Sequence\n{cds_code}\n\n"
                f">{tid}|{loc_id} Protein Sequence\n{peptide_code}\n\n"
                f">{tid}|{loc_id} Promoter Sequence\n{promote_code}\n")
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{tid}_{loc_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            header = f">{tid}|{loc_id}"
            promote_file = f"{header}\n{promote_code}\n"
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Promoter Sequence in FASTA Format (.txt)", data=promote_file, file_name=f"{tid}_{loc_id}_promoter_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            st.write("Paste the promoter sequence on the following link to get promoter region analysis!")
            st.write("https://bioinformatics.psb.ugent.be/webtools/plantcare/html/search_CARE_onCluster.html\n")
            return True
        return False
    else:
        genomic_sequences = ""
        transcript_sequences = ""
        cds_sequences = ""
        peptide_sequences = ""
        promoter_sequences = ""

        for t_id in tid:
            matching_rows = df[df['Transcript id'] == t_id]
            if not matching_rows.empty:
                cds_code = format_sequence(matching_rows['Cds Sequence'].values[0])
                peptide_code = format_sequence(matching_rows['Peptide Sequence'].values[0])
                transcript_code = format_sequence(matching_rows['Transcript Sequence'].values[0])
                gene_code = format_sequence(matching_rows['Genomic Sequence'].values[0])
                promote_code = format_sequence(matching_rows['Promoter Sequence'].values[0])
                genomic_coordinates = matching_rows['Genomic Coordinates'].values[0]
                loc_id = matching_rows['LOC ID'].values[0]

                genomic_sequences += f">{t_id} | {loc_id}\n{gene_code}\n\n"
                transcript_sequences += f">{t_id} | {loc_id}\n{transcript_code}\n\n"
                cds_sequences += f">{t_id} | {loc_id}\n{cds_code}\n\n"
                peptide_sequences += f">{t_id} | {loc_id}\n{peptide_code}\n\n"
                promoter_sequences += f">{t_id} | {loc_id}\n{promote_code}\n\n"

                with st.expander(f"{t_id} | {loc_id} Genomic Sequence (Genomic Coordinates - {genomic_coordinates})"):
                    st.code(gene_code, language="text")
                with st.expander(f"{t_id} | {loc_id} Transcript Sequence"):
                    st.code(transcript_code, language="text")
                with st.expander(f"{t_id} | {loc_id} CDS Sequence"):
                    st.code(cds_code, language="text")
                with st.expander(f"{t_id} | {loc_id} Protein Sequence"):
                    st.code(peptide_code, language="text")
                with st.expander(f"{t_id} | {loc_id} Promoter Sequence (Genomic Sequences 2kb upstream to the transcription start site)"):
                    st.code(promote_code, language="text")

                combined_file_content = (
                    f">{t_id}|{loc_id} Genomic Sequence\n{gene_code}\n\n"
                    f">{t_id}|{loc_id} Transcript Sequence\n{transcript_code}\n\n"
                    f">{t_id}|{loc_id} CDS Sequence\n{cds_code}\n\n"
                    f">{t_id}|{loc_id} Protein Sequence\n{peptide_code}\n\n"
                    f">{t_id}|{loc_id} Promoter Sequence\n{promote_code}\n")
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{t_id}_{loc_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

                header = f">{t_id}|{loc_id}"
                promote_file = f"{header}\n{promote_code}\n"
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Promoter Sequence in FASTA Format (.txt)", data=promote_file, file_name=f"{t_id}_{loc_id}_promoter_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

                st.write(f"Paste the promoter sequence for {t_id} on the following link to get promoter region analysis!")
                st.write("https://bioinformatics.psb.ugent.be/webtools/plantcare/html/search_CARE_onCluster.html\n")
                st.write("\n")
            else:
                st.write(f"No matching data found for Gene ID: {t_id}\n")
        with st.expander("Combined Sequences Download", expanded=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            col2.download_button(label="Download Combined Genomic Sequences in FASTA Format (.txt)",data=genomic_sequences,file_name="combined_genomic_sequences.txt",mime="text/plain",on_click="ignore",use_container_width=True)

            col2.download_button(label="Download Combined Transcript Sequences in FASTA Format (.txt)",data=transcript_sequences,file_name="combined_transcript_sequences.txt",mime="text/plain",on_click="ignore",use_container_width=True)

            col2.download_button(label="Download Combined CDS Sequences in FASTA Format (.txt)",data=cds_sequences,file_name="combined_cds_sequences.txt",mime="text/plain",on_click="ignore",use_container_width=True)

            col2.download_button(label="Download Combined Protein Sequences in FASTA Format (.txt)",data=peptide_sequences,file_name="combined_peptide_sequences.txt",mime="text/plain",on_click="ignore",use_container_width=True)

            col2.download_button(label="Download Combined Promoter Sequences in FASTA Format (.txt)",data=promoter_sequences,file_name="combined_promoter_sequences.txt",mime="text/plain",on_click="ignore",use_container_width=True)

def show_biochemical_properties(tid, is_multi=False):
    """Display biochemical properties for transcript ID(s)."""
    if not is_multi:
        prop_matching_row = prop_df[prop_df['Transcript id'] == tid]
        if not prop_matching_row.empty:
            prop_matching_row = prop_matching_row.head(1)
            prop_matching_row = prop_matching_row.drop(columns=["Peptide"])
            prop_matching_row = prop_matching_row.drop(columns=["Status"])
            st.dataframe(prop_matching_row)
            st.write("\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in BioChemical Properties data\n")
            return False
    else:
        result = pd.DataFrame()
        for t_id in tid:
            temp_result = prop_df[prop_df['Transcript id'] == t_id]
            if not temp_result.empty:
                if 'Peptide' in temp_result.columns:
                    temp_result = temp_result.drop(columns=["Peptide"])
                if 'Status' in temp_result.columns:
                    temp_result = temp_result.drop(columns=["Status"])
                result = pd.concat([result, temp_result], ignore_index=True)
            # Removed separate 'else' message for each TID
        if not result.empty:
            result = result.drop_duplicates(subset=['Transcript id'])
            st.dataframe(result)
            return True
        else:
            st.write("No BioChemical Properties data found for any of the provided Gene IDs.\n")
            return False

def show_protein_ppi_data(tid, is_multi=False):
    """Display protein and PPI data for transcript ID(s)."""
    if not is_multi:
        protein_matching_row = protein_df[protein_df['Transcript id'] == tid]
        if not protein_matching_row.empty:
            st.dataframe(protein_matching_row)
            st.write("\n")
            protein_transcript = protein_matching_row['preferredName'].values[0]
            st.write(f"Protein Transcript for {tid}: {protein_transcript}")

            network_link = get_string_network_link(protein_transcript)
            st.write("Redirected Network URL -->", network_link)
            st.write("\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in protein data\n")
            return False
    else:
        result = pd.DataFrame()
        for t_id in tid:
            protein_matching_rows = protein_df[protein_df['Transcript id'] == t_id]
            if not protein_matching_rows.empty:
                result = pd.concat([result, protein_matching_rows], ignore_index=True)
        if not result.empty:
            sorted_result = result.sort_values(by="Transcript id")
            st.dataframe(sorted_result)
            for t_id in tid:
                protein_matching_rows = protein_df[protein_df['Transcript id'] == t_id]
                if not protein_matching_rows.empty:
                    protein_transcript = protein_matching_rows['preferredName'].values[0]
                    st.write(f"Protein Transcript for {t_id}: {protein_transcript}")
                    
                    network_link = get_string_network_link(protein_transcript)
                    st.write("Redirected Network URL -->", network_link)
                    st.write("\n")
            return True
        else:
            st.write("No protein data found for any of the provided Gene IDs.\n")
            return False

def show_cellular_Localization(tid, is_multi=False):
    """Display cellular Localization data for transcript ID(s)."""
    if not is_multi:
        cello_matching_row = cello_df[cello_df['Transcript id'] == tid]
        if not cello_matching_row.empty:
            cello_matching_row = cello_matching_row.head(1)
            cello_matching_row = cello_matching_row.drop(columns=["#Combined:"])
            st.dataframe(cello_matching_row)
            st.write("\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in Cellular Protein Localization data\n")
            return False
    else:
        result = pd.DataFrame()
        for t_id in tid:
            temp_result = cello_df[cello_df['Transcript id'] == t_id]
            if not temp_result.empty:
                if '#Combined:' in temp_result.columns:
                    temp_result = temp_result.drop(columns=['#Combined:'])
                result = pd.concat([result, temp_result], ignore_index=True)
        if not result.empty:
            result = result.drop_duplicates(subset=['Transcript id'])
            st.dataframe(result)
            return True
        else:
            st.write("No cellular Localization data found for any of the provided Gene IDs.\n")
            return False

def show_go_kegg_data(tid, is_multi=False):
    """Display GO and KEGG data for transcript ID(s)."""
    if not is_multi:
        GO_matching_row = GO_df[GO_df['Transcript id'] == tid]
        if not GO_matching_row.empty:
            st.dataframe(GO_matching_row)
            st.write("\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in GO KEGG data\n")
            return False
    else:
        result = pd.DataFrame()
        for t_id in tid:
            GO_matching_row = GO_df[GO_df['Transcript id'] == t_id]
            if not GO_matching_row.empty:
                temp_result = GO_matching_row[GO_matching_row['Transcript id'] == t_id]
                result = pd.concat([result, temp_result], ignore_index=True)
        if not result.empty:
            result = result.drop_duplicates(subset=['Transcript id'])
            st.dataframe(result)
            return True
        return False

def fpkm_glossary():
    glossary_entries = {
        'GS - Germinating Seedling': 'The early stage of seedling development where the seed begins to sprout and grow.',
        'S - Shoot': 'The above-ground part of the plant, including stems, leaves, and flowers.',
        'ML - Mature Leaf': 'A fully developed leaf, which has completed its growth.',
        'YL - Young Leaf': 'A developing leaf that has not yet reached full maturity.',
        'Brac - Bracteole': 'A small leaf-like structure at the base of a flower or inflorescence.',
        'R - Root': 'The part of the plant that anchors it in the soil and absorbs water and nutrients.',
        'Rtip - Root Tip': 'The growing tip of the root, where new cells are produced.',
        'RH - Root Hair': 'Tiny hair-like structures on the root that increase surface area for water absorption.',
        'Nod - Nodule': 'A swollen structure on plant roots, often containing nitrogen-fixing bacteria.',
        'SAM - Shoot Apical Meristem': 'The tissue at the tip of the shoot where growth and development occur.',
        'FB1-FB4 - Stages of Flower Bud Development': 'Sequential stages representing the development of flower buds.',
        'FL1-FL5 - Stages of Flower Development': 'Sequential stages representing the development of flowers.',
        'Cal - Calyx': 'The outermost whorl of a flower, usually consisting of sepals.',
        'Cor - Corolla': 'The petals of a flower, collectively forming the corolla.',
        'And - Androecium': 'The male reproductive part of the flower, consisting of stamens.',
        'Gyn - Gynoecium': 'The female reproductive part of the flower, consisting of pistils.',
        'Pedi - Pedicel': 'The stalk that supports a flower or an inflorescence.',
        'Emb - Embryo': 'The early stage of development of a plant from the fertilized egg cell.',
        'Endo - Endosperm': 'The tissue that provides nourishment to the developing embryo in seeds.',
        'SdCt - Seed Coat': 'The outer protective layer of a seed.',
        'PodSh - Podshell': 'The outer casing that surrounds the seeds within a pod.',
        '5DAP - Seed 5 Days After Pollination': 'The developmental stage of seed five days after pollination.',
        '10DAP - Seed 10 Days After Pollination': 'The developmental stage of seed ten days after pollination.',
        '20DAP - Seed 20 Days After Pollination': 'The developmental stage of seed twenty days after pollination.',
        '30DAP - Seed 30 Days After Pollination': 'The developmental stage of seed thirty days after pollination.',
    }

    with st.expander("Abbreviations", expanded=True):
        c1, c2, c3 = st.columns(3)

        columns = [c1, c2, c3]

        for i, (term, definition) in enumerate(glossary_entries.items()):
            col = columns[i % 3]
            with col:
                with st.popover(term, use_container_width=True):
                    st.write(definition)
    return

def show_fpkm_matrix(tid, is_multi=False):
    """Display FPKM matrix atlas data for transcript ID(s)."""
    temp_df = df.copy()
    if not is_multi:
        result = temp_df[temp_df['Transcript id'] == tid]
        result = result.drop(columns=['Genomic Coordinates', 'mRNA', 'lncRNA', 'Genomic Sequence', 'Transcript Sequence', 'Peptide Sequence', 'Cds Sequence', 'Promoter Sequence'])
        st.dataframe(result)
        return True
    else:
        result = pd.DataFrame()
        for t_id in tid:
            temp_result = temp_df[temp_df['Transcript id'] == t_id]
            temp_result = temp_result.drop(columns=['Genomic Coordinates', 'mRNA', 'lncRNA', 'Genomic Sequence', 'Transcript Sequence', 'Peptide Sequence', 'Cds Sequence', 'Promoter Sequence'])
            result = pd.concat([result, temp_result], ignore_index=True)
        sorted_result = result.sort_values(by="Transcript id")
        st.dataframe(sorted_result)
        return True

def show_df28_matrix(id_list, is_multi=False, by_tid=True):
    temp_df = df_28.copy()
    if by_tid:
        id_column = 'Chickpea_Id'
    else:
        id_column = 'LOC ID'
    if not is_multi:
        result = temp_df[temp_df[id_column] == id_list]
        st.dataframe(result)
        return True
    else:
        result = pd.DataFrame()
        for id in id_list:
            temp_result = temp_df[temp_df[id_column] == id]
            result = pd.concat([result, temp_result], ignore_index=True)
        sorted_result = result.sort_values(by='Chickpea_Id')
        st.dataframe(sorted_result)
        return True

TISSUE_MAPPINGS = {
    'Ger_Coleoptile': ['GS'],
    'Ger_Embryo': ['Emb'],
    'Ger_Radical': ['GS'],
    'Rep_Buds': ['FB1', 'FB2', 'FB3', 'FB4'],
    'Rep_Flower': ['FL1', 'FL2', 'FL3', 'FL4', 'FL5'],
    'Rep_Immatureseeds': ['5DAP', '10DAP'],
    'Rep_Leaf': ['YL', 'ML'],
    'Rep_Nodules': ['Nod'],
    'Rep_Petiole': [],
    'Rep_Pods': ['PodSh'],
    'Rep_Root': ['R', 'Rtip', 'RH'],
    'Rep_Stem': ['S'],
    'Seed_Epicotyl': ['S'],
    'Seed_PrimaryRoot': ['R'],
    'Sen_Immatureseed': ['10DAP', '20DAP'],
    'Sen_Matureseed': ['20DAP', '30DAP'],
    'Sen_SeedCoat': ['SdCt'],
    'Sen_Leaf-Y': ['YL', 'ML'],
    'Sen_Leaf': ['YL', 'ML'],
    'Sen_Nodules': ['Nod'],
    'Sen_Petiole': [],
    'Sen_Root': ['R'],
    'Sen_Stem': ['S'],
    'Veg_Leaf': ['YL', 'ML'],
    'Veg_Petiole': [],
    'Veg_Root': ['R'],
    'Veg_Stem': ['S']
}

def create_comparison_chart(tid, is_multi=False):
    """Create comparison chart using Streamlit native charts"""
    
    if is_multi:
        # For multiple IDs, show expanders for each transcript
        st.subheader("Individual Transcript Comparisons")
        
        for i, transcript_id in enumerate(tid):
            # Create expander for each transcript
            with st.expander(f"Transcript: {transcript_id}", expanded=(i == 0)):  # First one expanded by default
                st.info(f"Showing comparison for: **{transcript_id}**")
                
                # Get data for this specific transcript
                data_32 = df[df['Transcript id'] == transcript_id]
                data_28 = df_28[df_28['Chickpea_Id'] == transcript_id]
                
                if data_32.empty or data_28.empty:
                    st.warning(f"No data found for transcript ID: {transcript_id}")
                    continue
                
                # Prepare data for comparison for this transcript
                comparison_data = []
                
                for tissue_28, tissues_32 in TISSUE_MAPPINGS.items():
                    if tissues_32 and tissue_28 in data_28.columns and tissue_28 != 'Chickpea_Id' and tissue_28 != 'LOC ID':
                        # Get 28-tissue value
                        val_28 = data_28[tissue_28].iloc[0] if not pd.isna(data_28[tissue_28].iloc[0]) else 0
                        
                        # Get average of related 32-tissues
                        val_32 = 0
                        count = 0
                        for tissue_32 in tissues_32:
                            if tissue_32 in data_32.columns:
                                tissue_val = data_32[tissue_32].iloc[0]
                                if not pd.isna(tissue_val):
                                    val_32 += tissue_val
                                    count += 1
                        val_32 = val_32 / count if count > 0 else 0
                        
                        if val_28 > 0 or val_32 > 0:  # Only include if there's data
                            comparison_data.append({
                                'Tissue': tissue_28,
                                '28_Tissues_FPKM': val_28,
                                '32_Tissues_FPKM': val_32
                            })
                
                if not comparison_data:
                    st.warning("No comparable tissue data found for this transcript.")
                    continue
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Display as bar chart
                st.subheader("FPKM Comparison - Bar Chart")
                st.bar_chart(comparison_df.set_index('Tissue')[['28_Tissues_FPKM', '32_Tissues_FPKM']], 
                             color=['#1f77b4', '#ff7f0e'], stack=False)
                
                # Display as line chart for trend comparison
                st.subheader("FPKM Comparison - Line Chart")
                st.line_chart(comparison_df.set_index('Tissue')[['28_Tissues_FPKM', '32_Tissues_FPKM']],
                              color=['#1f77b4', '#ff7f0e'])
                
                # Display data table
                st.subheader("Comparison Data")
                st.dataframe(comparison_df)
        
    else:
        # For single ID, use it directly
        data_32 = df[df['Transcript id'] == tid]
        data_28 = df_28[df_28['Chickpea_Id'] == tid]
        
        if data_32.empty or data_28.empty:
            st.warning(f"No data found for transcript ID: {tid}")
            return
        
        # Prepare data for comparison
        comparison_data = []
        
        for tissue_28, tissues_32 in TISSUE_MAPPINGS.items():
            if tissues_32 and tissue_28 in data_28.columns and tissue_28 != 'Chickpea_Id' and tissue_28 != 'LOC ID':
                # Get 28-tissue value
                val_28 = data_28[tissue_28].iloc[0] if not pd.isna(data_28[tissue_28].iloc[0]) else 0
                
                # Get average of related 32-tissues
                val_32 = 0
                count = 0
                for tissue_32 in tissues_32:
                    if tissue_32 in data_32.columns:
                        tissue_val = data_32[tissue_32].iloc[0]
                        if not pd.isna(tissue_val):
                            val_32 += tissue_val
                            count += 1
                val_32 = val_32 / count if count > 0 else 0
                
                if val_28 > 0 or val_32 > 0:  # Only include if there's data
                    comparison_data.append({
                        'Tissue': tissue_28,
                        '28_Tissues_FPKM': val_28,
                        '32_Tissues_FPKM': val_32
                    })
        
        if not comparison_data:
            st.warning("No comparable tissue data found for this transcript.")
            return
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display as bar chart
        st.subheader("FPKM Comparison - Bar Chart")
        st.bar_chart(comparison_df.set_index('Tissue')[['28_Tissues_FPKM', '32_Tissues_FPKM']], 
                     color=['#1f77b4', '#ff7f0e'], stack=False)
        
        # Display as line chart for trend comparison
        st.subheader("FPKM Comparison - Line Chart")
        st.line_chart(comparison_df.set_index('Tissue')[['28_Tissues_FPKM', '32_Tissues_FPKM']],
                      color=['#1f77b4', '#ff7f0e'])
        
        # Display data table
        st.subheader("Comparison Data")
        st.dataframe(comparison_df)

def show_fpkm_log2(tid, is_multi=False, display=True):
    """Display FPKM matrix atlas data for transcript ID(s), with log2(cell value + 1) transformation."""
    temp_df = df.copy()
    
    expression_columns = ['GS', 'S', 'R', 'Rtip', 'RH', 'YL', 'ML', 'Brac', 'SAM', 'FB1', 'FB2', 'FB3', 'FB4', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'Cal', 'Cor', 'And', 'Gyn', 'Pedi', 'PodSh', 'SdCt', 'Emb', 'Endo', '5DAP', '10DAP', '20DAP', '30DAP', 'Nod']
    
    if not is_multi:
        result = temp_df[temp_df['Transcript id'] == tid]
        columns_to_drop = ['Genomic Coordinates', 'mRNA', 'lncRNA', 'Genomic Sequence', 'Transcript Sequence', 
                          'Peptide Sequence', 'Cds Sequence', 'Promoter Sequence']
        columns_to_drop = [col for col in columns_to_drop if col in result.columns]
        result = result.drop(columns=columns_to_drop)

        result.loc[:, expression_columns] = result[expression_columns].apply(lambda x: np.log2(x + 1)) #change for log2 transformation (lambda x: [math.log2(val) if val > 0 else math.log2(1e-4) for val in x])

        if display:
            st.dataframe(result)
        return result
    else:
        result = pd.DataFrame()
        for t_id in tid:
            temp_result = temp_df[temp_df['Transcript id'] == t_id]
            columns_to_drop = ['Genomic Coordinates', 'mRNA', 'lncRNA', 'Genomic Sequence', 'Transcript Sequence', 
                              'Peptide Sequence', 'Cds Sequence', 'Promoter Sequence']
            columns_to_drop = [col for col in columns_to_drop if col in temp_result.columns]
            temp_result = temp_result.drop(columns=columns_to_drop)

            temp_result.loc[:, expression_columns] = temp_result[expression_columns].apply(lambda x: np.log2(x + 1)) #change for log2 transformation (lambda x: [math.log2(val) if val > 0 else math.log2(1e-4) for val in x])
            
            result = pd.concat([result, temp_result], ignore_index=True)

        sorted_result = result.sort_values(by="Transcript id")
        if display:
            st.dataframe(sorted_result)
        return sorted_result

def show_df28_log2(id_list, is_multi=False, by_tid=True, display=True):
    temp_df = df_28.copy()
    if by_tid:
        id_column = 'Chickpea_Id'
    else:
        id_column = 'LOC ID'
    
    expression_columns_28 = ['Ger_Coleoptile', 'Ger_Embryo', 'Ger_Radical', 'Rep_Buds', 'Rep_Flower', 
                             'Rep_Immatureseeds', 'Rep_Leaf', 'Rep_Nodules', 'Rep_Petiole', 'Rep_Pods', 
                             'Rep_Root', 'Rep_Stem', 'Seed_Epicotyl', 'Seed_PrimaryRoot', 'Sen_Immatureseed', 
                             'Sen_Leaf-Y', 'Sen_Leaf', 'Sen_Matureseed', 'Sen_Nodules', 'Sen_Petiole', 
                             'Sen_Root', 'Sen_SeedCoat', 'Sen_Stem', 'Veg_Leaf', 'Veg_Petiole', 'Veg_Root', 
                             'Veg_Stem']

    if not is_multi:
        result = temp_df[temp_df[id_column] == id_list]
        columns_to_drop = ['Tracking_id', 'Genomic coordinates', 'Sequence description']
        columns_to_drop = [col for col in columns_to_drop if col in result.columns]
        result = result.drop(columns=columns_to_drop)
        
        result.loc[:, expression_columns_28] = result[expression_columns_28].apply(lambda x: np.log2(x + 1)) #change for log2 transformation (lambda x: [math.log2(val) if val > 0 else math.log2(1e-4) for val in x])

        if display:
            st.dataframe(result)
        return result
    else:
        result = pd.DataFrame()
        for id_val in id_list:
            temp_result = temp_df[temp_df[id_column] == id_val]
            
            temp_result.loc[:, expression_columns_28] = temp_result[expression_columns_28].apply(lambda x: np.log2(x + 1)) #change for log2 transformation (lambda x: [math.log2(val) if val > 0 else math.log2(1e-4) for val in x])
            
            result = pd.concat([result, temp_result], ignore_index=True)
        
        sorted_result = result.sort_values(by='Chickpea_Id')
        if display:
            st.dataframe(sorted_result)
        return sorted_result
    
def create_comparison_chart_log2(tid, is_multi=False):
    """Create comparison chart using log2 transformed values"""
    
    if is_multi:
        # For multiple IDs, show expanders for each transcript
        st.subheader("Individual Transcript Comparisons (Log2)")
        
        for i, transcript_id in enumerate(tid):
            # Create expander for each transcript
            with st.expander(f"Transcript: {transcript_id}", expanded=(i == 0)):  # First one expanded by default
                st.info(f"Showing comparison for: **{transcript_id}**")
                
                # Get log2 transformed data for this specific transcript
                data_32_log2 = show_fpkm_log2(transcript_id, is_multi=False, display=False)
                data_28_log2 = show_df28_log2(transcript_id, is_multi=False, by_tid=True, display=False)

                if data_32_log2.empty or data_28_log2.empty:
                    st.warning(f"No data found for transcript ID: {transcript_id}")
                    continue
                
                # Prepare data for comparison for this transcript
                comparison_data = []
                
                for tissue_28, tissues_32 in TISSUE_MAPPINGS.items():
                    if tissues_32 and tissue_28 in data_28_log2.columns:
                        # Get 28-tissue log2 value
                        val_28 = data_28_log2[tissue_28].iloc[0] if not pd.isna(data_28_log2[tissue_28].iloc[0]) else 0
                        
                        # Get average of related 32-tissues log2 values
                        val_32 = 0
                        count = 0
                        for tissue_32 in tissues_32:
                            if tissue_32 in data_32_log2.columns:
                                tissue_val = data_32_log2[tissue_32].iloc[0]
                                if not pd.isna(tissue_val):
                                    val_32 += tissue_val
                                    count += 1
                        val_32 = val_32 / count if count > 0 else 0
                        
                        if val_28 > 0 or val_32 > 0:  # Only include if there's data
                            comparison_data.append({
                                'Tissue': tissue_28,
                                '28_Tissues_log2(FPKM+1)': val_28,
                                '32_Tissues_log2(FPKM+1)': val_32
                            })
                
                if not comparison_data:
                    st.warning("No comparable tissue data found for this transcript.")
                    continue
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Display as bar chart
                st.subheader("Log2(FPKM+1) Comparison - Bar Chart")
                st.bar_chart(comparison_df.set_index('Tissue')[['28_Tissues_log2(FPKM+1)', '32_Tissues_log2(FPKM+1)']],
                             color=['#1f77b4', "#ff0e0e"], stack=False)
                
                # Display as line chart for trend comparison
                st.subheader("Log2(FPKM+1) Comparison - Line Chart")
                st.line_chart(comparison_df.set_index('Tissue')[['28_Tissues_log2(FPKM+1)', '32_Tissues_log2(FPKM+1)']],
                              color=['#1f77b4', '#ff0e0e'])

                # Display data table
                st.subheader("Log2(FPKM+1) Comparison Data")
                st.dataframe(comparison_df)
        
    else:
        # For single ID, use it directly
        data_32_log2 = show_fpkm_log2(tid, is_multi=False, display=False)
        data_28_log2 = show_df28_log2(tid, is_multi=False, by_tid=True, display=False)

        if data_32_log2.empty or data_28_log2.empty:
            st.warning(f"No data found for transcript ID: {tid}")
            return
        
        comparison_data = []
        
        for tissue_28, tissues_32 in TISSUE_MAPPINGS.items():
            if tissues_32 and tissue_28 in data_28_log2.columns:
                # Get 28-tissue log2 value
                val_28 = data_28_log2[tissue_28].iloc[0] if not pd.isna(data_28_log2[tissue_28].iloc[0]) else 0
                
                # Get average of related 32-tissues log2 values
                val_32 = 0
                count = 0
                for tissue_32 in tissues_32:
                    if tissue_32 in data_32_log2.columns:
                        tissue_val = data_32_log2[tissue_32].iloc[0]
                        if not pd.isna(tissue_val):
                            val_32 += tissue_val
                            count += 1
                val_32 = val_32 / count if count > 0 else 0
                
                if val_28 > 0 or val_32 > 0:  # Only include if there's data
                    comparison_data.append({
                        'Tissue': tissue_28,
                        '28_Tissues_log2(FPKM+1)': val_28,
                        '32_Tissues_log2(FPKM+1)': val_32
                    })
        
        if not comparison_data:
            st.warning("No comparable tissue data found for this transcript.")
            return
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display as bar chart
        st.subheader("Log2(FPKM+1) Comparison - Bar Chart")
        st.bar_chart(comparison_df.set_index('Tissue')[['28_Tissues_log2(FPKM+1)', '32_Tissues_log2(FPKM+1)']],
                     color=['#1f77b4', "#ff0e0e"], stack=False)
        
        # Display as line chart for trend comparison
        st.subheader("Log2(FPKM+1) Comparison - Line Chart")
        st.line_chart(comparison_df.set_index('Tissue')[['28_Tissues_log2(FPKM+1)', '32_Tissues_log2(FPKM+1)']],
                      color=['#1f77b4', '#ff0e0e'])

        # Display data table
        st.subheader("Log2(FPKM+1) Comparison Data")
        st.dataframe(comparison_df)

def show_pfam_matrix(id_list, is_multi=False, by_tid=True):
    temp_df = pfam_df.copy()
    if by_tid:
        id_column = 'Transcript id'
    else:
        id_column = 'LOC ID'
    if not is_multi:
        result = temp_df[temp_df[id_column] == id_list]
        st.dataframe(result)
        return True
    else:
        result = pd.DataFrame()
        for id in id_list:
            temp_result = temp_df[temp_df[id_column] == id]
            result = pd.concat([result, temp_result], ignore_index=True)
        sorted_result = result.sort_values(by='Transcript id')
        st.dataframe(sorted_result)
        return True

def show_snp_data(tid, is_multi=False):
    """Display SNP calling data for transcript ID(s)."""
    st.write("Result data for both Cultivated and Wild varieties will be downloaded in the form of HTML content. Click on the files to view data\n")
    if not is_multi:
        with st.spinner("SNP calling data loading", show_time=True):
            try:
                html_Cultivated_page_source = automate_Cultivated_task(tid)
                b64_html = base64.b64encode(html_Cultivated_page_source.encode()).decode()
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label=f"Download {tid} Cultivated SNP", data=html_Cultivated_page_source, file_name=f"{tid}_CultivatedSNP.html", mime="text/plain", on_click="ignore", use_container_width=True)
                iframe_CODE = f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="500"></iframe>'
                with st.expander("View Cultivated SNP", expanded=True):
                    st_components_html(iframe_CODE, height=500)

                html_wild_page_source = automate_Wild_task(tid)
                b64_html2 = base64.b64encode(html_wild_page_source.encode()).decode()
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label=f"Download {tid} Wild SNP", data=html_wild_page_source, file_name=f"{tid}_WildSNP.html", mime="text/plain", on_click="ignore", use_container_width=True)
                iframe_CODE2 = f'<iframe src="data:text/html;base64,{b64_html2}" width="100%" height="500"></iframe>'
                with st.expander("View Wild SNP", expanded=True):
                    st_components_html(iframe_CODE2, height=500)
                return True
            except Exception as e:
                st.write("Error ! Error ! Error !")
                st.write("Unable to fetch data from the server. Please try again later -->", "https://cegresources.icrisat.org/cicerseq/?page_id=3605\n")
                return False
    else:
        for t_id in tid:
            with st.spinner("Loading SNP caling data", show_time=True):
                try:
                    html_Cultivated_page_source = automate_Cultivated_task(t_id)
                    b64_html = base64.b64encode(html_Cultivated_page_source.encode()).decode()
                    col1,col2,col3=st.columns([1,2,1])
                    with col2:
                        st.download_button(label=f"Download {t_id} Cultivated SNP", data=html_Cultivated_page_source, file_name=f"{t_id}_CultivatedSNP.html", mime="text/plain", on_click="ignore", use_container_width=True)
                    iframe_CODE = f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="500"></iframe>'
                    with st.expander(f"View {t_id} Cultivated SNP", expanded=True):
                        st_components_html(iframe_CODE, height=500)

                    html_wild_page_source = automate_Wild_task(t_id)
                    b64_html2 = base64.b64encode(html_wild_page_source.encode()).decode()
                    col1,col2,col3=st.columns([1,2,1])
                    with col2:
                        st.download_button(label=f"Download {t_id} Wild SNP", data=html_wild_page_source, file_name=f"{t_id}_WildSNP.html", mime="text/plain", on_click="ignore", use_container_width=True)
                    iframe_CODE2 = f'<iframe src="data:text/html;base64,{b64_html2}" width="100%" height="500"></iframe>'
                    with st.expander(f"View {t_id} Wild SNP", expanded=True):
                        st_components_html(iframe_CODE2, height=500)
                except Exception as e:
                    st.write(f"Error fetching data for Gene ID: {t_id}")
                    st.write("Unable to fetch data from the server. Please try again later -->", "https://cegresources.icrisat.org/cicerseq/?page_id=3605")
        return True

def show_rna_data(tid, is_multi=False):
    """Display RNA data for transcript ID(s)."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            if pd.notna(matching_row['mRNA'].values[0]):
                st.success("mRNA present : Yes ( 1 )\n")
            else:
                st.error("mRNA absent : No ( 0 )\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in RNA data\n")
            return False
    else:
        for t_id in tid:
            matching_row = df[df['Transcript id'] == t_id]
            if not matching_row.empty:
                if pd.notna(matching_row['mRNA'].values[0]):
                    st.success(f"{t_id} mRNA present : Yes ( 1 )\n")
                else:
                    st.error(f"{t_id} mRNA absent : No ( 0 )\n")
            # Removed separate 'else' message for each TID
        return True

def show_lncrna_data(tid, is_multi=False):
    """Display lncRNA data for transcript ID(s)."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            if pd.notna(matching_row['lncRNA'].values[0]):
                st.success("lncRNAs present : Yes ( 1 )")
            else:
                st.error("lncRNAs absent : No ( 0 )\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in lncRNA data\n")
            return False
    else:
        for t_id in tid:
            matching_row = df[df['Transcript id'] == t_id]
            if not matching_row.empty:
                if pd.notna(matching_row['lncRNA'].values[0]):
                    st.success(f"{t_id} lncRNAs present : Yes ( 1 )\n")
                else:
                    st.error(f"{t_id} lncRNAs absent : No ( 0 )\n")
            # Removed separate 'else' message for each TID
        return True

def show_mirna_data(tid, is_multi=False):
    """Display miRNA data for transcript ID(s)."""
    if not is_multi:
        miRNA_matching_rows = miRNA_df[miRNA_df['Target_Acc.'] == tid]
        if not miRNA_matching_rows.empty:
            st.dataframe(miRNA_matching_rows)
            st.write("\n")
            return True
        else:
            st.write(f"No match found for Gene id: {tid} in miRNA data\n")
            return False
    else:
        miRNA_matching_rows = miRNA_df[miRNA_df['Target_Acc.'].isin(tid)]
        result = pd.DataFrame()
        for t_id in tid:
            temp_result = miRNA_matching_rows[miRNA_matching_rows['Target_Acc.'] == t_id]
            if not temp_result.empty:
                #st.dataframe(temp_result)
                #st.write("\n")
                result = pd.concat([result, temp_result], ignore_index=True)
            else:
                st.write(f"No match found for Gene id: {t_id} in miRNA data\n")
        if not result.empty:
            sorted_result = result.sort_values(by="Target_Acc.")
            st.dataframe(sorted_result)
            return True
        return False
def filter_orthologs(tid):
    """Filter orthologs data for a specific transcript ID."""
    return orthologs_df[(orthologs_df["Species A"].str.contains(tid)) | 
                        (orthologs_df["Species B"].str.contains(tid))]

def filter_paralogs(tid):
    """Filter paralogs data for a specific transcript ID."""
    return paralogs_df[(paralogs_df["Species A"].str.contains(tid)) | 
                      (paralogs_df["Species B"].str.contains(tid))]

def show_orthologs_data(tid, is_multi=False):
    """Display orthologs data for transcript ID(s)."""
    if not is_multi:
        with st.spinner("Loading Orthologs", show_time=True):
            ortho_df = filter_orthologs(tid)
            if not ortho_df.empty:
                st.dataframe(ortho_df)
                st.write("\n")
                return True
            else:
                st.write(f"No match found for Gene id: {tid} in Orthologs data\n")
                return False
    else:
        with st.spinner("Loading Orthologs", show_time=True):
            for t_id in tid:
                ortho_df = filter_orthologs(t_id)
                if not ortho_df.empty:
                    st.write(t_id)
                    st.dataframe(ortho_df)

                else:
                    st.write(f"No match found for Gene id: {t_id} in Orthologs data\n")
        return True

def show_inparalogs_data(tid, is_multi=False):
    """Display inparalogs data for transcript ID(s)."""
    if not is_multi:
        with st.spinner("Loading Paralogs", show_time=True):
            para_df = filter_paralogs(tid)
            if not para_df.empty:
                st.dataframe(para_df)
                st.write("\n")
                return True
            else:
                st.write(f"No match found for Gene id: {tid} in Inparalogs data\n")
                return False
    else:
        with st.spinner("Loading Paralogs", show_time=True):
            for t_id in tid:
                para_df = filter_paralogs(t_id)
                if not para_df.empty:
                    st.write(t_id)
                    st.dataframe(para_df)
                else:
                    st.write(f"No match found for Gene id: {t_id} in Inparalogs data\n")    

        return True
    return
def process_tid(tid, df, show_output=True):
    result = df[df['Transcript id'] == tid]
    if not result.empty:
        loc_id = result.iloc[0]['LOC ID']
        if show_output:
            st.write(f"LOC ID for Transcript id {tid} is {loc_id}")
        return loc_id
    else:
        return None

def show_tf_info(tid, is_multi=False):
    """Display Transcription Factor info for Transcript ID(s) by matching Gene_ID in tf_df."""
    
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


def transcriptid_info(tid):
    if 'Transcript id' in df.columns and 'lncRNA' in df.columns:
        matching_row = df[df['Transcript id'] == tid]

        if not matching_row.empty:
            # Define ordered sections (label list) for single transcript
            section_labels = [
                "Sequence data",
                "Biochemical Properties",
                "Protein Protein Interaction",
                "Cellular-localization",
                "Gene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis",
                "Fragments per kilobase of Exon per million mapped fragments Matrix Atlas",
                "Pfam Domain Information",
                "Single Nucleotide Polymorphism (SNP)",
                "RNA",
                "lncRNA",
                "miRNA Target",
                "Transcription Factor",
                "Orthologs",
                "Paralogs",
                "Model Prediction"
            ]
            sections = [(_slugify(lbl), lbl) for lbl in section_labels]
            render_section_navbar(sections, title="Sections")
            con=st.container(border=True)
            with con:
                section_anchor(sections[0][0])
                st.subheader("Sequence data")
                show_sequence_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                    st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                    st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)
    
                section_anchor(sections[1][0])
                st.subheader("Biochemical Properties")
                show_biochemical_properties(tid)

            con=st.container(border=True)
            with con:
                section_anchor(sections[2][0])
                st.subheader("Protein Protein Interaction")
                show_protein_ppi_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("STRING v12.0 - https://string-db.org/")
                with c2.popover("Research Article", use_container_width=True):    
                    st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/36370105/" target="_blank">Szklarczyk D, Kirsch R, Koutrouli M, Nastou K, Mehryary F, Hachilif R, Gable AL, Fang T, Doncheva NT, Pyysalo S, Bork P, Jensen LJ, von Mering C. The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. Nucleic Acids Res. 2023 Jan 6;51(D1):D638-D646. doi: 10.1093/nar/gkac1000. PMID: 36370105; PMCID: PMC9825434. https://pubmed.ncbi.nlm.nih.gov/36370105/</a>', unsafe_allow_html=True)
            
            con=st.container(border=True)
            with con:
                section_anchor(sections[3][0])
                st.subheader("Cellular-localization")
                show_cellular_Localization(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
                with c2.popover("Research Article", use_container_width=True):    
                    st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                    st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

            con=st.container(border=True)
            with con:
                section_anchor(sections[4][0])
                st.subheader("Gene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis")
                show_go_kegg_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("GOATOOLS: A Python library for Gene Ontology analyses - https://pypi.org/project/goatools/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('<a href="https://www.nature.com/articles/s41598-018-28948-z" target="_blank">Klopfenstein, D.V., Zhang, L., Pedersen, B.S. et al. GOATOOLS: A Python library for Gene Ontology analyses. Sci Rep 8, 10872 (2018). https://doi.org/10.1038/s41598-018-28948-z</a>', unsafe_allow_html=True)
    
            tab1,tab2=st.tabs(["FPKM Values", "log2(FPKM+1) Transformed"])
            with tab1:
                con=st.container(border=True)
                with con:
                    section_anchor(sections[5][0])
                    st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_matrix(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                    show_df28_matrix(tid, by_tid=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                    create_comparison_chart(tid)
                    fpkm_glossary()
            with tab2:
                con=st.container(border=True)
                with con:
                    section_anchor(sections[5][0])
                    st.subheader("Log2(FPKM+1) Transformed - Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                    show_fpkm_log2(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
        
                    show_df28_log2(tid, by_tid=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                    create_comparison_chart_log2(tid)
                    fpkm_glossary()

            con=st.container(border=True)
            with con:
                section_anchor(sections[6][0])
                st.subheader("Pfam Domain Information")
                show_pfam_matrix(tid, by_tid=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write(" a ")
                with c2.popover("Research Article", use_container_width=True):    
                    st.write(' a ')

            con=st.container(border=True)
            with con:
                section_anchor(sections[7][0])
                st.subheader("Single Nucleotide Polymorphism (SNP)")
                show_snp_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("https://cegresources.icrisat.org/cicerseq/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://doi.org/10.1038/s41586-021-04066-1" target="_blank">Varshney, R.K., Roorkiwal, M., Sun, S. et al. A chickpea genetic variation map based on the sequencing of 3,366 genomes. Nature 599, 622–627 (2021). https://doi.org/10.1038/s41586-021-04066-1</a>""", unsafe_allow_html=True)

            con=st.container(border=True)
            with con:
                section_anchor(sections[8][0])
                st.subheader("RNA")
                show_rna_data(tid)
                section_anchor(sections[9][0])
                st.subheader("lncRNA")
                show_lncrna_data(tid)
                section_anchor(sections[10][0])
                st.subheader("miRNA Target")
                show_mirna_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("PmiREN - https://pmiren.com")
                    st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                    st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
            con=st.container(border=True)
            with con:
                section_anchor(sections[11][0])
                st.subheader("Transcription Factor")
                show_tf_info(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                    st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                    st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

            con=st.container(border=True)
            with con:
                section_anchor(sections[12][0])
                st.subheader("Orthologs")
                show_orthologs_data(tid)
                section_anchor(sections[13][0])
                st.subheader("Paralogs")
                show_inparalogs_data(tid)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
                section_anchor(sections[14][0])
        else:
            st.error("Gene ID not found\n")
    else:
        st.error("...Error...\n")
    return

def multi_transcriptid_info(mtid):
    mtid_list = [tid.strip() for tid in mtid.replace(",", " ").split()]
    mtid_list.sort()

    # Gather found IDs and missing IDs
    matching_rows = df[df['Transcript id'].isin(mtid_list)]
    found_ids = matching_rows['Transcript id'].unique().tolist()
    not_found_ids = [x for x in mtid_list if x not in found_ids]
    if not_found_ids:
        st.error(f"No matches found for Gene IDs: {', '.join(not_found_ids)}")

    if found_ids:
        # Define ordered sections (label list) for multi transcript view
        section_labels = [
            "Sequences data",
            "Biochemical Properties",
            "Protein Protein Interaction",
            "Cellular-localization",
            "Gene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis",
            "Fragments per kilobase of Exon per million mapped fragments Matrix Atlas",
            "Pfam Domain Information",
            "Single Nucleotide Polymorphism (SNP)",
            "RNA",
            "lncRNA",
            "miRNA Target",
            "Transcription Factor",
            "Orthologs",
            "Paralogs",
            "Model Prediction"
        ]
        sections = [(_slugify(lbl), lbl) for lbl in section_labels]
        render_section_navbar(sections, title="Sections")
        con=st.container(border=True)
        with con:
            section_anchor(sections[0][0])
            st.subheader("\nSequences data")
            show_sequence_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
            with c2.popover("Research Article", use_container_width=True):
                st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)
    
            section_anchor(sections[1][0])
            st.subheader("Biochemical Properties")
            show_biochemical_properties(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            section_anchor(sections[2][0])
            st.subheader("Protein Protein Interaction")
            show_protein_ppi_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("STRING v12.0 - https://string-db.org/")
            with c2.popover("Research Article", use_container_width=True):    
                st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/36370105/" target="_blank">Szklarczyk D, Kirsch R, Koutrouli M, Nastou K, Mehryary F, Hachilif R, Gable AL, Fang T, Doncheva NT, Pyysalo S, Bork P, Jensen LJ, von Mering C. The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. Nucleic Acids Res. 2023 Jan 6;51(D1):D638-D646. doi: 10.1093/nar/gkac1000. PMID: 36370105; PMCID: PMC9825434. https://pubmed.ncbi.nlm.nih.gov/36370105/</a>', unsafe_allow_html=True)

        con=st.container(border=True)
        with con:
            section_anchor(sections[3][0])
            st.subheader("\nCellular-localization")
            show_cellular_Localization(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
            with c2.popover("Research Article", use_container_width=True):    
                st.write("""(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>""", unsafe_allow_html=True)
                st.write("""(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>""", unsafe_allow_html=True)

        con=st.container(border=True)
        with con:
            section_anchor(sections[4][0])
            st.subheader("\nGene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis")
            show_go_kegg_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("GOATOOLS: A Python library for Gene Ontology analyses - https://pypi.org/project/goatools/")
            with c2.popover("Research Article", use_container_width=True):
                st.write('<a href="https://www.nature.com/articles/s41598-018-28948-z" target="_blank">Klopfenstein, D.V., Zhang, L., Pedersen, B.S. et al. GOATOOLS: A Python library for Gene Ontology analyses. Sci Rep 8, 10872 (2018). https://doi.org/10.1038/s41598-018-28948-z</a>', unsafe_allow_html=True)
        
        tab1,tab2=st.tabs(["FPKM Values","Log2(FPKM+1) Transformed"])
        with tab1:
            con=st.container(border=True)
            with con:
                section_anchor(sections[5][0])
                st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                show_fpkm_matrix(found_ids, is_multi=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
                show_df28_matrix(found_ids, is_multi=True, by_tid=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                create_comparison_chart(found_ids, is_multi=True)
                fpkm_glossary()
        with tab2:
            con=st.container(border=True)
            with con:
                section_anchor(sections[5][0])
                st.subheader("Log2(FPKM+1) Transformed - Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                show_fpkm_log2(found_ids, is_multi=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
                show_df28_log2(found_ids, is_multi=True, by_tid=True)
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)
                create_comparison_chart_log2(found_ids, is_multi=True)
                fpkm_glossary()

        con=st.container(border=True)
        with con:
            section_anchor(sections[6][0])
            st.subheader("Pfam Domain Information")
            show_pfam_matrix(found_ids, is_multi=True, by_tid=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write(" a ")
            with c2.popover("Research Article", use_container_width=True):    
                st.write(' a ')

        con=st.container(border=True)
        with con:
            section_anchor(sections[7][0])
            st.subheader("\nSingle Nucleotide Polymorphism (SNP)")
            show_snp_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("https://cegresources.icrisat.org/cicerseq/")
            with c2.popover("Research Article", use_container_width=True):
                st.write("""<a href="https://doi.org/10.1038/s41586-021-04066-1" target="_blank">Varshney, R.K., Roorkiwal, M., Sun, S. et al. A chickpea genetic variation map based on the sequencing of 3,366 genomes. Nature 599, 622–627 (2021). https://doi.org/10.1038/s41586-021-04066-1</a>""", unsafe_allow_html=True)

        con=st.container(border=True)
        with con:
            section_anchor(sections[8][0])
            st.subheader("RNA")
            show_rna_data(found_ids, is_multi=True)
            section_anchor(sections[9][0])
            st.subheader("lncRNA")
            show_lncrna_data(found_ids, is_multi=True)
            section_anchor(sections[10][0])
            st.subheader("miRNA Target")
            show_mirna_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("PmiREN - https://pmiren.com")
                st.write("psRNATarget - https://www.zhaolab.org/psRNATarget/")
            with c2.popover("Research Article", use_container_width=True):
                st.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""", unsafe_allow_html=True)
                st.write("""<a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""", unsafe_allow_html=True)
                st.write("""<a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""", unsafe_allow_html=True)
                st.write("""<a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""", unsafe_allow_html=True)    
            
        con=st.container(border=True)
        with con:
            section_anchor(sections[11][0])
            st.subheader("Transcription Factor")
            show_tf_info(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("PlantRegMap - http://plantregmap.gao-lab.org/")
            with c2.popover("Research Article", use_container_width=True):
                st.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
                st.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
                st.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)

        con=st.container(border=True)
        with con:
            section_anchor(sections[12][0])
            st.subheader("Orthologs")
            show_orthologs_data(found_ids, is_multi=True)
            section_anchor(sections[13][0])
            st.subheader("\nParalogs")
            show_inparalogs_data(found_ids, is_multi=True)
            c1,c2=con.columns(2)
            with c1.popover("Data Source", use_container_width=True):
                st.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/")
            with c2.popover("Research Article", use_container_width=True):
                st.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
            section_anchor(sections[14][0])
    else:
        st.error("Gene ID not found\n")

glossary_first={
    'ST':'ST - Seed Tissue',
    'FDS':'FDS - Flower Development Stages',
    'FP':'FP - Flower Parts',
    'GT':'GT - Green Tissues',
    'RT':'RT - Root Tissues'}
glossary_entries = {
    'ST - Seed Tissue': '- the tissue in seeds that supports the development of the embryo and storage of nutrients.',
    'FDS - Flower Development Stages': '- the various phases of growth and development that a flower undergoes from bud to bloom.',
    'FP - Flower Parts': '- the various components that make up a flower, including petals, sepals, stamens, and carpels.',
    'GT - Green Tissues': '- plant tissues that are photosynthetic, primarily found in leaves and stems.',
    'RT - Root Tissues': '- the tissues found in the root system of a plant, involved in nutrient absorption and anchorage.'}

def display_ml_model_prediction(tid_list):
    """
    Display ML model predictions for single or multiple transcript IDs.
    
    Args:
        tid_list: Single transcript ID (str) or list of transcript IDs
    
    Returns:
        None (displays results in Streamlit)
    """
    # Convert single ID to list for uniform processing
    if isinstance(tid_list, str):
        tid_list = [tid_list]
    
    con = st.container(border=True)
    with con:
        st.subheader("Model Prediction")
        
        unique_resultant_values = []
        ids_with_predictions = []
        ids_without_predictions = []
        
        # Process each transcript ID
        for tid in tid_list:
            tid = tid.strip()
            if tid in combined_data['Transcript id'].values:
                resultant_value = combined_data[combined_data['Transcript id'] == tid]['Resultant'].values[0]
                
                # Display individual prediction
                if len(tid_list) == 1:
                    st.write(f"Stage/Tissue Group Concerned for {tid}: {resultant_value}")
                else:
                    st.write(f"{tid} - Stage/Tissue Group Concerned: {resultant_value}")
                
                # Collect unique tissues
                tissues = resultant_value.split(", ")
                for tissue in tissues:
                    if tissue not in unique_resultant_values:
                        unique_resultant_values.append(tissue)
                
                ids_with_predictions.append(tid)
            else:
                ids_without_predictions.append(tid)
        
        # Display IDs without predictions together
        if ids_without_predictions:
            st.write("")  # Add spacing
            if len(ids_without_predictions) == 1:
                st.write(f"{ids_without_predictions[0]} - Expression Status: normal (no particular tissue/stage favoured)")
            else:
                st.write(f"**IDs with normal expression (no particular tissue/stage favoured):**")
                st.write(", ".join(ids_without_predictions))
        
        if unique_resultant_values:
            st.write("")  # Add spacing
            st.write("**Tissue/Stage Definitions:**")
            for term in unique_resultant_values:
                with st.expander(glossary_first[term], expanded=False):
                    definition = glossary_entries.get(glossary_first[term], "Definition not available.")
                    st.write(definition)
            
            # Display performance chart
            perf_chart(unique_resultant_values)

def user_input_menu(tid):
        transcriptid_info(tid)
        display_ml_model_prediction(tid)
        return

def multi_user_input_menu(mtid):
        multi_transcriptid_info(mtid)
        mtid_list = re.split(r'[,\s]+', mtid.strip())
        mtid_list = [tid.strip() for tid in mtid_list if tid.strip()]
        mtid_list.sort()
        display_ml_model_prediction(mtid_list)
        return

def process_locid(locid, show_output=True):
    result = protein_df[protein_df['preferredName'] == locid]
    if not result.empty:
        result = result.iloc[0]['Transcript id']
        if show_output:
            st.write(f"Gene ID for {locid} is {result}")
        return result
    else:
        return None
        
def process_mlocid(mlocid):
    mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
    mlocid_list = list(set(mlocid_list))
    transcript_ids = []
    for locid in mlocid_list:
        transcript_id = process_locid(locid)
        if transcript_id:
            transcript_ids.append(transcript_id)
    result=",".join(transcript_ids)
    return result

def col(selected_tissue):
    if selected_tissue == "ST":
        return "#5E5E5E"
    elif selected_tissue == "GT":
        return "#54AE32"
    elif selected_tissue == "RT":
        return "#F9DB57"
    elif selected_tissue == "FDS":
        return "#C23175"
    elif selected_tissue == "FP":
        return "#3274B5"

def perf_chart(selected_tissues):
    data = {"Tissue/Stages/File": ["ST", "GT", "RT", "FDS", "FP"],
        "Training Accuracy": [0.9457962198566152, 0.9669780577883988, 0.9564414512274604, 0.9459048446665218, 0.9404736041711927],
        "Test Accuracy": [0.9517810599478714, 0.9695916594265855, 0.9565595134665508, 0.94874022589053, 0.9422241529105126],
        "Grid Search": [0.9578533004710534, 0.9720835758784261, 0.9574185181187819, 0.9639368327061073, 0.9522051993411031],
        "Random Search": [0.9637190876647906, 0.9726262281333435, 0.9623066347952094, 0.9663269560929981, 0.9547033105857]}
    df = pd.DataFrame(data)
    df.set_index("Tissue/Stages/File", inplace=True)
    filtered_df = df.loc[selected_tissues]
    if len(selected_tissues) == 1:
        clr = col(selected_tissues[0])
        st.bar_chart(filtered_df.T, height=400, color=clr,x_label='Metrics', y_label='Accuracy/Score')
    else:
        colors = [col(tissue) for tissue in selected_tissues]
        st.bar_chart(filtered_df.T, height=400, color=colors,stack=False,x_label='Metrics', y_label='Accuracy/Score')

def svm_charts():
    data = {"Tissue/Stages/File": ["Seed Tissues", "Green Tissues", "Root Tissues", "Flower Development Stages", "Flower Parts"],
        "Training Accuracy": [0.9457962198566152, 0.9669780577883988, 0.9564414512274604, 0.9459048446665218, 0.9404736041711927],
        "Test Accuracy": [0.9517810599478714, 0.9695916594265855, 0.9565595134665508, 0.94874022589053, 0.9422241529105126],
        "Grid Search": [0.9578533004710534, 0.9720835758784261, 0.9574185181187819, 0.9639368327061073, 0.9522051993411031],
        "Random Search": [0.9637190876647906, 0.9726262281333435, 0.9623066347952094, 0.9663269560929981, 0.9547033105857]}

    df = pd.DataFrame(data)
    df.set_index("Tissue/Stages/File", inplace=True)

    st.title("Model Performance Analysis")
    st.write("The following section presents the performance analysis of the integrated machine learning model, showcasing key metrics such as training and test accuracy across various tissue-specific super-classes. Additionally, visualizations are provided to illustrate the effects of different kernel functions and hyperparameter optimization techniques on the model's performance.")
    con9=st.container(border=True)
    with con9:
        col1,col2,col3=st.columns([1,2,1])
        with col2:
            con=st.container(border=True)
            con.subheader("Dataset")
            con.dataframe(df)

        col1,col2=st.columns(2)
        with col1:
            container = st.container(border=True)
            container.subheader("Training Accuracy")
            container.bar_chart(df["Training Accuracy"],x_label='Tissue/Stages/File',y_label='Accuracy')

            # Bar chart for Test Accuracy
            container=st.container(border=True)
            container.subheader("Test Accuracy")
            container.bar_chart(df["Test Accuracy"],x_label='Tissue/Stages/File',y_label='Accuracy',color='#AFDC8F')

        with col2:
            container=st.container(border=True)
            container.subheader("Grid Search")
            container.bar_chart(df["Grid Search"],x_label='Tissue/Stages/File',y_label='Score',color='#FF6347')

            container=st.container(border=True)
            container.subheader("Random Search")
            container.bar_chart(df["Random Search"],x_label='Tissue/Stages/File',y_label='Score',color='#FFD700')

    model_data = {"Algorithm": ["linear", "rbf", "poly_deg1", "poly_deg2", "poly_deg3"], 
              "Train Accuracy": [0.8000901655181297, 0.9753976943388936, 0.8000901655181297, 0.9707606105493656, 0.9183680041218523], 
              "Test Accuracy": [0.7982998454404946, 0.9747552807831015, 0.7982998454404946, 0.9702472952086554, 0.9200154559505409]}

    m_df = pd.DataFrame(model_data)
    m_df.set_index("Algorithm", inplace=True)

    container=st.container(border=True)
    with container:
        col1,col2=st.columns([1,2])
        with col1:
            container=st.container(border=True,height=630)
            container.subheader("Dataset")
            container.dataframe(m_df,use_container_width=True)
            container.expander("Linear",expanded=False).write("Support Vector Machine with a Linear Kernel (SVM Linear) \nDescription: A linear kernel is used when the data is linearly separable. The model tries to find the best hyperplane that separates the classes")
            container.expander("RBF",expanded=False).write("Support Vector Machine with a Radial Basis Function Kernel (SVM RBF) \nDescription: The Radial Basis Function kernel is used when the data is not linearly separable. It is used to map the data into a higher-dimensional space where it can be linearly separable.")
            container.expander("Poly_deg1",expanded=False).write("Support Vector Machine with a Polynomial Kernel of Degree 1 (SVM Poly Degree 1) \nDescription: This is a polynomial kernel with degree 1, which is essentially a linear kernel. In this case, the polynomial kernel behaves the same as the linear kernel.")
            container.expander("Poly_deg2",expanded=False).write("Support Vector Machine with a Polynomial Kernel of Degree 2 (SVM Poly Degree 2) \nDescription: The polynomial kernel of degree 2 allows the decision boundary to be a quadratic function, which can be useful for separating classes in a non-linear way.")
            container.expander("Poly_deg3",expanded=False).write("Support Vector Machine with a Polynomial Kernel of Degree 3 (SVM Poly Degree 3) \nDescription: The polynomial kernel of degree 3 allows for more flexibility in modeling complex, non-linear decision boundaries by fitting cubic curves to separate the data.")
        with col2:
            container=st.container(border=True,height=630)
            container.subheader("Model Performance")
            container.bar_chart(m_df,stack=False,x_label='Algorithms',y_label='Accuracy',color=['#AFDC8F','#FF6347'],height=530)
    return

def tsi_plot():
    df = tsi_df
    st.title("Tissue Specificity Index (TSI) Analysis")
    st.write("It is a measure used to quantify how specifically a gene is expressed in a particular tissue compared to other tissues. It ranges from 0 to 1, where a TSI value of 1 indicates that the gene is expressed exclusively in one tissue, while a TSI value of 0 indicates that the gene is uniformly expressed across all tissues.")

    con=st.container(border=True)
    with con:
        con=st.container(border=True)
        col1,col2=st.columns([10,9])
        with col1:
            con=st.container(border=True,height=500)
            df['Category'] = 'non-TF'
            df.loc[df['TF family'].notna(), 'Category'] = 'TF'
            df.loc[df['lncRNA'].notna(), 'Category'] = 'lncRNA'
            df['TSI value (%)'] = df['TSI value'] * 100
            con.subheader("Dataset")
            con.dataframe(df)
        with col2:
            con=st.container(border=True,height=500)
            con.subheader("Percentage Presence of lncRNA, TF, and non-TF")
            category_counts = df['Category'].value_counts(normalize=True) * 100
            category_counts = category_counts[['non-TF', 'lncRNA', 'TF']]
            con.bar_chart(category_counts,color=['#AFDC8F'],y_label='Percentage (%)',x_label='Category',height=360)

        con=st.container(border=True)
        con.subheader("TSI Value by Tissue Type")
        tsi_by_tissue = df.groupby('TSI tissue')['TSI value (%)'].mean().reset_index()
        con.bar_chart(tsi_by_tissue.set_index('TSI tissue'),color='#FF6347',y_label='TSI value (%)',x_label='Tissue Type')
        con=st.container(border=True)

        con.subheader("Tissue-Specific Distribution of lncRNA, TF, and non-TF")
        category_counts_by_tissue = df.groupby(['TSI tissue', 'Category']).size().unstack(fill_value=0)
        category_percentages = category_counts_by_tissue.div(category_counts_by_tissue.sum(axis=1), axis=0) * 100

        custom_order = ['GS', 'S', 'R', 'Rtip', 'RH', 'YL', 'ML', 'Brac', 'SAM', 'FB1', 'FB2', 'FB3', 'FB4', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'Cal', 'Cor', 'And', 'Gyn', 'Pedi', 'PodSh', 'SdCt', 'Emb', 'Endo', '5 DAP', '10 DAP', '20  DAP', '30  DAP', 'Nod']
        category_percentages = category_percentages.reindex(custom_order)
        category_percentages = category_percentages[['non-TF', 'TF', 'lncRNA']]
        con.bar_chart(category_percentages,y_label='TSI tissue',x_label='Percentage (%)',color=['#FF6347','#FFD700','#0066CC'],height=500,width=700)
    return

def img_to_base64(image_data):
    return base64.b64encode(image_data).decode()

def mlocid_error(mlocid):
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            
            available = []
            rejected = []
            
            for locid in mlocid_list:
                transcript_id = process_locid2(locid)
                
                if transcript_id:
                    available.append(locid)
                else:
                    rejected.append(locid)
            return available, rejected

def process_locid2(locid):
    result = protein_df[protein_df['preferredName'] == locid]
    if not result.empty:
        result = result.iloc[0]['Transcript id']
        return result
    else:
        return None

def show_sequence_data_p(tid, is_multi=False):
    """Display sequence data for a transcript ID."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            gene_code = format_sequence(matching_row['Genomic Sequence'].values[0])

            # Display as code block with copy functionality
            with st.expander("Genomic Sequence", expanded=True):
                st.code(gene_code, language="text")

            combined_file_content = (
                f">{tid}|{tid} Genomic Sequence\n{gene_code}\n\n"
            )
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            return True
        return False
    else:
        # For multi transcript IDs
        for t_id in tid:
            matching_rows = df[df['Transcript id'] == t_id]
            if not matching_rows.empty:
                gene_code = format_sequence(matching_rows['Genomic Sequence'].values[0])

                with st.expander(f"{t_id} Genomic Sequence", expanded=True):
                    st.code(gene_code, language="text")

                combined_file_content = (
                    f">{t_id}|{t_id} Genomic Sequence\n{gene_code}\n\n"
                )
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
            else:
                st.write(f"No matching data found for Gene ID: {t_id}\n")

def show_sequence_data_cds(tid, is_multi=False):
    """Display sequence data for a transcript ID."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            cds_code = format_sequence(matching_row['Cds Sequence'].values[0])

            # Display as code block with copy functionality
            with st.expander("CDS Sequence", expanded=True):
                st.code(cds_code, language="text")

            combined_file_content = (
                f">{tid}|{tid} CDS Sequence\n{cds_code}\n\n"
            )
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            return True
        return False
    else:
        # For multi transcript IDs
        for t_id in tid:
            matching_rows = df[df['Transcript id'] == t_id]
            if not matching_rows.empty:
                cds_code = format_sequence(matching_rows['Cds Sequence'].values[0])

                with st.expander(f"{t_id} CDS Sequence", expanded=True):
                    st.code(cds_code, language="text")

                combined_file_content = (
                    f">{t_id}|{t_id} CDS Sequence\n{cds_code}\n\n"
                )
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
            else:
                st.write(f"No matching data found for Gene ID: {t_id}\n")

def show_sequence_data_g_p(tid, is_multi=False):
    """Display sequence data for a transcript ID."""
    if not is_multi:
        matching_row = df[df['Transcript id'] == tid]
        if not matching_row.empty:
            peptide_code = format_sequence(matching_row['Peptide Sequence'].values[0])
            gene_code = format_sequence(matching_row['Genomic Sequence'].values[0])

            # Display as code block with copy functionality
            with st.expander("Genomic Sequence"):
                st.code(gene_code, language="text")
            with st.expander("Protein Sequence"):
                st.code(peptide_code, language="text")

            combined_file_content = (
                f">{tid}|{tid} Genomic Sequence\n{gene_code}\n\n"
                f">{tid}|{tid} Protein Sequence\n{peptide_code}\n\n")
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
        return False
    else:
        # For multi transcript IDs
        for t_id in tid:
            matching_rows = df[df['Transcript id'] == t_id]
            if not matching_rows.empty:
                peptide_code = format_sequence(matching_rows['Peptide Sequence'].values[0])
                gene_code = format_sequence(matching_rows['Genomic Sequence'].values[0])

                with st.expander(f"{t_id} Genomic Sequence"):
                    st.code(gene_code, language="text")
                with st.expander(f"{t_id} Protein Sequence"):
                    st.code(peptide_code, language="text")

                combined_file_content = (
                    f">{t_id}|{t_id} Genomic Sequence\n{gene_code}\n\n"
                    f">{t_id}|{t_id} Protein Sequence\n{peptide_code}\n\n")
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence in FASTA Format (.txt)", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

def header_styled(title: str, tagline: str):
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Open+Sans:wght@400;500&display=swap');

            .custom-header-box {{
                text-align: center;
                background: linear-gradient(to bottom, #833c0d 0%, #7a3e1b 100%);
                padding: 28px 25px;
                margin-bottom: 35px;
                border-radius: 8px;
                position: relative;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                overflow: hidden;
            }}

            .custom-header-box:before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                opacity: 0.1;
                z-index: 0;
                border-radius: 8px;
            }}

            .custom-header-box:after {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 4px;
                background: linear-gradient(90deg, #c55b11, #ffe3c1, #c55b11);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}

            .custom-header-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 1.9rem;
                font-weight: 700;
                margin-bottom: 14px;
                color: white;
                letter-spacing: 1px;
                /* text-transform: uppercase; */
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                position: relative;
                z-index: 1;
            }}

            .custom-header-title:before, 
            .custom-header-title:after {{
                content: "";
                height: 3px;
                background: linear-gradient(90deg, rgba(255,255,255,0.2), rgba(255,255,255,0.8), rgba(255,255,255,0.2));
                flex-grow: 0.08;
                display: block;
            }}

            .custom-header-tagline {{
                font-family: 'Open Sans', sans-serif;
                font-size: 1.05rem;
                font-weight: 400;
                color: #ffe3c1;
                margin-top: 10px;
                letter-spacing: 0.3px;
                max-width: 80%;
                margin-left: auto;
                margin-right: auto;
                line-height: 1.5;
                position: relative;
                z-index: 1;
                padding: 0 20px;
            }}

            .custom-header-box .icon-dna {{
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                opacity: 0.15;
                font-size: 1rem;
                color: #ffe3c1;
                display: none;
            }}

            .custom-header-box .icon-bio {{
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                opacity: 0.15;
                font-size: 1rem;
                color: #ffe3c1;
                display: none;
            }}
        </style>

        <div class="custom-header-box">
            <div class="custom-header-title">{title}</div>
            <div class="custom-header-tagline">{tagline}</div>
        </div>
    """, unsafe_allow_html=True)

def run_blast_and_get_rid(sequence_input):
    driver=web_driver()
    rid = None

    try:
        driver.get("https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome")

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seq"))
        )
        textarea.clear()
        textarea.send_keys(sequence_input)

        blast_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#blastButton1 input.blastbutton"))
        )
        blast_button.click()

        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rid_input = soup.find("input", {"name": "RID"})
        if rid_input:
            rid = rid_input.get("value")

    except Exception as e:
        st.error(f"Error during BLAST submission: {e}")
    finally:
        driver.quit()

    return rid

def run_blast_and_get_protein(sequence_input):
    driver=web_driver()
    rid = None

    try:
        driver.get("https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome")

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seq"))
        )
        textarea.clear()
        textarea.send_keys(sequence_input)

        blast_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.blastbutton"))
        )
        blast_button.click()

        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rid_input = soup.find("input", {"name": "RID"})
        if rid_input:
            rid = rid_input.get("value")

    except Exception as e:
        st.error(f"Error during BLAST submission: {e}")
    finally:
        driver.quit()

    return rid

def run_gsds(cds_code, genomic_code):
    driver=web_driver()
    result_url = None

    try:
        driver.get("https://gsds.gao-lab.org") 

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input_format_selector"))
        )
        format_selector = driver.find_element(By.ID, "input_format_selector")
        format_selector.send_keys("seq")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seq_data_txt1"))
        )
        cds_textarea = driver.find_element(By.ID, "seq_data_txt1")
        cds_textarea.clear()
        cds_textarea.send_keys(cds_code)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seq_data_txt2"))
        )
        genomic_textarea = driver.find_element(By.ID, "seq_data_txt2")
        genomic_textarea.clear()
        genomic_textarea.send_keys(genomic_code)

        # Wait until the submit button is clickable
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit_button"))
        )
        # Use JavaScript to click the button (avoids interception issues)
        driver.execute_script("arguments[0].click();", submit_button)

        time.sleep(10)

        result_url = driver.current_url

    except Exception as e:
        st.error(f"Error during form submission: {e}")
    finally:
        driver.quit()

    return result_url


def run_blast_and_get_primer(sequence_input):
    driver=web_driver()
    job_id = None

    try:
        driver.get("https://www.ncbi.nlm.nih.gov/tools/primer-blast/")

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seq"))
        )
        textarea.clear()
        textarea.send_keys(sequence_input)

        get_primers_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.blastbutton.prbutton"))
        )
        get_primers_btn.click()

        end_time = time.time() + 80
        while time.time() < end_time:
            time.sleep(2)
            page = driver.page_source
            if "primertool.cgi" in page:
                soup = BeautifulSoup(page, "html.parser")
                a = soup.find("a", href=lambda h: h and "primertool.cgi" in h)
                if a and a.get("href"):
                    
                    break
                import re
                m = re.search(r"JOB\s*ID\s*[:\-]?\s*([A-Za-z0-9_\-]+)", page)
                if m:
                    job_id = m.group(1)
                    #primer_url = f"https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi?job_key={job_id}"
                    break

    except Exception as e:
        try:
            st.error(f"Error during BLAST submission: {e}")
        except Exception:
            pass
    finally:
        driver.quit()
    return job_id
