import streamlit as st


st.sidebar.header("Business Intelligence")
st.sidebar.text("@ Universidad Panamericana")

st.sidebar.image("./assets/logo_up.png")

pages = {
    "Visualizations": [
        st.Page("./pages/overview.py", title="Overview"),
        st.Page("./pages/franchise.py", title="Franchise"),
    ],
    "Methodology": [
        st.Page("./pages/atlas.py", title="Atlas"),
        st.Page("./pages/nlp.py", title="NLP"),
    ],
    "About": [
        st.Page("./pages/project.py", title="Project"),
        st.Page("./pages/team.py", title="Us"),
    ]
}

pg = st.navigation(pages, expanded=True)

st.title("Florida Gyms")

pg.run()
