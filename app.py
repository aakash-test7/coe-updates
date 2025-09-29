import streamlit as st
st.set_page_config(page_title="ChickpeaOmicsExplorer", layout="wide",initial_sidebar_state="expanded")
from streamlit_navigation_bar import st_navbar
import pages as pg
import time
from pages.security import basic_stats, update_visitor_count
import individual

pages = ["HOME", "SEARCH", "Tissue-Specific Expression", "RNA-type", "miRNA-target","Transcription Factors", "PPI", "Localization", "GO-KEGG", "ORTHOLOGS/PARALOGS", "ABOUT US", "LOGIN"]
logo_path = ("logo1.svg")
options={"use_padding": True, "show_menu":False}

styles = {
    "nav": {
        "background-color": "rgb(197, 91, 17)",  # Background color of the navigation bar
        "height": "4rem",  # Set the total height of the navigation bar
        "display": "flex",  # Use flexbox for layout
        "align-items": "center",  # Vertically center the items
        "justify-content": "space-between",  # Space out the items evenly
        "padding": "0 1rem",  # Add padding to the left and right of the navigation bar
    "overflow-x": "auto",  # Enable horizontal scrolling if the content overflows
    "overflow-y": "hidden",  # Disable vertical scrolling in the navbar
        "white-space": "nowrap",  # Prevent items from wrapping to a new line
        "text-color": "rgba(255,255,255,1)",
    },
    "div": {
        "width": "100%",
        "display": "flex",  # Use flexbox for layout
    },
    "span": {
        "border-radius": "0.5rem",  # Rounded corners for the headings
        "margin": "0 0.125rem",  # Margin around each heading
        "padding": "0.4375rem 0.625rem",  # Padding inside each heading
        "font-size": "1.1rem",  # Increase the font size of the headings
        "font-weight": "bold",  # Make the headings bold
        "color": "white",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",  # Background color for the active heading
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",  # Background color on hover
    },
    "img": {
        "height": "5rem",  # Logo height
        "width": "12rem",   # Logo width
    },
}
st.markdown("""
        <style>
               .block-container {
                    padding-top: 3.5rem;
                    padding-bottom: 2rem;
                    padding-left: 3rem;
                    padding-right: 3rem;
                }
        </style>
        """, unsafe_allow_html=True)

if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"
page = st_navbar(pages, logo_path=logo_path, styles=styles, options=options,logo_page="HOME")

# Logic for redirecting to login or setting pages
if st.session_state.get("redirect_to_login", False):
    st.session_state.current_page = "LOGIN"
    st.session_state.programmatic_nav = False
elif st.session_state.get("redirected_to_login", True) is False:
    if "first_time" not in st.session_state or st.session_state.first_time:
        st.session_state.current_page = "SEARCH"
        st.session_state.first_time = False
        st.session_state.programmatic_nav = False
else:
    if "last_navbar_page" not in st.session_state:
        st.session_state.last_navbar_page = "HOME"
    
    if page != st.session_state.last_navbar_page and page in pages:
        st.session_state.current_page = page
        st.session_state.programmatic_nav = False
        st.session_state.last_navbar_page = page
    elif not st.session_state.get("programmatic_nav", False):
        if page in pages:
            st.session_state.current_page = page
            st.session_state.last_navbar_page = page

external_links = {
    "Legume Information System": "https://www.legumeinfo.org/",
    "Pulse Crop Database": "https://www.pulsedb.org/main",
    "Legumepedia":"https://cegresources.icrisat.org/legumepedia/index.php",
    "Phytozome": "https://phytozome-next.jgi.doe.gov/",
    "NCBI": "https://www.ncbi.nlm.nih.gov/",
    "Ensemble Plants": "https://plants.ensembl.org/index.html",
    "SoyBase": "https://www.soybase.org/",
    "Gramene": "https://www.gramene.org/",
    "GrainGenes": "https://wheat.pw.usda.gov/",
    "MaizeGDB": "https://www.maizegdb.org/",
    "Rice Database": "https://shigen.nig.ac.jp/rice/oryzabase/locale/change?lang=en",
    "TAIR": "https://www.arabidopsis.org",
    "Cassavabase": "https://www.cassavabase.org",
}

from backend import img_to_base64
with open("logo1.png", "rb") as img_file:
        img_data = img_file.read()
img_sidebar=img_to_base64(img_data)
st.sidebar.image(f"data:image/png;base64,{img_sidebar}", use_container_width=True)
st.sidebar.markdown("""
    <h3 style="text-align: center; font-size: 1.25rem;">Important Resources</h3>
""", unsafe_allow_html=True)
for name, link in external_links.items():
    st.sidebar.markdown(
f'<a href="{link}" target="_blank" class="sidebar-button" style="text-decoration: none; background-color: rgb(197,91,17); color: black; font-weight: bold;" onmouseover="this.style.textDecoration=\'none\'; this.style.color=\'black\';" onmouseout="this.style.textDecoration=\'none\'; this.style.color=\'black\';">{name}</a>',
        unsafe_allow_html=True)
    
#visitor
if 'first_access' not in st.session_state:
    st.session_state.first_access = True
if 'visitor_count' not in st.session_state:
    st.session_state.visitor_count = 0
if 'display_count' not in st.session_state:
    st.session_state.display_count = True

if st.session_state.first_access:
    st.session_state.visitor_count = update_visitor_count()
    st.session_state.member, st.session_state.search=basic_stats()

if st.session_state.display_count:
    st.toast(f"Visitor Count : {st.session_state.visitor_count}")
    st.session_state.display_count = False

visitor_placeholder = st.sidebar.empty()

if st.session_state.get("authenticated",False):
    visitor_placeholder.metric(value=st.session_state.visitor_count, label="Total Visitors", border=True)
    col1,col2=st.sidebar.columns(2)
    member_placeholder = col1.empty()
    search_placeholder = col2.empty()
    if st.sidebar.button("Site Sync"):
        st.session_state.member, st.session_state.search=basic_stats()
        st.session_state.visitor_count = update_visitor_count()
        visitor_placeholder.metric(value=st.session_state.visitor_count, label="Total Visitors", border=True)
    member_placeholder.metric(value=st.session_state.member, label="Total Members", delta=None, border=True)
    search_placeholder.metric(value=st.session_state.search, label="Total Searches", delta=None, border=True)
    if st.sidebar.button("Logout",key="logout_sidebar"):
        st.session_state["logged_in"] = False
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.success("You have been logged out successfully!")
        time.sleep(2)
        st.rerun()

else:
    visitor_placeholder.metric(value=st.session_state.visitor_count, label="Total Visitors", border=True)

    if st.sidebar.button("Site Sync", key="non-member"):
        st.session_state.visitor_count = update_visitor_count()
        visitor_placeholder.metric(value=st.session_state.visitor_count, label="Total Visitors", border=True)
        st.toast(f"Total visitors: {st.session_state.visitor_count}")

st.markdown(
    """
    <style>
        @media (max-width: 900px) {
            .stNavBar-nav {
                overflow-x: scroll;  /* Enable scrolling on smaller screens */
                flex-wrap: nowrap;    /* Prevent wrapping of items */
                padding: 0.5rem;      /* Adjust padding for mobile */
            }
            .stNavBar-span {
                font-size: 0.9rem;      /* Slightly reduce font size for mobile */
            }
        }
        .stSidebar {
        background-color: #e6c4aeff;
    }
        .sidebar-button {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            color: white;
            background-color: #833c0d; /* Dark Red */
            border: 2px solid #5a2a09;
            border-radius: 15px;
            cursor: pointer;
            margin-bottom: 5px;
            text-align: center;
            display: block;
            text-decoration: none;
            transition: all 0.3 ease;
        }

        .sidebar-button:hover {
            background-color: rgb(197,91,17);
            border-color: #c97b4b;
        }

        .stButton>button:hover p {
            color: white !important; /* Keep text visible */
        }
        .stButton>button {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            color: white;
            background-color: #833c0d; /* Dark Red */
            border: 0px solid #5a2a09;
            border-radius: 15px;
            cursor: pointer;
            margin-bottom: 5px;
            text-align: center;
            display: block;
            text-decoration: none;
            transition: all 0.3 ease;
        }

        .stButton>button:hover {
            background-color: rgb(197,91,17);
            border-color: #c97b4b;
        }
        .stTextInput input{
            color: white !important;
        }
        
        .stTextInput input::placeholder {
            color: lightgray !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
functions = {
    "HOME": pg.home_page,
    "SEARCH": pg.search_page,
    "GENE-INFO": individual.gene_info_page,
    "Tissue-Specific Expression": individual.spatial_info_page,
    "RNA-type": individual.rna_type_page,
    "miRNA-target": individual.mirna_info_page,
    "PPI": individual.ppi_info_page,
    "Localization": individual.local_info_page,
    "GO-KEGG": individual.go_info_page,
    "SNP-CALLING": individual.snp_info_page,
    "ORTHOLOGS/PARALOGS": individual.orthologs_info_page,
    "ABOUT US": pg.about_page,
    "LOGIN": pg.login_page,
    "PRIMER": individual.primer_info_page,
    "CRISPR": individual.crispr_info_page,
    "Transcription Factors": individual.tf_info_page
}

go_to = functions.get(st.session_state.current_page)
if go_to:
    go_to()
