from utils.course_recommendation import (
    load_data,
    create_similarity_matrix,
    get_recommended_courses,
    display_course_details,
    search_courses,
)
import streamlit as st


def main():
    try:

        df = load_data()
        similarity_scores = create_similarity_matrix(df)

        st.title("📚 Course Search and Recommender")

        st.write("Search for courses by title, description, or skills:")
        search_query = st.text_input(
            "",
            placeholder="Enter keywords to search courses...",
            help="Type keywords and press Enter to search",
        )

        if "selected_course_index" in st.session_state:

            selected_course = df.iloc[st.session_state.selected_course_index]
            recommended_courses = get_recommended_courses(
                df, st.session_state.selected_course_index, similarity_scores
            )

            if st.button("← Back to Search"):
                del st.session_state.selected_course_index
                st.rerun()

            display_course_details(selected_course, recommended_courses)

        else:

            if search_query:
                results = search_courses(df, search_query)

                if len(results) == 0:
                    st.info(
                        "No courses found matching your search. Try different keywords."
                    )
                else:
                    st.subheader(f"Search Results ({len(results)} courses found)")
                    for idx, row in results.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button(
                                f"📘 {row['Course Name']}", key=f"course_{idx}"
                            ):
                                st.session_state.selected_course_index = idx
                                st.rerun()
                        with col2:
                            st.write(f"by {row['University']}")
            else:
                st.info("Enter keywords above to search for courses.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your data format and try again.")


main()
