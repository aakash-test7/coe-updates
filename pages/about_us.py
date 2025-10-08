import requests
import streamlit as st
from backend import generate_signed_url, img_to_base64, svm_charts, tsi_plot, header_styled
from pages.footer import base_footer
import streamlit as st
from backend import svm_charts, tsi_plot, header_styled
from pages.footer import base_footer


def citations_page():
    header_styled("Citations","Citations for Supporting Data, Algorithms, and Tools Utilized in the ChickpeaOmicsExplorer")
    con=st.container(border=True)
    con.write("### Expression Data :")
    con.write("Chickpea Gene Expression Atlas Database (CaGEADB) - http://ccbb.jnu.ac.in/CaGEA/")
    con.write("""<a href="https://www.nature.com/articles/s42003-022-04083-4" target="_blank">Jain, M., Bansal, J., Rajkumar, M.S. et al. An integrated transcriptome mapping the regulatory network of coding and long non-coding RNAs provides a genomics resource in chickpea. Commun Biol 5, 1106 (2022). https://doi.org/10.1038/s42003-022-04083-4</a>""", unsafe_allow_html=True)
    con.write(" ")
    con.write("https://pubmed.ncbi.nlm.nih.gov/29637575/")
    con.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/29637575/" target="_blank">Kudapa H, Garg V, Chitikineni A, Varshney RK. The RNA-Seq-based high resolution gene expression atlas of chickpea (Cicer arietinum L.) reveals dynamic spatio-temporal changes associated with growth and development. Plant Cell Environ. 2018 Sep;41(9):2209-2225. doi: 10.1111/pce.13210. Epub 2018 May 16. PMID: 29637575.</a>""", unsafe_allow_html=True)

    con = st.container(border=True)
    con.write("### Sequences:")
    con.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
    con.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
    
    con=st.container(border=True)
    con.write("### BLAST Search:")
    con.write("BLAST (Basic Local Alignment Search Tool) - https://blast.ncbi.nlm.nih.gov/Blast.cgi")
    con.write("<a href='https://doi.org/10.1093/nar/gkw241' target='_blank'>Sayers EW, Beck J, Bolton EE, Brister JR, Chan J, Connor R, Feldgarden M, Fine AM, Funk K, Hoffman J, Kannan S, Kelly C, Klimke W, Kim S, Lathrop S, Marchler-Bauer A, Murphy TD, O'Sullivan C, Schmieder E, Skripchenko Y, Stine A, Thibaud-Nissen F, Wang J, Ye J, Zellers E, Schneider VA, Pruitt KD. Database resources of the National Center for Biotechnology Information in 2025. Nucleic Acids Res. 2025 Jan 6;53(D1):D20-D29. doi: 10.1093/nar/gkae979. PMID: 39526373; PMCID: PMC11701734.</a>", unsafe_allow_html=True)

    con = st.container(border=True)
    con.write("### SNP Calling:")
    con.write("https://cegresources.icrisat.org/cicerseq/")
    con.write("""<a href="https://doi.org/10.1038/s41586-021-04066-1" target="_blank">Varshney, R.K., Roorkiwal, M., Sun, S. et al. A chickpea genetic variation map based on the sequencing of 3,366 genomes. Nature 599, 622–627 (2021). https://doi.org/10.1038/s41586-021-04066-1</a>""", unsafe_allow_html=True)

    con = st.container(border=True)
    con.write("### Primer Design:")
    con.write("Primer3 - https://primer3.org/")
    con.write("""<a href="https://pubmed.ncbi.nlm.nih.gov/22730293/" target="_blank">Untergasser A, Cutcutache I, Koressaar T, Ye J, Faircloth BC, Remm M, Rozen SG. Primer3--new capabilities and interfaces. Nucleic Acids Res. 2012 Aug;40(15):e115. doi: 10.1093/nar/gks596. Epub 2012 Jun 22. PMID: 22730293; PMCID: PMC3424584, https://pubmed.ncbi.nlm.nih.gov/22730293/</a>""",unsafe_allow_html=True)

    con=st.container(border=True)
    con.write("### CRISPR Construct:")
    con.write("CHOPCHOP - https://chopchop.cbu.uib.no")
    con.write('<a href="https://pubmed.ncbi.nlm.nih.gov/31106371/" target="_blank">Labun K, Montague TG, Krause M, Torres Cleuren YN, Tjeldnes H, Valen E. CHOPCHOP v3: expanding the CRISPR web toolbox beyond genome editing. Nucleic Acids Res. 2019 Jul 2;47(W1):W171-W174. doi: 10.1093/nar/gkz365. PMID: 31106371; PMCID: PMC6602426. https://pubmed.ncbi.nlm.nih.gov/31106371/</a>', unsafe_allow_html=True)
    
    con = st.container(border=True)
    con.write("### PROMOTER Analysis:")
    con.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
    con.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)

    con=st.container(border=True)
    con.write("### miRNA Target:")
    con.write("PmiREN (Source) - https://pmiren.com")
    con.write("""<a href="https://doi.org/10.1093/nar/gkz894" target="_blank">Guo Z, Kuang Z, Ying Wang Y, Zhao Y, Tao Y, Cheng C, Yang J, Lu X, Hao C, Wang T, Cao X, Wei J, Li L, Yang X, PmiREN: a comprehensive encyclopedia of plant miRNAs, Nucleic Acids Research, Volume 48, Issue D1, 08 January 2020, Pages D1114–D1121, https://doi.org/10.1093/nar/gkz894</a>""",unsafe_allow_html=True)
    con.write("psRNATarget (Target) - https://www.zhaolab.org/psRNATarget/")
    con.write("""(1) <a href="https://doi.org/10.1093/nar/gky316" target="_blank">Dai X, Zhuang Z, Zhao PX. psRNATarget: a plant small RNA target analysis server (2017 release). Nucleic Acids Res. 2018 Jul 2;46(W1):W49-W54. doi: 10.1093/nar/gky316. PMID: 29718424; PMCID: PMC6030838.</a>""",unsafe_allow_html=True)
    con.write("""(2) <a href="https://doi.org/10.1093/nar/gkr319" target="_blank">Dai X, Zhao PX. psRNATarget: a plant small RNA target analysis server. Nucleic Acids Res. 2011 Jul;39(Web Server issue):W155-9. doi: 10.1093/nar/gkr319. Epub 2011 May 27. PMID: 21622958; PMCID: PMC3125753.</a>""",unsafe_allow_html=True)
    con.write("""(3) <a href="https://doi.org/10.1093/bib/bbq065" target="_blank">Dai X, Zhuang Z, Zhao PX. Computational analysis of miRNA targets in plants: current status and challenges. Brief Bioinform. 2011 Mar;12(2):115-21. doi: 10.1093/bib/bbq065. Epub 2010 Sep 21. PMID: 20858738.</a>""",unsafe_allow_html=True)

    con = st.container(border=True)
    con.write("### PlantRegMap:")
    con.write("PlantRegMap - http://plantregmap.gao-lab.org/")
    con.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/31701126/" target="_blank">Tian F, Yang DC, Meng YQ, Jin J, Gao G. PlantRegMap: charting functional regulatory maps in plants. Nucleic Acids Res. 2020 Jan 8;48(D1):D1104-D1113. doi: 10.1093/nar/gkz1020. PMID: 31701126; PMCID: PMC7145545. https://pubmed.ncbi.nlm.nih.gov/31701126/</a>', unsafe_allow_html=True)
    con.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/27924042/" target="_blank">Jin J, Tian F, Yang DC, Meng YQ, Kong L, Luo J, Gao G. PlantTFDB 4.0: toward a central hub for transcription factors and regulatory interactions in plants. Nucleic Acids Res. 2017 Jan 4;45(D1):D1040-D1045. doi: 10.1093/nar/gkw982. Epub 2016 Oct 24. PMID: 27924042; PMCID: PMC5210657. https://pubmed.ncbi.nlm.nih.gov/27924042/</a>', unsafe_allow_html=True)
    con.write('(3) <a href="https://pubmed.ncbi.nlm.nih.gov/25750178/" target="_blank">Jin J, He K, Tang X, Li Z, Lv L, Zhao Y, Luo J, Gao G. An Arabidopsis Transcriptional Regulatory Map Reveals Distinct Functional and Evolutionary Features of Novel Transcription Factors. Mol Biol Evol. 2015 Jul;32(7):1767-73. doi: 10.1093/molbev/msv058. Epub 2015 Mar 6. Erratum in: Mol Biol Evol. 2017 Nov 1;34(11):3039. doi: 10.1093/molbev/msx245. PMID: 25750178; PMCID: PMC4476157. https://pubmed.ncbi.nlm.nih.gov/25750178/</a>', unsafe_allow_html=True)
    
    con = st.container(border=True)
    con.write("### Protein-Protein Interactions (PPI):")
    con.write("STRING v12.0 - https://string-db.org/")
    con.write('<a href="https://pubmed.ncbi.nlm.nih.gov/36370105/" target="_blank">Szklarczyk D, Kirsch R, Koutrouli M, Nastou K, Mehryary F, Hachilif R, Gable AL, Fang T, Doncheva NT, Pyysalo S, Bork P, Jensen LJ, von Mering C. The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. Nucleic Acids Res. 2023 Jan 6;51(D1):D638-D646. doi: 10.1093/nar/gkac1000. PMID: 36370105; PMCID: PMC9825434. https://pubmed.ncbi.nlm.nih.gov/36370105/</a>', unsafe_allow_html=True)

    con = st.container(border=True)
    con.write("### Cellular Localization:")
    con.write("CELLO v.2.5: subCELlular Localization predictor - http://cello.life.nctu.edu.tw/")
    con.write('(1) <a href="https://pubmed.ncbi.nlm.nih.gov/15096640/" target="_blank">Yu CS, Lin CJ, Hwang JK: Predicting subcellular localization of proteins for Gram-negative bacteria by support vector machines based on n-peptide compositions. Protein Science 2004, 13:1402-1406. https://pubmed.ncbi.nlm.nih.gov/15096640/</a>', unsafe_allow_html=True)
    con.write('(2) <a href="https://pubmed.ncbi.nlm.nih.gov/16752418/" target="_blank">Yu CS, Chen YC, Lu CH, Hwang JK, Proteins: Structure, Function and Bioinformatics, 2006, 64:643-651. https://pubmed.ncbi.nlm.nih.gov/16752418/</a>', unsafe_allow_html=True)

    con=st.container(border=True)
    con.write("### Functional Annotation:")
    con.write("GOATOOLS: A Python library for Gene Ontology analyses - https://pypi.org/project/goatools/")
    con.write('<a href="https://www.nature.com/articles/s41598-018-28948-z" target="_blank">Klopfenstein, D.V., Zhang, L., Pedersen, B.S. et al. GOATOOLS: A Python library for Gene Ontology analyses. Sci Rep 8, 10872 (2018). https://doi.org/10.1038/s41598-018-28948-z</a>', unsafe_allow_html=True)
    
    con = st.container(border=True)
    con.write("### Orthologous analysis:")
    con.write("OrthoVenn3 (2022) - https://orthovenn3.bioinfotoolkits.net/") 
    con.write('<a href="https://doi.org/10.1093/nar/gkad313" target="_blank">Sun J, Lu F, Luo Y, Bie L, Xu L, Wang Y, OrthoVenn3: an integrated platform for exploring and visualizing orthologous data across genomes, Nucleic Acids Research, Volume 51, Issue W1, 5 July 2023, Pages W397-W403, https://doi.org/10.1093/nar/gkad313</a>', unsafe_allow_html=True)
    
    con=st.container(border=True)
    con.write("### Machine Learning Backend:")
    con.write("Scikit-learn - https://scikit-learn.org/")
    con.write('<a href="https://jmlr.org/papers/v12/pedregosa11a.html" target="_blank">Pedregosa et al., Scikit-learn: Machine Learning in Python, JMLR 12, pp. 2825-2830, 2011. https://jmlr.org/papers/v12/pedregosa11a.html</a>', unsafe_allow_html=True)

    con=st.container(border=True)
    con.write("### Selenium WebDriver:")
    con.write("Selenium - https://www.selenium.dev/")
    con.write('<a href="https://www.selenium.dev/documentation/en/" target="_blank">Selenium Documentation. Selenium HQ. 2025. https://www.selenium.dev/documentation/en/</a>', unsafe_allow_html=True)

    con=st.container(border=True)
    con.write("### Web Framework:")
    con.write("Streamlit - https://streamlit.io/")
    con.write('<a href="https://streamlit.io/" target="_blank">Streamlit for Teams. Streamlit Inc., 2025. https://streamlit.io/</a>', unsafe_allow_html=True)   
    return

def glossary_page():
    header_styled("Glossary","Key Terms and Definitions")
    glossary_entries = {
        'GS - Germinating Seedling': '- The early stage of seedling development where the seed begins to sprout and grow.',
        'S - Shoot': '- The above-ground part of the plant, including stems, leaves, and flowers.',
        'ML - Mature Leaf': '- A fully developed leaf, which has completed its growth.',
        'YL - Young Leaf': '- A developing leaf that has not yet reached full maturity.',
        'Brac - Bracteole': '- A small leaf-like structure at the base of a flower or inflorescence.',
        'R - Root': '- The part of the plant that anchors it in the soil and absorbs water and nutrients.',
        'Rtip - Root Tip': '- The growing tip of the root, where new cells are produced.',
        'RH - Root Hair': '- Tiny hair-like structures on the root that increase surface area for water absorption.',
        'Nod - Nodule': '- A swollen structure on plant roots, often containing nitrogen-fixing bacteria.',
        'SAM - Shoot Apical Meristem': '- The tissue at the tip of the shoot where growth and development occur.',
        'FB1-FB4 - Stages of Flower Bud Development': '- Sequential stages representing the development of flower buds.',
        'FL1-FL5 - Stages of Flower Development': '- Sequential stages representing the development of flowers.',
        'Cal - Calyx': '- The outermost whorl of a flower, usually consisting of sepals.',
        'Cor - Corolla': '- The petals of a flower, collectively forming the corolla.',
        'And - Androecium': '- The male reproductive part of the flower, consisting of stamens.',
        'Gyn - Gynoecium': '- The female reproductive part of the flower, consisting of pistils.',
        'Pedi - Pedicel': '- The stalk that supports a flower or an inflorescence.',
        'Emb - Embryo': '- The early stage of development of a plant from the fertilized egg cell.',
        'Endo - Endosperm': '- The tissue that provides nourishment to the developing embryo in seeds.',
        'SdCt - Seed Coat': '- The outer protective layer of a seed.',
        'PodSh - Podshell': '- The outer casing that surrounds the seeds within a pod.',
        '5DAP - Seed 5 Days After Pollination': '- The developmental stage of seed five days after pollination.',
        '10DAP - Seed 10 Days After Pollination': '- The developmental stage of seed ten days after pollination.',
        '20DAP - Seed 20 Days After Pollination': '- The developmental stage of seed twenty days after pollination.',
        '30DAP - Seed 30 Days After Pollination': '- The developmental stage of seed thirty days after pollination.',
        'GO - Gene Ontology': '- a framework for the model of biology that describes gene functions in a species-independent manner.',
        'KEGG - Kyoto Encyclopedia of Genes and Genomes': '- a database resource for understanding high-level functions and utilities of biological systems.',
        'FPKM - Fragments per kilobase of transcript per million mapped reads': '- a normalized method for counting RNA-seq reads.',
        'miRNA - MicroRNA': '- small non-coding RNA molecules that regulate gene expression by binding to complementary sequences on target mRNA.',
        'lncRNA - Long Non-Coding RNA': '- a type of RNA molecule that is greater than 200 nucleotides in length but does not encode proteins.',
        'ST - Seed Tissue': '- the tissue in seeds that supports the development of the embryo and storage of nutrients.',
        'FDS - Flower Development Stages': '- the various phases of growth and development that a flower undergoes from bud to bloom.',
        'FP - Flower Parts': '- the various components that make up a flower, including petals, sepals, stamens, and carpels.',
        'GT - Green Tissues': ' - plant tissues that are photosynthetic, primarily found in leaves and stems.',
        'RT - Root Tissues': '- the tissues found in the root system of a plant, involved in nutrient absorption and anchorage.',
        'TF - Transcription Factor': '- a protein that controls the rate of transcription of genetic information from DNA to messenger RNA.',
        'Non-TF - Non-Transcription Factors': '- proteins or molecules that do not directly bind to DNA to initiate or regulate transcription, but still influence gene expression through other mechanisms.',
        'WGCNA - Weighted Gene Co-expression Network Analysis': '- a method for finding clusters (modules) of highly correlated genes and studying their relationships to clinical traits.',
        'PPI - Protein-Protein Interaction': '- physical contacts between two or more proteins that occur in a living organism and are essential for various biological functions, including signal transduction and gene regulation.',
        'SNP CALLING - Single Nucleotide Polymorphism': 'The process of identifying single nucleotide polymorphisms (SNPs) in a genome from sequencing data. SNPs are variations at a single position in the DNA sequence, and SNP calling is crucial for genetic studies and disease association analyses.',
        'PEPTIDE SEQUENCE': 'A sequence of amino acids that make up a peptide, which is a short chain of amino acids linked by peptide bonds.',
        'CDS SEQUENCE - Coding Sequence': '- the portion of a gene\'s DNA or RNA that codes for a protein.',
        'TRANSCRIPT SEQUENCE': 'The RNA sequence transcribed from a gene, which may be translated into a protein or may function as non-coding RNA.',
        'GENOMIC SEQUENCE': 'The complete sequence of nucleotides (DNA or RNA) that make up the entire genome of an organism.'
    }

    con=st.container(border=True)
    search_term = con.text_input("Search Glossary", "")
    
    filtered_entries = {term: definition for term, definition in glossary_entries.items() if search_term.lower() in term.lower() or search_term.lower() in definition.lower()}
    con=st.container(border=True)
    with con:
        for term, definition in filtered_entries.items():
            with st.expander(term):
                st.write(definition)
    return

#@st.cache_data(show_spinner=False)
def get_image_url(image_path):
    return generate_signed_url(image_path)

def meta_data_page():
    #st.title("Statistical Insights")
    #st.write("**Key Insights and Analytics from the Application Backend**")
    header_styled("Statistical Insights","Key Insights and Analytics from the Application Backend")
    # Call charts (no caching needed for these)
    svm_charts()
    con=st.container(border=True)
    # Create 2x2 symmetric layout
    row1_col1, row1_col2 = con.columns(2)
    row2_col1, row2_col2 = con.columns(2)
    
    # Top-left: Text/Subheader
    with row1_col1:
        st.subheader("Initial Voting Classifier Results")
        st.write("Performance metrics for the initial voting classifier model including confusion matrix, precision/recall scores, and ROC-AUC curve analysis.")
        
        st.write("**Key Metrics:**")
        st.write("• **Confusion Matrix**: Shows true vs predicted classifications")
        st.write("• **Precision**: True positives / (True positives + False positives)")
        st.write("• **Recall**: True positives / (True positives + False negatives)")
        st.write("• **F1-Score**: Harmonic mean of precision and recall")
        st.write("• **ROC-AUC**: Area under the receiver operating characteristic curve")
        
        st.write("**Model Performance:**")
        st.write("The voting classifier combines multiple base estimators to improve prediction accuracy and robustness.")
    
    # Top-right: First image
    with row1_col2:
        st.image(get_image_url("Images/11.png"), caption="Confusion Matrix", use_container_width=True)
    
    # Bottom-left: Second image  
    with row2_col1:
        st.image(get_image_url("Images/12.png"), caption="Precision, Recall, F1-Score", use_container_width=True)

    # Bottom-right: Third image
    with row2_col2:
        st.image(get_image_url("Images/23.png"), caption="ROC-AUC Curve", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Combined Confusion Matrix all files")
    # Center the image using columns
    col1, col2, col3 = con.columns([1, 4, 1])
    with col2:
        st.image(get_image_url("Images/29.png"), caption="Confusion Matrix", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Root Tissue Analysis")
    c1,c2=con.columns([5.8,4.2])
    c1.image(get_image_url("Images/14.png"),caption="Precision, Recall, F1-Score", use_container_width=True)
    c2.image(get_image_url("Images/24.png"),caption="ROC-AUC Curve", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Seed Tissue Analysis")
    c1,c2=con.columns([5.8,4.2])
    c1.image(get_image_url("Images/16.png"),caption="Precision, Recall, F1-Score", use_container_width=True)
    c2.image(get_image_url("Images/25.png"),caption="ROC-AUC Curve", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Green Tissue Analysis")
    c1,c2=con.columns([5.8,4.2])
    c1.image(get_image_url("Images/18.png"),caption="Precision, Recall, F1-Score", use_container_width=True)
    c2.image(get_image_url("Images/26.png"),caption="ROC-AUC Curve", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Flower Development Stages Analysis")
    c1,c2=con.columns([5.8,4.2])
    c1.image(get_image_url("Images/20.png"),caption="Precision, Recall, F1-Score", use_container_width=True)
    c2.image(get_image_url("Images/27.png"),caption="ROC-AUC Curve", use_container_width=True)

    con=st.container(border=True)
    con.subheader("Flower Parts Analysis")
    c1,c2=con.columns([5.8,4.2])
    c1.image(get_image_url("Images/22.png"),caption="Precision, Recall, F1-Score", use_container_width=True)
    c2.image(get_image_url("Images/28.png"),caption="ROC-AUC Curve", use_container_width=True)
    tsi_plot()

    # Use cached image URLs
    col1, col2 = st.columns([4,6])
    with col1:
        st.image(get_image_url("Images/1.png"), caption="Expression Data Heatmap", use_container_width=True)
    with col2:    
        st.image(get_image_url("Images/9.png") , caption="Functional Annotation [Flower Parts]", use_container_width=True)

    c1,c2,c3=st.columns([1,4,1])
    with c2:
        st.image(get_image_url("Images/4.png"), caption="Functional Annotation [Root Tissues]", use_container_width=True)
        st.write("")
    
    col3, col4 = st.columns(2)
    with col3:
        st.image(get_image_url("Images/110.png"), caption="Functional Annotation [Seed Tissues]", use_container_width=True)
        st.write("")

    with col4:
        st.image(get_image_url("Images/5.png"), caption="WGCNA Heatmaps", use_container_width=True)
        st.write("")

    col5, col6 = st.columns(2)
    with col5:
        st.image(get_image_url("Images/8.png"), caption="Functional Annotation [Flower Development Stages]", use_container_width=True)
        st.write("")

    with col6:
        st.image(get_image_url("Images/10.png"), caption="Functional Annotation [Green Tissues]", use_container_width=True)
        st.write("")

    # Footer
    #base_footer()
    return


def tutorials_page():
    header_styled("Tutorials", "This page helps you understand how to use the app through video tutorials.")

    # Navigation Tutorial
    st.subheader("Navigation Tutorial")
    st.video("https://youtu.be/wkvhZbtgfvY")

    # Registration and Login Tutorial
    st.subheader("Registration and Login")
    st.video("https://youtu.be/mWVMYyBNlDU")
    st.markdown("""
    1. Navigate to the Login page.
    2. Register for new users.
    3. Login using your credentials.
    4. Unlock Search functionality and additional features.
    """)

    # Single Task Tutorial
    st.subheader("Single Task Tutorial")
    st.video("https://youtu.be/ltAakrOmig0")
    st.markdown("""
    1. Navigate to the **Start Task** page.
    2. Enter the 8-character code when prompted.
    3. Click the **Start** button to begin the task.
    4. Wait for the task to complete and view the results.
    """)

    # Multi Task Tutorial
    st.subheader("Multi Task Tutorial")
    st.video("https://youtu.be/QcCkNOmBU5M")
    st.markdown("""
    1. Navigate to the **Start Task** page.
    2. Enter the 8-character code when prompted.
    3. Click the **Start** button to begin the task.
    4. Wait for the task to complete and view the results.
    """)

    # Glossary Tutorial
    st.subheader("Glossary Tutorial")
    st.video("https://youtu.be/mY4S24c-ADc")

    return


#@st.cache_data(show_spinner=False)
def get_image_url(image_path):
    return generate_signed_url(image_path)

def display_about_content():
    st.title("About Us")
    col1, col2 = st.columns(2)
    
    # Container 1
    st.markdown("""<style>.stVerticalBlock.st-key-au2, .stVerticalBlock.st-key-au1, .stVerticalBlock.st-key-au3, .stVerticalBlock.st-key-au4, .stVerticalBlock.st-key-au5, .stVerticalBlock.st-key-au6 {background-color: rgb(196,91,17); color: white; padding: 20px; border-radius: 10px; transition: all 0.3s ease-in-out;} .stVerticalBlock.st-key-au2:hover, .stVerticalBlock.st-key-au1:hover, .stVerticalBlock.st-key-au3:hover, .stVerticalBlock.st-key-au4:hover, .stVerticalBlock.st-key-au5:hover, .stVerticalBlock.st-key-au6:hover {background-color: rgba(242,240,239,0.5); color: black; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); transform: translateY(-2px);}</style>""", unsafe_allow_html=True)
    con = col1.container(border=False, key="au1")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Dr. Sarvajeet Singh Gill")
        c2.write("Centre for Biotechnology\
                 \nMaharshi Dayanand University, Rohtak, HR, India\
                 \nㅤ")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="https://linktr.ee/techwill",use_container_width=True)
        d3.link_button("Email",url="mailto:ssgill14@mdurohtak.ac.in",use_container_width=True)
    
    # Container 2
    con = col2.container(border=False, key="au2")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Dr. Kamaldeep Joshi")
        c2.write("Department of Computer Science and Technology\
                 \nUniversity Institute of Engineering and Technology,\
                 \nMaharshi Dayanand University, Rohtak, HR, India")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="wwww.google.com",use_container_width=True)
        d3.link_button("Email",url="mailto:kduiet@mdurohtak.ac.in",use_container_width=True)

    # Container 3
    con = col1.container(border=False, key="au3")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Dr. Ritu Gill")
        c2.write("Centre for Biotechnology\
                 \nMaharshi Dayanand University, Rohtak, HR, India\
                 \nㅤ")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="wwww.google.com",use_container_width=True)
        d3.link_button("Email",url="mailto:abc@gmail.com",use_container_width=True)
    
    # Container 4
    con = col2.container(border=False, key="au4")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Dr. Gopal Kalwan")
        c2.write("ICAR - Indian Agricultural Research Institute\
                 \nNew Delhi, India\
                 \nㅤ")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="wwww.google.com",use_container_width=True)
        d3.link_button("Email",url="mailto:abc@gmail.com",use_container_width=True)

    # Container 5
    con = col1.container(border=False, key="au5")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Ms. Ashima Nehra")
        c2.write("Centre for Biotechnology\
                 \nMaharshi Dayanand University, Rohtak, HR, India\
                 \nㅤ")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="wwww.google.com",use_container_width=True)
        d3.link_button("Email",url="mailto:abc@gmail.com",use_container_width=True)
    
    # Container 6
    con = col2.container(border=False, key="au6")
    with con:
        c1, c2 = st.columns([7,13])
        c1.image(get_image_url("About/img.jpg"), use_container_width=True)
        c2.subheader("Mr. Aakash Kharb")
        c2.write("Department of Computer Science and Technology\
                 \nUniversity Institute of Engineering and Technology,\
                 \nMaharshi Dayanand University, Rohtak, HR, India")
        d0,d1,d2,d3,d4=c2.columns([1,5,1,5,1])
        d1.link_button("Profile",url="wwww.google.com",use_container_width=True)
        d3.link_button("Email",url="mailto:akharbrtk@gmail.com",use_container_width=True)
    return

def about_page():
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'STATISTICS'
    
    def set_active_tab(tab_name):
        st.session_state.active_tab = tab_name

    st.write(" ")
    
    #col1, col2, col3, col4, col5 = st.columns(5)
    col2,col3,col4,col5=st.columns(4)
    #if col1.button("ABOUT US", key="btn_about",use_container_width=True):
    #    set_active_tab('ABOUT-US')
    #    st.rerun()
    if col2.button("STATISTICS", key="btn_meta",use_container_width=True):
        set_active_tab('STATISTICS')
        st.rerun()
    if col3.button("CITATIONS", key="btn_citations",use_container_width=True):
        set_active_tab('CITATIONS')
        st.rerun()
    if col4.button("GLOSSARY", key="btn_glossary",use_container_width=True):
        set_active_tab('GLOSSARY')
        st.rerun()
    if col5.button("TUTORIALS", key="btn_tutorials",use_container_width=True):
        set_active_tab('TUTORIALS')
        st.rerun()
        
    if st.session_state.active_tab == 'ABOUT-US':
        display_about_content()
    elif st.session_state.active_tab == 'STATISTICS':
        meta_data_page()
    elif st.session_state.active_tab == 'CITATIONS':
        citations_page()
    elif st.session_state.active_tab == 'GLOSSARY':
        glossary_page()
    elif st.session_state.active_tab == 'TUTORIALS':
        tutorials_page()
    
    base_footer()
    return

if __name__ == "__main__":
    about_page()