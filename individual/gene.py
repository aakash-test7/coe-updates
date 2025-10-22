import streamlit as st
from backend import process_locid, process_mlocid, show_sequence_data,df, show_biochemical_properties, mlocid_error,header_styled
from pages.footer import base_footer

def gene_info_page():
    st.markdown("""<style>.block-container {padding-top: 4rem;}</style>""", unsafe_allow_html=True)
    if "first_gene_visit" not in st.session_state:
        st.session_state["first_gene_visit"] = True
    # Show "Back to Home" button if navigation was programmatic
    if st.session_state.get("programmatic_nav", False):
        c1,c2,c3,c4=st.columns(4)
        if c1.button("← Back to Home", key="back_to_home_gene", type="secondary"):
            st.session_state["programmatic_nav"] = False
            st.session_state["current_page"] = "HOME"
            st.session_state["first_gene_visit"] = True
            st.rerun()
    
    header_styled("Gene Information Search", "It gives detailed insights about each Genomic Sequence, RNA Sequence, CDS Sequence, Promoter Sequences, Protein Sequence and biochemical properties of each protein.")
    col1, col2 = st.columns(2)

    with col1:
        con1 = st.container(border=True)
        tid = con1.text_input("Enter the Gene ID: ", placeholder="e.g., Ca_00001", key="ginfo_Tid_input1").strip()
        mtid = con1.text_input("Enter multiple Gene IDs: ", placeholder="e.g., Ca_00001, Ca_00002", key="ginfo_mTid_input2").strip()
        if mtid:
            mtid_list = [item.strip() for item in mtid.replace(",", " ").split()]
            mtid_list = list(set(mtid_list))
            mtid = ",".join(mtid_list)

    with col2:
        con2 = st.container(border=True)
        locid = con2.text_input("Enter the NCBI ID: ", placeholder="e.g., LOC101511858", key="ginfo_Locid_input1").strip()
        mlocid = con2.text_input("Enter multiple NCBI IDs: ", placeholder="e.g., LOC101511858, LOC101496413", key="ginfo_mLocid_input2").strip()
        if mlocid:
            mlocid_list = [item.strip() for item in mlocid.replace(",", " ").split()]
            mlocid_list = list(set(mlocid_list))
            mlocid = ",".join(mlocid_list)

    con1, con2, con3 = st.columns([2, 2, 2])
    with con2:
        start_button = st.button("Search", use_container_width=True, key="ginfo_Searchbutton1")
    # Main logic for Streamlit interface
    if st.session_state.get("programmatic_nav", False) and tid == "" and mtid == "" and locid == "" and mlocid == "" and st.session_state.get("first_gene_visit", True):
        con= st.container(border=True)
        st.session_state["first_gene_visit"] = False
        temp_list = st.session_state.get("site_search_input_transcript")
        st.session_state["site_search_input_transcript"] = []
        if temp_list:   
            with con:
                st.subheader("Sequence data")
                show_sequence_data(temp_list, is_multi=True) if len(temp_list) > 1 else show_sequence_data(temp_list[0])
                c1,c2=con.columns(2)
                with c1.popover("Data Source", use_container_width=True):
                    st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                    st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                with c2.popover("Research Article", use_container_width=True):
                    st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                    st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)
    
                st.subheader("Biochemical Properties")
                show_biochemical_properties(temp_list, is_multi=True) if len(temp_list) > 1 else show_biochemical_properties(temp_list[0])
        #st.toast("Task completed successfully.")

    elif start_button:
        if tid:
            matching_row = df[df['Transcript id'] == tid]

            if not matching_row.empty:
                con=st.container(border=True)
                with con:
                    st.subheader("Sequence data")
                    show_sequence_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                        st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)

                    st.subheader("Biochemical Properties")
                    show_biochemical_properties(tid)
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
                    show_sequence_data(mtid_list, is_multi=True)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                        st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)

                    st.subheader("Biochemical Properties")
                    show_biochemical_properties(mtid_list, is_multi=True)

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
                    show_sequence_data(tid)
                    c1,c2=con.columns(2)
                    with c1.popover("Data Source", use_container_width=True):
                        st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                        st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                    with c2.popover("Research Article", use_container_width=True):
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                        st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)

                    st.subheader("Biochemical Properties")
                    show_biochemical_properties(tid)
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
                        show_sequence_data(mtid_list, is_multi=True)
                        c1,c2=con.columns(2)
                        with c1.popover("Data Source", use_container_width=True):
                            st.write("Phytozome v13 - https://phytozome-next.jgi.doe.gov/")
                            st.write("PlantCARE, a database of plant cis-acting regulatory elements - http://bioinformatics.psb.ugent.be/webtools/plantcare/html/")
                        with c2.popover("Research Article", use_container_width=True):
                            st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/22110026/" target="_blank">David M. Goodstein, Shengqiang Shu, Russell Howson, Rochak Neupane, Richard D. Hayes, Joni Fazo, Therese Mitros, William Dirks, Uffe Hellsten, Nicholas Putnam, and Daniel S. Rokhsar, Phytozome: a comparative platform for green plant genomics, Nucleic Acids Res. 2012 40 (D1): D1178-D1186. https://pubmed.ncbi.nlm.nih.gov/22110026/</a>', unsafe_allow_html=True)
                            st.write('<a href="https://pubmed.ncbi.nlm.nih.gov/11752327/" target="_blank">Lescot M, Déhais P, Thijs G, Marchal K, Moreau Y, Van de Peer Y, Rouzé P, Rombauts S. PlantCARE, a database of plant cis-acting regulatory elements and a portal to tools for in silico analysis of promoter sequences. Nucleic Acids Res. 2002 Jan 1;30(1):325-7. doi: 10.1093/nar/30.1.325. PMID: 11752327; PMCID: PMC99092. https://pubmed.ncbi.nlm.nih.gov/11752327/</a>', unsafe_allow_html=True)

                        st.subheader("Biochemical Properties")
                        show_biochemical_properties(mtid_list, is_multi=True)
                st.toast("Task completed successfully.")
            if rejected:
                st.error(f"No matches found for NCBI IDs: {', '.join(rejected)}")

            st.toast("Task completed successfully.")
            
    elif tid == "":
        st.warning("Need Gene ID to proceed.")
    else:
        st.write("Press the 'Search' button to begin ...")
        st.write("Follow the instructions or check out tutorials")

    base_footer()
    return

if __name__ == "__main__":
    gene_info_page()