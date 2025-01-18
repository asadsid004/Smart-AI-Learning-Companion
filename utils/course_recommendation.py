import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


st.set_page_config(page_title="Course Recommender", page_icon="📚", layout="wide")


def clean_skills(skills_str):
    """Clean and process skills string into a list of skills."""
    if pd.isna(skills_str):
        return []

    if isinstance(skills_str, list):
        return skills_str

    skills = re.split("[,\n]", str(skills_str))
    skills = [skill.strip(" []\"'") for skill in skills]
    return list(filter(None, set(skills)))


@st.cache_data
def load_data():

    df = pd.read_csv("Coursera.csv")
    df = df.dropna(subset=["Course Name", "Course Description"])

    df["Skills"] = df["Skills"].apply(clean_skills)
    df["skills_string"] = df["Skills"].apply(lambda x: " ".join(x) if x else "")

    df["University"] = df["University"].fillna("Not Specified")
    df["Difficulty Level"] = df["Difficulty Level"].fillna("Not Specified")
    df["Course Rating"] = df["Course Rating"].fillna("No Rating")

    return df


@st.cache_data
def create_similarity_matrix(df):

    combined_features = (
        df["Course Name"]
        + " "
        + df["Course Description"]
        + " "
        + df["skills_string"]
        + " "
        + df["University"]
        + " "
        + df["Difficulty Level"]
    )

    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(combined_features)
    return cosine_similarity(tfidf_matrix)


def get_recommended_courses(df, course_index, similarity_scores, n=5):
    """Get recommended courses based on similarity scores."""
    course_scores = similarity_scores[course_index]
    similar_indices = np.argsort(course_scores)[::-1][1 : n + 1]
    return df.iloc[similar_indices]


def search_courses(df, search_query):
    """Search courses based on title and description."""
    if not search_query:
        return pd.DataFrame()

    mask = (
        df["Course Name"].str.contains(search_query, case=False, na=False)
        | df["Course Description"].str.contains(search_query, case=False, na=False)
        | df["skills_string"].str.contains(search_query, case=False, na=False)
    )
    return df[mask].head(10)


def display_course_details(course, recommended_courses):
    """Display detailed course information and recommendations."""
    st.header(course["Course Name"])

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write(f"**University:** {course['University']}")
        st.write(f"**Difficulty Level:** {course['Difficulty Level']}")
    with col2:
        st.write(f"**Rating:** {course['Course Rating']}")
        st.write(f"**Skills:** {', '.join(course['Skills'])}")

    st.write("**Description:**")
    st.write(course["Course Description"])

    if not pd.isna(course["Course URL"]):
        st.markdown(f"[Go to Course Page]({course['Course URL']})")

    st.header("Recommended Courses:")
    cols = st.columns(2)
    for idx, (_, rec_course) in enumerate(recommended_courses.iterrows()):
        with cols[idx % 2]:
            with st.container():
                st.markdown("---")

                if st.button(
                    f"📚 {rec_course['Course Name']}",
                    key=f"rec_{rec_course.name}",
                    help="Click to view course details",
                ):
                    st.session_state.selected_course_index = rec_course.name
                    st.rerun()

                st.write(f"**University:** {rec_course['University']}")
                st.write(f"**Difficulty Level:** {rec_course['Difficulty Level']}")
                st.write(f"**Rating:** {rec_course['Course Rating']}")

                desc = rec_course["Course Description"]
                if len(desc) > 200:
                    st.write(f"{desc[:200]}...")
                else:
                    st.write(desc)
