import streamlit as st
import psycopg2
import pandas as pd
import os
def create_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ.get('DB_PORT', 5432)
    )
st.set_page_config(page_title="Spotify Trend Analysis", layout="wide")
st.title("Spotify Trend Analysis Dashboard")
st.markdown("""
Welcome to the Spotify Trend Analysis Project Dashboard.
Analyze song trends, artist popularity, regional streaming statistics, and run queries based on your access level.
---
""")
user_type = st.sidebar.selectbox("Select User Type", ("User", "Admin"))

is_admin = False

if user_type == "Admin":
    admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
    if admin_password == "admin123":
        st.sidebar.success("Admin login successful.")
        is_admin = True
    else:
        st.sidebar.error("Incorrect password. Only read access is allowed.")
option = st.sidebar.selectbox(
    'Choose a Feature',
    ('Home', 'Top Songs', 'Popular Artists', 'Regional Trends', 'Custom SQL Query')
)
conn = create_connection()
cursor = conn.cursor()
if option == 'Home':
    st.header("Home")
    st.write("Use the sidebar to navigate to different features.")
elif option == 'Top Songs':
    st.header("Top Songs Based on Popularity")
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


elif option == 'Popular Artists':
    st.header("Most Popular Artists by Number of Songs")
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


elif option == 'Regional Trends':
    st.header("Explore Regional Trends")
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


elif option == 'Custom SQL Query':
    st.header("Run Your Own SQL Query")

    if is_admin:
        st.write("Access Level: Admin (Full Access)")
    else:
        st.write("Access Level: User (Only SELECT queries are allowed)")

    user_query = st.text_area("Enter your SQL query below:", height=150)

    if st.button("Execute Query"):
        if user_query.strip() != "":
            try:
                if not is_admin:
                    if not user_query.strip().lower().startswith("select"):
                        st.error("As a User, you can only run SELECT queries.")
                    else:
                        cursor.execute(user_query)
                        results = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                        df = pd.DataFrame(results, columns=columns)
                        st.dataframe(df)
                else:
                    cursor.execute(user_query)
                    if cursor.description:
                        results = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                        df = pd.DataFrame(results, columns=columns)
                        st.dataframe(df)
                    else:
                        conn.commit()
                        st.success("Query executed successfully.")
            except Exception as e:
                st.error(f"Error executing query: {e}")

cursor.close()
conn.close()
