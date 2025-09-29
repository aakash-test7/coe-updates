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
from streamlit.components.v1 import html as st_components_html
import os
from google.cloud import storage
import io
import json
from google.oauth2 import service_account
from google.cloud import storage
from datetime import timedelta
from google.oauth2 import service_account

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

bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "chickpea-transcriptome3")

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

df = read_excel_from_gcs(bucket_name, "Data/FPKM_Matrix(Ca).xlsx")
miRNA_df = read_excel_from_gcs(bucket_name, "Data/8.xlsx")
protein_df = read_excel_from_gcs(bucket_name, "Data/9.xlsx")
combined_data = read_excel_from_gcs(bucket_name, "Data/7.xlsx")
GO_df = read_excel_from_gcs(bucket_name, "Data/10.xlsx")
cello_df = read_excel_from_gcs(bucket_name, "Data/13.xlsx")
tsi_df=read_excel_from_gcs(bucket_name, "Data/12.xlsx")
prop_df=read_excel_from_gcs(bucket_name,"Data/16.xlsx")
tf_df=read_excel_from_gcs(bucket_name,"Data/17.xlsx")

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


            # Display as code block with copy functionality
            with st.expander(f"Genomic Sequence (Genomic Coordinates - {genomic_coordinates})"):
                st.code(gene_code, language="text")
            with st.expander("Transcript Sequence"):
                st.code(transcript_code, language="text")
            with st.expander("CDS Sequence"):
                st.code(cds_code, language="text")
            with st.expander("Peptide Sequence"):
                st.code(peptide_code, language="text")
            with st.expander("Promoter Sequence (Genomic Sequences 2kb upstream to the transcription start site)"):
                st.code(promote_code, language="text")
            combined_file_content = (
                f">{tid}|{tid} Genomic Sequence\n{gene_code}\n\n"
                f">{tid}|{tid} Transcript Sequence\n{transcript_code}\n\n"
                f">{tid}|{tid} CDS Sequence\n{cds_code}\n\n"
                f">{tid}|{tid} Peptide Sequence\n{peptide_code}\n\n"
                f">{tid}|{tid} Promoter Sequence\n{promote_code}\n")
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            header = f">{tid}|{tid}"
            promote_file = f"{header}\n{promote_code}\n"
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Promoter Sequence as .txt", data=promote_file, file_name=f"{tid}_promoter_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

            st.write("Paste the promoter sequence on the following link to get promoter region analysis!")
            st.write("https://bioinformatics.psb.ugent.be/webtools/plantcare/html/search_CARE_onCluster.html\n")
            return True
        return False
    else:
        # For multi transcript IDs
        for t_id in tid:
            matching_rows = df[df['Transcript id'] == t_id]
            if not matching_rows.empty:
                cds_code = format_sequence(matching_rows['Cds Sequence'].values[0])
                peptide_code = format_sequence(matching_rows['Peptide Sequence'].values[0])
                transcript_code = format_sequence(matching_rows['Transcript Sequence'].values[0])
                gene_code = format_sequence(matching_rows['Genomic Sequence'].values[0])
                promote_code = format_sequence(matching_rows['Promoter Sequence'].values[0])
                genomic_coordinates = matching_rows['Genomic Coordinates'].values[0]

                with st.expander(f"{t_id} Genomic Sequence (Genomic Coordinates - {genomic_coordinates})"):
                    st.code(gene_code, language="text")
                with st.expander(f"{t_id} Transcript Sequence"):
                    st.code(transcript_code, language="text")
                with st.expander(f"{t_id} CDS Sequence"):
                    st.code(cds_code, language="text")
                with st.expander(f"{t_id} Peptide Sequence"):
                    st.code(peptide_code, language="text")
                with st.expander(f"{t_id} Promoter Sequence (Genomic Sequences 2kb upstream to the transcription start site)"):
                    st.code(promote_code, language="text")

                combined_file_content = (
                    f">{t_id}|{t_id} Genomic Sequence\n{gene_code}\n\n"
                    f">{t_id}|{t_id} Transcript Sequence\n{transcript_code}\n\n"
                    f">{t_id}|{t_id} CDS Sequence\n{cds_code}\n\n"
                    f">{t_id}|{t_id} Peptide Sequence\n{peptide_code}\n\n"
                    f">{t_id}|{t_id} Promoter Sequence\n{promote_code}\n")
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

                header = f">{t_id}|{t_id}"
                promote_file = f"{header}\n{promote_code}\n"
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Promoter Sequence as .txt", data=promote_file, file_name=f"{t_id}_promoter_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

                st.write(f"Paste the promoter sequence for {t_id} on the following link to get promoter region analysis!")
                st.write("https://bioinformatics.psb.ugent.be/webtools/plantcare/html/search_CARE_onCluster.html\n")
                st.write("\n")
            else:
                st.write(f"No matching data found for Gene ID: {t_id}\n")

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
            # Removed separate 'else' message
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

    with st.expander("Key Terms and Definitions", expanded=False):
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
def transcriptid_info(tid):
    if 'Transcript id' in df.columns and 'lncRNA' in df.columns:
        matching_row = df[df['Transcript id'] == tid]

        if not matching_row.empty:
            con=st.container(border=True)
            with con:
                st.subheader("Sequence data")
                show_sequence_data(tid)

            #con=st.container(border=True)
            #with con:
                st.subheader("Biochemical Properties")
                show_biochemical_properties(tid)

            con=st.container(border=True)
            with con:
                st.subheader("Protein Protein Interaction")
                show_protein_ppi_data(tid)
            
            con=st.container(border=True)
            with con:
                st.subheader("Cellular-localization")
                show_cellular_Localization(tid)

            con=st.container(border=True)
            with con:
                st.subheader("Gene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis")
                show_go_kegg_data(tid)

            con=st.container(border=True)
            with con:
                st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
                show_fpkm_matrix(tid)
                fpkm_glossary()

            con=st.container(border=True)
            with con:
                st.subheader("Single Nucleotide Polymorphism (SNP)")
                show_snp_data(tid)

            con=st.container(border=True)
            with con:
                st.subheader("RNA")
                show_rna_data(tid)

                st.subheader("lncRNA")
                show_lncrna_data(tid)

                st.subheader("miRNA Target")
                show_mirna_data(tid)

            con=st.container(border=True)
            with con:
                st.subheader("Orthologs")
                show_orthologs_data(tid)
                
                st.subheader("Paralogs")
                show_inparalogs_data(tid)
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
        con=st.container(border=True)
        with con:
            st.subheader("\nSequences data")
            show_sequence_data(found_ids, is_multi=True)

            st.subheader("Biochemical Properties")
            show_biochemical_properties(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("Protein Protein Interaction")
            show_protein_ppi_data(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("\nCellular-localization")
            show_cellular_Localization(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("\nGene Ontology and Kyoto Encyclopedia of Genes and Genomes Analysis")
            show_go_kegg_data(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("Fragments per kilobase of Exon per million mapped fragments Matrix Atlas")
            show_fpkm_matrix(found_ids, is_multi=True)
            fpkm_glossary()

        con=st.container(border=True)
        with con:
            st.subheader("\nSingle Nucleotide Polymorphism (SNP)")
            show_snp_data(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("RNA")
            show_rna_data(found_ids, is_multi=True)
            st.subheader("lncRNA")
            show_lncrna_data(found_ids, is_multi=True)
            st.subheader("miRNA Target")
            show_mirna_data(found_ids, is_multi=True)

        con=st.container(border=True)
        with con:
            st.subheader("Orthologs")
            show_orthologs_data(found_ids, is_multi=True)
            st.subheader("\nParalogs")
            show_inparalogs_data(found_ids, is_multi=True)
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

def user_input_menu(tid):
        transcriptid_info(tid)
        if tid in combined_data['Transcript id'].values:
            con=st.container(border=True)
            with con:
                st.subheader("Model Prediction")
                resultant_value = combined_data[combined_data['Transcript id'] == tid]['Resultant'].values[0]
                st.write(f"Stage/Tissue Group Concerned {tid}: {resultant_value}\n")
                unique_resultant_values = []
                tissues = resultant_value.split(", ")
                for tissue in tissues:
                    if tissue not in unique_resultant_values:
                            unique_resultant_values.append(tissue)
                for term in unique_resultant_values:
                    with st.expander(glossary_first[term],expanded=False):
                        definition = glossary_entries.get(glossary_first[term], "Definition not available.")
                        st.write(definition)
                perf_chart(unique_resultant_values)
        else:
            con=st.container(border=True)
            with con:
                st.subheader("Model Prediction")
                st.write("Expression Status : normal  ( no particular tissue/stage favoured ) 0 \n")
        return

def multi_user_input_menu(mtid):
        multi_transcriptid_info(mtid)
        if "," in mtid:
                mtid_list = mtid.split(",")
        elif " " in mtid:
                mtid_list = mtid.split(" ")
        else:
                mtid_list= [mtid.strip()]
        mtid_list.sort()
        con=st.container(border=True)
        with con:      
            st.subheader("Model Prediction")
            unique_resultant_values = []
            for tid in mtid_list:
                if tid in combined_data['Transcript id'].values:
                    resultant_value = combined_data[combined_data['Transcript id'] == tid]['Resultant'].values[0]
                    st.write(f"{tid} Stage/Tissue Group Concerned: {resultant_value}\n")
                    tissues = resultant_value.split(", ")
                    for tissue in tissues:
                        if tissue not in unique_resultant_values:
                            unique_resultant_values.append(tissue)
                    for term in unique_resultant_values:
                        with st.expander(glossary_first[term],expanded=False):
                            definition = glossary_entries.get(glossary_first[term], "Definition not available.")
                            st.write(definition)
                else:
                    st.write(f"{tid} Expression Status : normal  ( no particular tissue/stage favoured ) 0 \n")
            if unique_resultant_values:
                perf_chart(unique_resultant_values)
        return

def process_locid(locid):
    result = protein_df[protein_df['preferredName'] == locid]
    if not result.empty:
        result = result.iloc[0]['Transcript id']
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
                st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

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
                    st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
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
                st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

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
                    st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
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
            with st.expander("Peptide Sequence"):
                st.code(peptide_code, language="text")

            combined_file_content = (
                f">{tid}|{tid} Genomic Sequence\n{gene_code}\n\n"
                f">{tid}|{tid} Peptide Sequence\n{peptide_code}\n\n")
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{tid}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)
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
                with st.expander(f"{t_id} Peptide Sequence"):
                    st.code(peptide_code, language="text")

                combined_file_content = (
                    f">{t_id}|{t_id} Genomic Sequence\n{gene_code}\n\n"
                    f">{t_id}|{t_id} Peptide Sequence\n{peptide_code}\n\n")
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.download_button(label="Download Sequence as .txt", data=combined_file_content, file_name=f"{t_id}_sequence.txt", mime="text/plain", on_click="ignore",use_container_width=True)

def header_styled(title: str, tagline: str):
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Open+Sans:wght@400;500&display=swap');

            .custom-header-box {{
                text-align: center;
                background: linear-gradient(to bottom, #833c0d 0%, #5a2a09 100%);
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
