"""Streamlit entry point for Phase 1 demo."""
import pathlib
import streamlit as st

STATIC_DIR = pathlib.Path(__file__).parent / "static"

st.set_page_config(page_title="Patient Profiling", page_icon=str(STATIC_DIR / "favicon.svg"))

# Load custom CSS
css_path = STATIC_DIR / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.title("Patient Profiling System (Phase 1)")

st.write("This is a placeholder UI. Functionality will be implemented in later phases.")
