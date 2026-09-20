import pandas as pd
from db_connection import engine

df = pd.read_sql("SELECT * FROM features", engine)

print(df.shape)
print(df.head())
print(df.dtypes)