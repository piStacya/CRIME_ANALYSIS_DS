import os
import pandas as pd

iccs = {
    "ICCS0101": "Intentional homicide",
    "ICCS0102": "Attempted intentional homicide",
    "ICCS02011": "Assault",
    "ICCS020111": "Serious assault",
    "ICCS020221": "Kidnapping",
    "ICCS0301" : "Sexual violence",
    "ICCS03011" : "Rape",
    "ICCS03012" : "Sexual Assault",
    "ICCS030221" : "Child pornography",
    "ICCS0302" : "Sexual exploitation",
    "ICCS0401": "Robbery",
    "ICCS0501": "Burglary",
    "ICCS05012": "Burglary of private residential premises",
    "ICCS0502": "Theft",
    "ICCS05021": "Theft of a motorized vehicle or parts thereof",
    "ICCS050211": "Theft of a motorized land vehicle",
    "ICCS0601" : "Unlawful acts involving controlled drugs",
    "ICCS0701" : "Fraud",
    "ICCS0703" : "Corruption",
    "ICCS07031" : "Bribery",
    "ICCS07041" : "Money laundering",
    "ICCS0903" : "Acts against computer systems",
    "ICCS09051" : "Participation in an organized criminal group",
    "ICCS1001" : "Acts that cause environmental pollution or degradation",
    "ICCS1004" : "Acts that result in the depletion or degradation of natural resources",
    "ICCS1002" : "Acts involving the movement or dumping of waste",
    "ICCS1003" : "Trade or possession of protected or prohibited species of fauna and flora",
    "ICCS02-04": "Serious violent crimes (aggregate)",
    "TOTAL": "Total offences"
}

os.makedirs('C:\\Users\\panda\\Desktop\\sksksk and i oop\\kool\\andmeteadus\\projekt\\cleanedDatasetsCrimes', exist_ok=True)
for filename in os.listdir('C:\\Users\\panda\\Desktop\\sksksk and i oop\\kool\\andmeteadus\\projekt\\cleanedDatasetsCountryNames'):
    if not filename.lower().endswith('.tsv'):
        continue

    input_path = os.path.join('C:\\Users\\panda\\Desktop\\sksksk and i oop\\kool\\andmeteadus\\projekt\\cleanedDatasetsCountryNames', filename)
    output_path = os.path.join('C:\\Users\\panda\\Desktop\\sksksk and i oop\\kool\\andmeteadus\\projekt\\cleanedDatasetsCrimes', filename)

    print(f"\n--- Faili töötlemine: {filename} ---")
    df = pd.read_csv(input_path, sep='\t')
    if "iccs" in df.columns:
        df["iccs"] = df["iccs"].replace(iccs)
    df.to_csv(output_path, sep='\t', index=False)
