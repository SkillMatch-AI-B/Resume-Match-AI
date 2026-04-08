import streamlit as st
from sentence_transformers import SentenceTransformer, util

@st.cache_resource
def load_bert():
    # Loads the lightweight MiniLM model
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(resume_text, jd_text):
    model = load_bert()
    emb1 = model.encode(resume_text, convert_to_tensor=True)
    emb2 = model.encode(jd_text, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2)
    return round(float(score[0][0]) * 100, 2)