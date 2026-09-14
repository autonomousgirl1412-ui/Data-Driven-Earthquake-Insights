import streamlit as st
import pandas as pd
import pydeck as pdk
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Data-Driven Earthquake Insights",
    page_icon="🌍",
    layout="wide"
)

engine = create_engine(
    "mysql+pymysql://root:vish1412@localhost/earthquake_db"
)

st.title("🌍 Data-Driven Earthquake Insights")
st.caption("Interactive analysis of global earthquake activity")

st.divider()

section = st.pills(
    "Dashboard Section",
    [
        "Overview",
        "Earthquake Explorer",
        "Trends",
        "SQL Analysis"
    ],
    default="Overview"
)

st.divider()

if section == "Overview":

    st.subheader("📊 Global Earthquake Overview")

    total_query = """
        SELECT COUNT(*) AS total
        FROM earthquakes;
    """

    total_df = pd.read_sql(total_query, engine)
    total_earthquakes = total_df["total"].iloc[0]

    avg_mag_query = """
        SELECT AVG(mag) AS avg_mag
        FROM earthquakes;
    """

    avg_mag_df = pd.read_sql(avg_mag_query, engine)
    avg_magnitude = avg_mag_df["avg_mag"].iloc[0]

    max_mag_query = """
        SELECT MAX(mag) AS max_mag
        FROM earthquakes;
    """

    max_mag_df = pd.read_sql(max_mag_query, engine)
    max_magnitude = max_mag_df["max_mag"].iloc[0]

    max_depth_query = """
        SELECT MAX(depth_km) AS max_depth
        FROM earthquakes;
    """

    max_depth_df = pd.read_sql(max_depth_query, engine)
    max_depth = max_depth_df["max_depth"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🌎 Total Earthquakes",
        f"{total_earthquakes:,}"
    )

    col2.metric(
        "📊 Average Magnitude",
        f"{avg_magnitude:.2f}"
    )

    col3.metric(
        "⚡ Strongest Magnitude",
        f"{max_magnitude:.2f}"
    )

    col4.metric(
        "🌊 Maximum Depth",
        f"{max_depth:.2f} km"
    )

    st.divider()

    st.subheader("📌 About This Dashboard")

    st.write(
        """
        This dashboard analyzes earthquake activity using data stored
        in MySQL. Explore earthquake locations, magnitude, depth,
        yearly trends and SQL-based analytical results.
        """
    )

elif section == "Earthquake Explorer":

    st.subheader("🔎 Earthquake Explorer")

    explorer_query = """
        SELECT
            id,
            time,
            latitude,
            longitude,
            depth_km,
            mag,
            magType,
            place,
            country,
            tsunami
        FROM earthquakes
        ORDER BY time DESC;
    """

    earthquake_df = pd.read_sql(
        explorer_query,
        engine
    )

    st.markdown("### 🎚️ Filters")

    col1, col2, col3 = st.columns(3)

    min_magnitude = float(
        earthquake_df["mag"].min()
    )

    max_magnitude = float(
        earthquake_df["mag"].max()
    )

    with col1:

        magnitude_range = st.slider(
            "Magnitude",
            min_value=min_magnitude,
            max_value=max_magnitude,
            value=(
                min_magnitude,
                max_magnitude
            ),
            step=0.1
        )

    countries = sorted(
        earthquake_df["country"]
        .dropna()
        .loc[
            earthquake_df["country"] != ""
        ]
        .unique()
        .tolist()
    )

    with col2:

        selected_country = st.selectbox(
            "Country",
            ["All Countries"] + countries
        )

    min_depth = float(
        earthquake_df["depth_km"].min()
    )

    max_depth = float(
        earthquake_df["depth_km"].max()
    )

    with col3:

        depth_range = st.slider(
            "Depth (km)",
            min_value=min_depth,
            max_value=max_depth,
            value=(
                min_depth,
                max_depth
            ),
            step=10.0
        )

    filtered_df = earthquake_df[
        (earthquake_df["mag"] >= magnitude_range[0])
        &
        (earthquake_df["mag"] <= magnitude_range[1])
        &
        (earthquake_df["depth_km"] >= depth_range[0])
        &
        (earthquake_df["depth_km"] <= depth_range[1])
    ]

    if selected_country != "All Countries":

        filtered_df = filtered_df[
            filtered_df["country"] == selected_country
        ]

    st.metric(
        "🔎 Matching Earthquakes",
        f"{len(filtered_df):,}"
    )

    st.divider()

    st.subheader("📋 Earthquake Data")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🗺️ Earthquake Locations")

    map_df = filtered_df[
        [
            "latitude",
            "longitude",
            "mag",
            "place"
        ]
    ].dropna()

    earthquake_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_radius="mag * 2000",
        get_fill_color="[255, 80, 50, 160]",
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=1.2,
        pitch=0
    )

    deck = pdk.Deck(
        layers=[earthquake_layer],
        initial_view_state=view_state,
        tooltip={
            "text": "Place: {place}\nMagnitude: {mag}"
        }
    )

    st.pydeck_chart(
        deck,
        use_container_width=True
    )

elif section == "Trends":

    st.subheader("📈 Earthquake Trends")

    yearly_query = """
        SELECT
            year,
            COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY year
        ORDER BY year;
    """

    yearly_df = pd.read_sql(
        yearly_query,
        engine
    )

    st.markdown("### 📅 Earthquakes by Year")

    st.line_chart(
        yearly_df.set_index("year")[
            "earthquake_count"
        ]
    )

    st.divider()

    monthly_query = """
        SELECT
            month,
            COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY month
        ORDER BY month;
    """

    monthly_df = pd.read_sql(
        monthly_query,
        engine
    )

    st.markdown("### 🗓️ Earthquakes by Month")

    st.bar_chart(
        monthly_df.set_index("month")[
            "earthquake_count"
        ]
    )

elif section == "SQL Analysis":

    st.subheader("🧮 SQL Analysis")

    st.write(
        "Analytical results"
    )

    queries = {

        "1. Top 10 strongest earthquakes": """
            SELECT *
            FROM earthquakes
            ORDER BY mag DESC
            LIMIT 10;
        """,

        "2. Top 10 deepest earthquakes": """
            SELECT *
            FROM earthquakes
            ORDER BY depth_km DESC
            LIMIT 10;
        """,

        "3. Shallow earthquakes (<50 km) and mag > 7.5": """
            SELECT *
            FROM earthquakes
            WHERE depth_km < 50
              AND mag > 7.5;
        """,

        "5. Average magnitude per magnitude type": """
            SELECT
                magType,
                AVG(mag) AS avg_magnitude
            FROM earthquakes
            GROUP BY magType
            ORDER BY avg_magnitude DESC;
        """,

        "6. Year with most earthquakes": """
            SELECT
                year,
                COUNT(*) AS earthquakes_count
            FROM earthquakes
            GROUP BY year
            ORDER BY earthquakes_count DESC
            LIMIT 1;
        """,

        "7. Month with highest number of earthquakes": """
            SELECT
                month,
                COUNT(*) AS earthquakes_count
            FROM earthquakes
            GROUP BY month
            ORDER BY earthquakes_count DESC
            LIMIT 1;
        """,

        "8. Day of week with most earthquakes": """
            SELECT
                day_of_week,
                COUNT(*) AS earthquakes_count
            FROM earthquakes
            GROUP BY day_of_week
            ORDER BY earthquakes_count DESC
            LIMIT 1;
        """,

        "9. Count of earthquakes per hour": """
            SELECT
                hour,
                COUNT(*) AS earthquakes_count
            FROM earthquakes
            GROUP BY hour
            ORDER BY hour;
        """,

        "10. Most active reporting network": """
            SELECT
                net,
                COUNT(*) AS report_count
            FROM earthquakes
            GROUP BY net
            ORDER BY report_count DESC
            LIMIT 1;
        """,

        "14. Reviewed vs automatic earthquakes": """
            SELECT
                status,
                COUNT(*) AS total_count
            FROM earthquakes
            GROUP BY status;
        """,

        "15. Count by earthquake type": """
            SELECT
                type,
                COUNT(*) AS total_count
            FROM earthquakes
            GROUP BY type
            ORDER BY total_count DESC;
        """,

        "16. Number of earthquakes by data type": """
            SELECT
                types,
                COUNT(*) AS total_count
            FROM earthquakes
            GROUP BY types
            ORDER BY total_count DESC;
        """,

        "18. Events with high station coverage": """
            SELECT *
            FROM earthquakes
            WHERE nst > 50;
        """,

        "19. Number of tsunamis triggered per year": """
            SELECT
                year,
                COUNT(*) AS tsunamis_triggered
            FROM earthquakes
            WHERE tsunami = 1
            GROUP BY year
            ORDER BY year;
        """,

        "21. Top 5 countries with highest average magnitude": """
            SELECT
                country,
                AVG(mag) AS avg_magnitude
            FROM earthquakes
            WHERE country IS NOT NULL
              AND country != ''
            GROUP BY country
            ORDER BY avg_magnitude DESC
            LIMIT 5;
        """,

        "22. Countries with shallow and deep earthquakes in same month": """
            SELECT
                country,
                year,
                month
            FROM earthquakes
            WHERE country IS NOT NULL
              AND country != ''
            GROUP BY country, year, month
            HAVING
                SUM(
                    CASE
                        WHEN depth_km < 50 THEN 1
                        ELSE 0
                    END
                ) > 0
                AND
                SUM(
                    CASE
                        WHEN depth_km > 300 THEN 1
                        ELSE 0
                    END
                ) > 0;
        """,

        "23. Year-over-year growth rate": """
            WITH AnnualCounts AS (
                SELECT
                    year,
                    COUNT(*) AS total_eq
                FROM earthquakes
                GROUP BY year
            )
            SELECT
                curr.year,
                curr.total_eq,
                prev.total_eq AS prev_year_eq,
                (
                    (curr.total_eq - prev.total_eq)
                    / NULLIF(prev.total_eq, 0)
                ) * 100 AS yoy_growth_percentage
            FROM AnnualCounts curr
            LEFT JOIN AnnualCounts prev
                ON curr.year = prev.year + 1
            ORDER BY curr.year;
        """,

        "24. Three most seismically active regions": """
            SELECT
                place,
                COUNT(*) AS frequency,
                AVG(mag) AS avg_magnitude,
                COUNT(*) * AVG(mag)
                    AS seismic_activity_score
            FROM earthquakes
            GROUP BY place
            ORDER BY seismic_activity_score DESC
            LIMIT 3;
        """,

        "25. Average depth within ±5° latitude of equator": """
            SELECT
                country,
                AVG(depth_km) AS avg_depth
            FROM earthquakes
            WHERE latitude BETWEEN -5 AND 5
              AND country IS NOT NULL
              AND country != ''
            GROUP BY country
            ORDER BY avg_depth DESC;
        """,

        "26. Highest shallow-to-deep earthquake ratio": """
            SELECT
                country,
                SUM(
                    CASE
                        WHEN depth_km < 50 THEN 1
                        ELSE 0
                    END
                )
                /
                NULLIF(
                    SUM(
                        CASE
                            WHEN depth_km > 300 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS shallow_to_deep_ratio
            FROM earthquakes
            WHERE country IS NOT NULL
              AND country != ''
            GROUP BY country
            HAVING shallow_to_deep_ratio IS NOT NULL
            ORDER BY shallow_to_deep_ratio DESC;
        """,

        "27. Magnitude difference with and without tsunami": """
            SELECT
                AVG(
                    CASE
                        WHEN tsunami = 1 THEN mag
                    END
                )
                -
                AVG(
                    CASE
                        WHEN tsunami = 0 THEN mag
                    END
                ) AS magnitude_difference
            FROM earthquakes;
        """,

        "28. Events with lowest data reliability": """
            SELECT
                id,
                time,
                place,
                mag,
                gap,
                rms
            FROM earthquakes
            ORDER BY gap DESC, rms DESC
            LIMIT 20;
        """,

        "30. Deep-focus earthquake regions": """
            SELECT
                place,
                COUNT(*) AS deep_earthquake_count
            FROM earthquakes
            WHERE depth_km > 300
            GROUP BY place
            ORDER BY deep_earthquake_count DESC;
        """
    }

    selected_query = st.selectbox(
        "Select a SQL Problem Statement",
        list(queries.keys())
    )

    result_df = pd.read_sql(
        queries[selected_query],
        engine
    )

    st.markdown("### 📋 Query Result")

    st.metric(
        "Rows Returned",
        f"{len(result_df):,}"
    )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )