import streamlit as st
from individual.crispr import crispr_info_page
from individual.primer import primer_info_page

def tools_page():
    if 'active_tab_tools' not in st.session_state:
        st.session_state.active_tab_tools = 'PrimerDesign'
    
    def set_active_tab(tab_name):
        st.session_state.active_tab_tools = tab_name

    st.write(" ")
    
    col1,col2=st.columns(2)
    if col1.button("Primer Design", key="btn_pd",use_container_width=True):
        set_active_tab('PrimerDesign')
        st.rerun()
    if col2.button("CRISPR Construct", key="btn_cc",use_container_width=True):
        set_active_tab('CRISPRConstruct')
        st.rerun()

    if st.session_state.active_tab_tools == 'PrimerDesign':
        primer_info_page()
    elif st.session_state.active_tab_tools == 'CRISPRConstruct':
        crispr_info_page()
    
    return

if __name__ == "__main__":
    tools_page()