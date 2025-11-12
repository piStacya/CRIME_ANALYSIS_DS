import pandas as pd

# Read the tab-separated file
df = pd.read_csv("C:\\Users\\panda\\Desktop\\sksksk and i oop\kool\\andmeteadus\\projekt\\databases\\intentional_homicide_and_sexual_offences_by_legal_status_and_sex_of_the_person_involved.tsv", sep="\t")

# Split the first column (which has comma-separated values)
split_cols = df.iloc[:, 0].str.split(",", expand=True)

# Rename those new columns, veerud iga tabeli jaoks eraldi vaadata
split_cols.columns = ["freq", "iccs", "leg_stat", "sex", "unit", "geo"]

# Drop the original combined column and join the split ones
df = pd.concat([split_cols, df.iloc[:, 1:]], axis=1)

# Save the cleaned version, iga tabeli jaoks norm nimi panna
df.to_csv("cleaned_data.tsv", sep="\t", index=False)

print("✅ Cleaned file saved as cleaned_data.tsv")
print(df.head())