import streamlit as st
import pandas as pd
st.set_page_config(layout="centered")
st.header("📌 Final Project")

st.write("The final project aims to apply the knowledge acquired throughout the course to analyze real data and propose a valuable solution for a business.")

st.subheader("📂 Database")

st.write("Students must use the database available in the Streamlit application developed for the class. Although they may complement it with other sources, this database must be included in their analysis.")

st.subheader("📈 Project Requirements")

st.markdown("""
* Business Proposal: Formulate a hypothesis or proposal that represents an opportunity or improvement in a specific sector.

* EDA (Exploratory Data Analysis): Show how the data is organized and distributed.

* Data Science Methodology: Apply at least one technique among:
    * Supervised Learning
    * Unsupervised Learning
    * Natural Language Processing (NLP)
    * Image Analysis

* Visualization and Storytelling: Incorporate visual elements and storytelling to communicate findings.
""")

data = {
    "Criterion": [
        "Data and metadata analysis",
        "EDA (Exploratory Data Analysis)",
        "Business proposal",
        "Implementation of Data Science technique",
        "Data storytelling and visualization",
        "Conclusions and contributions"
    ],
    "Weight": [
        "5%",
        "10%",
        "5%",
        "10%",
        "5%",
        "5%"
    ]
}

df = pd.DataFrame(data)

st.subheader("Evaluation Criteria")

st.table(df.set_index(pd.Index([""] * len(df))))
