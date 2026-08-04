import pandas as pd
file_path = "data/cmf/rentabilidad/articles-91850_document_2.xlsx"
df = pd.read_excel(file_path, skiprows=2)
print(df.tail().to_string())
