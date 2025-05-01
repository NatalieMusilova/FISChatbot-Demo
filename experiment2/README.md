# Experiment 2: Zlepšená segmentace a tematická optimalizace

Tento experiment navazuje na základní verzi RAG systému a zaměřuje se na **optimalizaci přípravy dat** a **výběru relevantního kontextu** tak, aby byly odstraněny slabiny identifikované v experimentu 1.

---

## 🧩 Architektura systému

Architektura je stále tříkomponentní (Indexování, Retriever, Generátor), ale zásadní změny byly provedeny v přípravě a struktuře dat:

### **Indexování**

V experimentu 2 byla použita předem připravená datová sada, uložená ve formátu dvojic (dotaz – kontext). Každý textový úsek v souboru `text_pairs2.txt` obsahuje text, který slouží jako kontextový vstup pro generátor. V tomto experimentu nejsou využita žádná složitá metadata – všechny informace potřebné pro odpověď jsou součástí samotného textu. 

Indexace byla provedena pomocí embeddingů těchto textových částí a jejich uložení do vektorové databáze Pinecone. 


- **V reálném provozu** by byly bloky **automaticky generovány a aktualizovány přímo z databáze znalostí** (např. pomocí systému Aphinit).
- Embeddingy jsou vytvářeny pomocí modelu `text-embedding-ada-002` a uloženy do Pinecone.
- Ukázka tematického seskupení textů je k dispozici v souboru **`text_pairs2.txt`** (ve formátu JSON).

### **Retriever**
- Uživatelský dotaz je opět převeden na embedding.
- Vyhledávání probíhá nad tematicky celistvými bloky.

### **Generátor**
- Jazykový model pracuje s komplexnějším kontextem, který zahrnuje všechny podstatné informace k danému tématu.
- Použit je model `gpt-3.5-turbo` (OpenAI API).

---
<img width="492" alt="image" src="https://github.com/user-attachments/assets/7cddf2ce-222f-4f7e-9abb-9efa5dd75b04">

## 🗂️ Struktura kódu

- **`indexing2.py`** – Skript pro přípravu dat do vektorové databáze Pinecone.
- **`main2.py`** – Hlavní skript pro běh chatbotu v rámci experimentu 2.
- **`evaluation2.py`** – Skript pro vyhodnocení výsledků (analyzuje přesnost, spotřebu tokenů atd.).
- **`text_pairs2.txt`** – Ukázka tematicky seskupených bloků ve formátu JSON. Každý záznam představuje ucelený tematický blok.

---

## 📁 Výstupy

- Výstupy generovaných odpovědí jsou ukládány do souboru `outputs2.txt`.
- Výsledky experimentu jsou podrobně analyzovány v diplomové práci a shrnuty v tabulkách a grafech.

---

## ⚙️ Parametry a výsledky testovaných verzí

V tomto experimentu byly testovány různé strategie tematického seskupení a nastavení parametru Top-k.

| Verze | Typ segmentace        | Top-k | Přesnost (ACC %) | Tokeny |
|-------|----------------------|-------|------------------|--------|
| 2a    | Tematické bloky      | 3     | 91               | 41 678 |
| 2b    | Tematické bloky      | 2     | 89               | 31 563 |
| 2c    | Tematické bloky      | 1     | 70               | 20 778 |

🧠 **Díky tematickému seskupení textů a optimalizaci retrieveru došlo k výraznému zvýšení přesnosti i snížení spotřeby tokenů oproti experimentu 1.**

---

## 🔍 Motivace pro experiment 2

Zásadní nedostatky experimentu 1, které tento experiment řeší:
- Odpovědi byly často nepřesné, protože klíčové informace byly rozptýleny v několika krátkých úsecích a generátor je neobdržel pohromadě.
- **Studenti často používají běžný hovorový jazyk** (např. „jak se dostanu na magistra“), zatímco **webové stránky používají formální formulace** (např. „podmínky pro přijetí do navazujícího magisterského studia“).  
  **Retriever v základní verzi nebyl dostatečně robustní**, aby tyto **strukturální nebo sémantické rozdíly** rozpoznal, což vedlo ke **ztrátě relevance** při výběru textů.
- 🧩 **Zbytkové texty bez obsahu způsobovaly chyby při vyhledávání**  
  Při dělení textu na úseky často vznikaly velmi krátké "zbytky" na konci dokumentů, které neobsahovaly žádné důležité informace.  
  Embedding model jim přesto přiřadil vektory, které byly nesprávně hodnoceny jako velmi podobné uživatelskému dotazu, protože chyběla sémantická výpověď.  
  🤷‍♂️ Retriever následně vybíral tyto prázdné nebo nerelevantní texty, protože je považoval za důležité. Pokud se v databázi nenacházel relevantní kontext, systém i přesto zpracoval tyto nerelevantní úseky – a zbytečně tak spotřeboval tokeny při generování odpovědi.

---

