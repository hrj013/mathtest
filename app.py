import pathlib
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(
    page_title="하수관 관제일지 // Gradient Descent",
    page_icon="🚰",
    layout="wide",
    initial_sidebar_state="collapsed",
)# Hide default Streamlit chrome for an immersive indie game frame
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.5rem;
            max-width: 1040px;
        }
        body {
            background-color: #0d0b14;
        }
    </style>
    """,
    unsafe_allow_html=True,
)html_path = pathlib.Path(__file__).parent / "assets" / "game_view.html"
game_html = html_path.read_text(encoding="utf-8")
components.html(game_html, height=705, scrolling=False)
