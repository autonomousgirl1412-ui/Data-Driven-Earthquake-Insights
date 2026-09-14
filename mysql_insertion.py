import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("earthquake_data_cleaned.csv")

print("Data loaded successfully!")
print(df.shape)
print(df.columns.tolist())

engine = create_engine(
    "mysql+pymysql://root:vish1412@localhost/earthquake_db"
)


print("mysql connection successful!")

df.to_sql(
    "earthquakes",
    con=engine,
    if_exists="replace",
    index=False
)

print("Data inserted successfully!")