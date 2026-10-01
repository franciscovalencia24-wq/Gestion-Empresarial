import streamlit as st
import pandas as pd

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({'ID': [1], 'Name': ['A'], 'Monto Neto': [100.0]})

edited = st.data_editor(st.session_state.df, num_rows="dynamic", hide_index=True)

if st.button('Save'):
    st.write(edited)
    for idx, row in edited.iterrows():
        m_id = row.get("ID")
        st.write(f"ID type: {type(m_id)}, value: {m_id}, pd.notna: {pd.notna(m_id)}")
