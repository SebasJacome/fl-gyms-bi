import streamlit as st
import os

IMG_DIR = "./data/outputs_nlp"

st.set_page_config(layout="wide")

wordclouds = [
    ("Bad Reviews — Uni+Bi+Tri", "wc_bad_all.png"),
    ("Good Reviews — Uni+Bi+Tri", "wc_good_all.png"),
    ("Bad — Unigrams", "wc_bad_uni.png"),
    ("Bad — Bigrams", "wc_bad_bi.png"),
    ("Bad — Trigrams", "wc_bad_tri.png"),
    ("Good — Unigrams", "wc_good_uni.png"),
    ("Good — Bigrams", "wc_good_bi.png"),
    ("Good — Trigrams", "wc_good_tri.png"),
]

st.title("☁️️ NLP — Wordcloud Analysis")
st.markdown("---")

st.subheader("General Overview — Good vs Bad Reviews")
col1, col2 = st.columns(2)
with col1:
    st.subheader(wordclouds[0][0])
    st.image(os.path.join(IMG_DIR, wordclouds[0][1]))
with col2:
    st.subheader(wordclouds[1][0])
    st.image(os.path.join(IMG_DIR, wordclouds[1][1]))

st.markdown("---")

st.subheader("Details of Bad Reviews")
bad_cols = st.columns(3)
for i, (title, file_name) in enumerate(wordclouds[2:5]):
    with bad_cols[i % 3]:
        st.subheader(title)
        st.image(os.path.join(IMG_DIR, file_name))

st.markdown("---")

st.subheader("Details of Good Reviews")
good_cols = st.columns(3)
for i, (title, file_name) in enumerate(wordclouds[5:]):
    with good_cols[i % 3]:
        st.subheader(title)
        st.image(os.path.join(IMG_DIR, file_name))

