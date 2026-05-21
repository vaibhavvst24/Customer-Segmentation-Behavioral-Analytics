import streamlit as st
from streamlit_option_menu import option_menu

from app import show_eda
from model import show_model


st.set_page_config(
    page_title="CustomerIQ",
    layout="wide",
    page_icon="🧑🏻"
)

# Load CSS
def load_css():
    with open("assests/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("Customer Behavior Analytics Platform")

selected = option_menu(
    menu_title=None,
    options=["EDA Dashboard", "ML Dashboard"],
    icons=["bar-chart", "cpu"],
    orientation="horizontal"
)

if selected == "EDA Dashboard":
    show_eda()

elif selected == "ML Dashboard":
    show_model()