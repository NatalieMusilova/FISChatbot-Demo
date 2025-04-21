# Experiment 1: Základní RAG systém

Tento experiment představuje **základní verzi RAG (Retrieval-Augmented Generation) systému**, který kombinuje vyhledávání relevantních informací a jejich následné využití k generování odpovědí pomocí velkých jazykových modelů (LLM).
## 🧩 Architektura systému
Architektura se skládá ze tří hlavních komponent:

1. **Indexování**  
   - Získávání dat z webových stránek pomocí `BeautifulSoup` a `requests`
   - Čištění dat (odstranění HTML tagů, prázdných znaků, speciálních symbolů)
   - Rozdělení textu na části (`chunking`) s parametry `chunk_size` a `chunk_overlap`
   - Vytvoření vektorových reprezentací pomocí embedding modelu `text-embedding-ada-002`
   - Uložení embeddingů do vektorové databáze Pinecone

2. **Retriever**  
   - Uživatelský dotaz je převeden do vektorové podoby
   - Prohledává se databáze embeddingů pro nalezení nejrelevantnějších textových segmentů (`Top-k`)
   - Použité skórování na základě kosinové podobnosti

3. **Generátor**  
   - Získané textové segmenty a uživatelský dotaz jsou předány modelu `gpt-3.5-turbo`
   - Model vygeneruje odpověď, která je vrácena uživateli

Tato základní architektura slouží jako první krok k experimentům s optimalizací vyhledávání a generování odpovědí pomocí RAG modelů:

![Architecture Experiment 1](./arch_exp1.png)

### Příprava dat

Data pro systém jsou získávána pomocí webového scrapingu. Proces zahrnuje:

1. **Extrakci dat**:  
   - Pomocí knihovny BeautifulSoup a requests v Pythonu se získává textový obsah z webových stránek.

2. **Čištění dat**:  
   - Data jsou očištěna od HTML tagů a nežádoucích znaků, aby byla připravena pro další zpracování. Používají se metody Pythonu jako `strip()`, `replace()` nebo regulární výrazy.
  

## ⚙️ Parametry testovaných verzí

V rámci testování bylo provedeno 6 variant experimentu (1a–1f), které se liší velikostí segmentů a mírou překryvu:

| Verze | Chunk size | Overlap | Top-k | Přesnost (ACC %) | Tokeny |
|-------|------------|---------|-------|------------------|--------|
| 1a    | 256        | 10      | 10    | 50               | 69 481 |
| 1b    | 370        | 20      | 7     | 52               | 67 113 |
| 1c    | 512        | 40      | 5     | 50               | 63 216 |
| 1d    | 640        | 60      | 4     | 48               | 60 763 |
| 1e    | 768        | 80      | 3     | 43               | 52 264 |
| 1f    | 1024       | 100     | 2     | 45               | 46 489 |

🧠 *Výsledek ukázal, že menší textové segmenty s vyšším počtem vrácených výsledků (Top-k) vedou k vyšší přesnosti, zatímco delší segmenty snižují spotřebu tokenů, ale i kvalitu odpovědí.*

## 📁 Výstupy

- Výstupy experimentu (odpovědi) jsou ukládány do souboru `outputs1.txt`
- Pro vyhodnocení výsledků slouží skript `evaluation1.py`, který extrahuje klíčové metriky:
  - počet dotazů
  - spotřeba tokenů
  - průměrné skóre podobnosti

📊 Vizualizace výsledků je dostupná v tabulce a grafu.

## 🔍 Detailní testování

Experiment pracuje s reálnými dotazy z příloh A, B a C diplomové práce. Hodnocení odpovědí bylo provedeno manuálně s ohledem na očekávané odpovědi.

📁 Výsledné soubory:
- `outputs1.txt` – obsahuje generované odpovědi
- `chatbot_log.txt` – zaznamenává dotazy, odpovědi, skóre a použitý kontext
- `unanswered_log.txt` – obsahuje nezodpovězené dotazy pro budoucí zpracování
  
 ![image](https://github.com/user-attachments/assets/c69ce3b0-e5a4-42f5-857d-9ca3615b05b6)

