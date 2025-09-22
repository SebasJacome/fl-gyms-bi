import streamlit as st
from embedding_atlas.streamlit import embedding_atlas
from embedding_atlas.projection import compute_text_projection
import pandas as pd
import os
from sentence_transformers import SentenceTransformer

os.environ["CUDA_VISIBLE_DEVICES"] = ""
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

if "value" not in st.session_state:
    st.session_state.value = "review"

def review_atlas():
    st.session_state.value = "review"

def tips_atlas():
    st.session_state.value = "tip"

def show_embedding(df):
    compute_text_projection(
        df, text="text", x="embedding_x", y="embedding_y", neighbors="neighbors"
    )
    return embedding_atlas(
        df,
        text="text",
        x="embedding_x",
        y="embedding_y",
        neighbors="neighbors",
        show_charts=False,
        show_embedding=True,
    )

st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 1])
with col1:
    st.button("Reviews", on_click=review_atlas, use_container_width=True)
with col2:
    st.button("Tips", on_click=tips_atlas, use_container_width=True)

df_r = pd.read_parquet("./data/review.parquet")
df_t = pd.read_parquet("./data/tip.parquet")

if st.session_state.value == "review":
    show_embedding(df_r)
elif st.session_state.value == "tip":
    show_embedding(df_t)
