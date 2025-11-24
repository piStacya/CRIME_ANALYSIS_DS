import pandas as pd

# Read the tab-separated file
#df = pd.read_csv("filepath", sep="\t")
df = pd.read_csv("C:\\Users\\panda\\Desktop\\sksksk and i oop\\kool\\andmeteadus\\projekt\\originalDatabases\\suspects_and_offenders_by_sex.tsv", sep="\t")


# Split the first column (which has comma-separated values)
split_cols = df.iloc[:, 0].str.split(",", expand=True)

# Rename those new columns, veerud iga tabeli jaoks eraldi vaadata
#split_cols.columns = [column names]
split_cols.columns = ["freq", "leg_stat", "sex", "unit","geo"]

# Drop the original combined column and join the split ones
df = pd.concat([split_cols, df.iloc[:, 1:]], axis=1)

# Save the cleaned version, iga tabeli jaoks norm nimi panna
#df.to_csv("new file name", sep="\t", index=False)
df.to_csv("suspects_and_offenders_by_sex.tsv", sep="\t", index=False)

print("Cleaned file saved")
print(df.head())