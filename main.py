import streamlit as st
from youtube_comments import youtube_comments_feature
from chat_interface import chat_interface_feature
from pdf_upload import pdf_upload_feature

st.title("YouTube Comments Extractor and Query System")

with st.sidebar:
    st.header("Features")
    feature = st.radio("Select Feature", ["Fetch YouTube Comments", "Chat Interface", "PDF Upload"])

if feature == "Fetch YouTube Comments":
    youtube_comments_feature()
elif feature == "Chat Interface":
    chat_interface_feature()
elif feature == "PDF Upload":
    pdf_upload_feature()
