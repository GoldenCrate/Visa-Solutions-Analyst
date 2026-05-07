import pandas as pd
import streamlit as st
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@st.cache_data
def load_market():
    df = pd.read_csv(os.path.join(DATA_DIR, "market_landscape.csv"), parse_dates=["month"])
    return df


@st.cache_data
def load_clients():
    return pd.read_csv(os.path.join(DATA_DIR, "client_profiles.csv"))
