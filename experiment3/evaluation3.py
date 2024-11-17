import pandas as pd

# Načti celý soubor jako řetězec
with open('/content/outputs3.txt', 'r', encoding='utf-8') as file:
    data = file.read()

# Rozdělení na jednotlivé bloky podle oddělovače
blocks = data.split("--------------------------------------------------")

# Vyčistění mezer kolem textu a odstranění prázdných bloků
blocks = [block.strip() for block in blocks if block.strip()]

# Vytvoření DataFrame s jedním sloupcem "text", kde každý blok je jeden řádek
txt_df = pd.DataFrame(blocks, columns=["text"])

# Nastavení pro zobrazení všech řádků DataFrame
pd.set_option('display.max_rows', None)  # Zobrazí všechny řádky při tisku

# Příprava prázdného seznamu pro ukládání jednotlivých experimentů
experiments = []
current_experiment = {}

# Iterace přes každý blok textu v 'text' sloupci txt_df
for block in txt_df["text"]:
    lines = block.split("\n")  # Rozdělení bloku na jednotlivé řádky
    for line in lines:
        # Kontrola začátku řádku a přiřazení hodnot do příslušných klíčů
        if line.startswith("Původní uživatelský dotaz:"):
            current_experiment["Původní uživatelský dotaz"] = line.replace("Původní uživatelský dotaz: ", "").strip()
        elif line.startswith("Vygenerovaná odpověď modelem:"):
            current_experiment["Vygenerovaná odpověď modelem"] = line.replace("Vygenerovaná odpověď modelem: ", "").strip()
        elif line.startswith("Verze experimentu:"):
            current_experiment["Verze experimentu"] = line.replace("Verze experimentu: ", "").strip()
        elif line.startswith("Minimální skóre podobnosti:"):
            current_experiment["Minimální skóre podobnosti"] = float(line.replace("Minimální skóre podobnosti: ", "").strip())
        elif line.startswith("Maximální skóre podobnosti:"):
            current_experiment["Maximální skóre podobnosti"] = float(line.replace("Maximální skóre podobnosti: ", "").strip())
        elif line.startswith("Spotřeba tokenů:"):
            current_experiment["Spotřeba tokenů"] = int(line.replace("Spotřeba tokenů: ", "").strip())
        elif line.startswith("Spotřeba tokenů - Vstupní (prompt):"):
            current_experiment["Vstupní spotřeba tokenů"] = int(line.replace("Spotřeba tokenů - Vstupní (prompt): ", "").strip())
        elif line.startswith("Spotřeba tokenů - Výstupní (completion):"):
            current_experiment["Výstupní spotřeba tokenů"] = int(line.replace("Spotřeba tokenů - Výstupní (completion): ", "").strip())

    # Po zpracování celého bloku přidáme experiment do seznamu a resetujeme current_experiment
    if current_experiment:
        experiments.append(current_experiment)
        current_experiment = {}

# Vytvoření strukturovaného DataFrame ze seznamu experimentů
structured_df = pd.DataFrame(experiments)
# Calculate the number of characters in "Generated Response by Model" for each row
structured_df["Response Character Count"] = structured_df["Vygenerovaná odpověď modelem"].str.len()

# Summary statistics: count of occurrences, sum of tokens, sum of characters in responses, and averages of similarity scores for each experiment version
version_summary = structured_df.groupby("Verze experimentu").agg(
    Count_of_Occurrences=("Verze experimentu", "size"),
    Total_Token_Consumption=("Spotřeba tokenů", "sum"),
    Total_Token_Prompt=("Vstupní spotřeba tokenů", "sum"),
    Total_Token_Completion=("Výstupní spotřeba tokenů", "sum"),
    Total_Response_Characters=("Response Character Count", "sum"),
    Avg_Max_Similarity_Score=("Maximální skóre podobnosti", "mean"),
    Avg_Min_Similarity_Score=("Minimální skóre podobnosti", "mean")
)

# Display the resulting summary DataFrame
version_summary
