import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:vish1412@localhost/earthquake_db"
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

    "9. Count of earthquakes per hour of day": """
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

    "14. Count of reviewed vs automatic earthquakes": """
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

    "18. Events with high station coverage (nst > 50)": """
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

    "22. Countries with shallow and deep quakes in same month": """
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

    "23. Year-over-year growth rate globally": """
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

    "24. 3 most seismically active regions": """
        SELECT
            place,
            COUNT(*) AS frequency,
            AVG(mag) AS avg_magnitude,
            COUNT(*) * AVG(mag) AS seismic_activity_score
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

    "26. Countries with highest ratio of shallow to deep earthquakes": """
        SELECT
            country,
            SUM(
                CASE
                    WHEN depth_km < 50 THEN 1
                    ELSE 0
                END
            ) /
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

    "27. Average magnitude difference (With tsunami vs Without)": """
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

    "30. Regions with highest frequency of deep focus earthquakes": """
        SELECT
            place,
            COUNT(*) AS deep_earthquake_count
        FROM earthquakes
        WHERE depth_km > 300
        GROUP BY place
        ORDER BY deep_earthquake_count DESC;
    """
}


for title, sql_text in queries.items():

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    try:
        df = pd.read_sql(sql_text, con=engine)

        if df.empty:
            print("No results found.")
        else:
            print(f"Rows returned: {len(df)}")
            print(df.head(10).to_string(index=False))

    except Exception as e:
        print(f"❌ Error running this query: {e}")