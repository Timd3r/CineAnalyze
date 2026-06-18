# app.py
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Set up page configurations
st.set_page_config(page_title="CineAnalyze Studio Dashboard", layout="wide")

# Helper function to connect to your Docker PostgreSQL database
def get_db_data(query):
    conn = psycopg2.connect(
        dbname="movie_db", 
        user="tde-raev", 
        password="Password", 
        host="localhost", 
        port="5432"
    )
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 1. Title Block
st.title("CineAnalyze Executive Dashboard")
st.markdown("Real-time financial analytics and metric tracking for studio release strategies.")
st.markdown("---")

# 2. Sidebar Filters (Data Analysis core concept: Interactivity)
st.sidebar.header("Dashboard Controls")

# Fetch unique genres for the filter dropdown directly from the DB
genres_df = get_db_data("SELECT genre_name FROM genres ORDER BY genre_name;")
genre_list = ["All Genres"] + list(genres_df["genre_name"])
selected_genre = st.sidebar.selectbox("Filter by Primary Genre", genre_list)

# 3. Build Dynamic SQL Queries based on user filter
where_clause = ""
if selected_genre != "All Genres":
    # SQL logic to filter movies linked to the chosen genre via the junction table
    where_clause = f"""
        WHERE m.movie_id IN (
            SELECT movie_id FROM movie_genres mg 
            JOIN genres g ON mg.genre_id = g.genre_id 
            WHERE g.genre_name = '{selected_genre}'
        )
    """

# Core metrics query (Aggregations)
metrics_query = f"""
    SELECT 
        COUNT(movie_id) as total_movies,
        SUM(budget) as total_budget,
        SUM(revenue) as total_revenue,
        AVG(vote_average) as avg_rating
    FROM movies m
    {where_clause};
"""
metrics_df = get_db_data(metrics_query)

# 4. Display Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Movies Cataloged", f"{metrics_df['total_movies'][0]:,}")
with col2:
    st.metric("Total Investment (Budget)", f"${metrics_df['total_budget'][0]:,}")
with col3:
    st.metric("Total Box Office (Revenue)", f"${metrics_df['total_revenue'][0]:,}")
with col4:
    st.metric("Average Audience Score", f"{metrics_df['avg_rating'][0]:.2f} / 10")

st.markdown("---")

# 5. Advanced Analytical Chart: Financial Risk vs Reward (ROI)
st.subheader("📊 Financial Sweet-Spot Analysis (Budget vs Revenue)")

chart_query = f"""
    SELECT 
        m.title, 
        m.budget, 
        m.revenue, 
        m.vote_average,
        ((m.revenue - m.budget)) as roi
    FROM movies m
    {where_clause}
    ORDER BY m.revenue DESC;
"""
chart_df = get_db_data(chart_query)

# Generate an interactive Scatter Plot using Plotly
fig = px.scatter(
    chart_df, 
    x="budget", 
    y="revenue", 
    hover_name="title",
    color="roi",
    size="vote_average",
    labels={"budget": "Production Budget ($)", "revenue": "Worldwide Revenue ($)", "roi": "Return on Investment (ROI)"},
    color_continuous_scale=px.colors.sequential.Viridis,
    title=f"Movie Performance Matrix ({selected_genre})"
)
st.plotly_chart(fig, use_container_width=True)

# 6. Advanced Table View using Data Analysis Window Functions
st.subheader("🏆 Efficiency Rankings (Top Profit-Generating Movies)")

# Wrote a query that filters or sorts by net profitability
ranking_query = f"""
    SELECT 
        m.title, 
        m.budget, 
        m.revenue,
        (m.revenue - m.budget) as net_profit
    FROM movies m
    {where_clause}
    ORDER BY net_profit DESC
    LIMIT 10;
"""
ranking_df = get_db_data(ranking_query)
st.dataframe(ranking_df, use_container_width=True)