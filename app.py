import streamlit as st
import psycopg2
import pandas as pd

# Database Connection
def create_connection():
    return psycopg2.connect(
        host='localhost',
        database='spotifytrackdb',
        user='postgres',
        password='123456',
        port="5432"
    )

# Streamlit App Starts Here
st.set_page_config(page_title="Spotify Trend Analysis", page_icon="🎵", layout="wide")

# Fancy Landing Page
st.markdown("""
    # 🎵 Spotify Trend Analysis Dashboard
    Welcome to the **Spotify Trend Analysis Project**.
    Analyze song trends, artist popularity, regional streaming statistics, and even run your own SQL queries!
    ---
""")

# Display Project Objective from Milestone1.pdf
with st.expander("📄 Project Overview (Click to Expand)"):
    st.markdown("""
    ## Project Details
    **Project Name**: Spotify Trend Analysis  
    **Team Members**: Srujan Avirneni (50496924), Saket Medhalavalasa (50594502)

    ## Problem Statement
    Spotify generates an enormous amount of data about music streaming, artist performance, album trends, and regional preferences.
    Analyzing this data requires structured storage and efficient querying. Excel spreadsheets lack scalability, while SQL databases 
    allow scalable storage and complex queries to derive meaningful insights.

    ## Project Goal
    Build a Spotify Streaming Insights Database to help music analysts, record labels, and independent artists track and analyze song trends across different regions.
    Key data points include artist details, album releases, song popularity, regional trends, and track features like energy, danceability, and loudness.

    ## Target Users
    - 🎯 **Music Industry Analysts**
    - 🎯 **Market Researchers**
    - 🎯 **Database Administrators**

    ## Real-Life Scenario
    Analysts track daily updates of top songs across 73 countries to predict trends, recommend content, and strategize market expansion, 
    while ensuring data integrity and security.

    ---
    """, unsafe_allow_html=True)

# Sidebar Navigation
option = st.sidebar.selectbox(
    'Choose a Feature',
    ('🏠 Home', '🔥 Top Songs', '🎤 Popular Artists', '🌎 Regional Trends', '🛠 Custom SQL Query')
)

# Connect to DB
conn = create_connection()
cursor = conn.cursor()

# Home Page
if option == '🏠 Home':
    st.header("Welcome! 🎉")
    st.subheader("Use the sidebar to navigate different features.")

# Top Songs
elif option == '🔥 Top Songs':
    st.header("🔥 Top Songs Based on Popularity")
    cursor.execute("""
        SELECT s.title, SUM(ss.popularity) AS total_popularity
        FROM songs s
        JOIN streaming_stats ss ON s.song_id = ss.song_id
        GROUP BY s.title
        ORDER BY total_popularity DESC
        LIMIT 10;
    """)
    df = pd.DataFrame(cursor.fetchall(), columns=['Song', 'Total Popularity'])
    st.dataframe(df)
    st.bar_chart(df.set_index('Song'))

# Popular Artists
elif option == '🎤 Popular Artists':
    st.header("🎤 Most Popular Artists by Number of Songs")
    cursor.execute("""
        SELECT ar.name, COUNT(s.song_id) AS num_songs
        FROM artists ar
        JOIN albums al ON ar.artist_id = al.artist_id
        JOIN songs s ON al.album_id = s.album_id
        GROUP BY ar.name
        ORDER BY num_songs DESC
        LIMIT 10;
    """)
    df = pd.DataFrame(cursor.fetchall(), columns=['Artist', 'Number of Songs'])
    st.dataframe(df)
    st.bar_chart(df.set_index('Artist'))

# Regional Trends
elif option == '🌎 Regional Trends':
    st.header("🌎 Explore Regional Trends")
    cursor.execute("SELECT DISTINCT name FROM countries ORDER BY name;")
    countries_list = [row[0] for row in cursor.fetchall()]
    
    selected_country = st.selectbox("Select a Country:", countries_list)
    
    if selected_country:
        cursor.execute("""
            SELECT s.title, ss.date, ss.popularity
            FROM songs s
            JOIN streaming_stats ss ON s.song_id = ss.song_id
            JOIN countries c ON ss.country_id = c.country_id
            WHERE c.name = %s
            ORDER BY ss.popularity DESC
            LIMIT 10;
        """, (selected_country,))
        df = pd.DataFrame(cursor.fetchall(), columns=['Song', 'Date', 'Popularity'])
        st.dataframe(df)

# Custom SQL Query
elif option == '🛠 Custom SQL Query':
    st.header("🛠 Run Your Own SQL Query")
    st.write("⚡ You can run any SQL query. (Be careful: this can modify data!)")
    
    user_query = st.text_area("Enter your SQL query here:", height=150)

    if st.button("Execute Query"):
        if user_query.strip() != "":
            try:
                cursor.execute(user_query)
                if cursor.description:  # if SELECT query
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(results, columns=columns)
                    st.dataframe(df)
                else:  # if DML query (INSERT/UPDATE/DELETE)
                    conn.commit()
                    st.success("✅ Query executed successfully!")
            except Exception as e:
                st.error(f"❌ Error executing query: {e}")

# Close DB Connection
cursor.close()
conn.close()
