# Experiment 3: Podmíněné generování a filtrace nerelevantních dotazů

Třetí experiment rozšiřuje architekturu systému RAG s cílem zlepšit **nákladovou efektivitu** a **zvýšit kvalitu výstupů**. Klíčovou inovací je zavedení mechanismu, který rozhoduje o dalším postupu podle míry podobnosti mezi dotazem a nalezeným kontextem.

---

## 🧭 Motivace pro experiment 3

Na základě zjištění z experimentu 2 byly identifikovány dva zásadní nedostatky:
- Generátor byl spouštěn i u dotazů, pro které byla v databázi dostupná jednoznačná odpověď – což vedlo ke zbytečné spotřebě tokenů.
- Do generátoru byly předávány i textové úseky s nízkou relevancí, které neobsahovaly potřebné informace k odpovědi. Výsledkem byly nejen zavádějící odpovědi, ale i zbytečná spotřeba tokenů.

Z těchto důvodů byl navržen **mechanismus podmíněného výběru textových úseků**:

- ✅ **Vysoká podobnost** (např. *score* > 0.9): systém použije přímo odpověď z metadat bez zapojení generátoru.
- ⚠️ **Nízká podobnost** (např. *score* < 0.8): generátor se nespustí vůbec, dotaz je uložen k dalšímu zpracování.
- 🔁 **Střední podobnost** (např. 0.8–0.9): dojde ke klasickému spuštění generátoru s využitím relevantního kontextu.

Tento přístup výrazně **minimalizuje zbytečné volání generátoru**, zachovává **relevantnost odpovědí** a zvyšuje **nákladovou efektivitu** systému.

---

## ⚙️ Architektura systému

Architektura zůstává tříkomponentní – Indexování, Retriever, Generátor – přičemž každá komponenta pracuje s rozhodovacím mechanismem na základě skóre podobnosti.

### **Indexování**
Pro experiment 3 byly použity dvě oddělené datové sady ve formátu JSON:

- `text_pairs3.txt` – obsahuje tematicky seskupené dotazy s odpovídajícími kontexty. Při indexaci jsou tyto záznamy označeny příznakem `text_query`.
- `text_pairs_resp3.txt` – zahrnuje často kladené dotazy s předpřipravenými odpověďmi. Tyto záznamy nesou příznak `text_response`.

Embeddingy pro oba typy dat byly vytvořeny pomocí modelu `text-embedding-ada-002` a následně uloženy do vektorové databáze Pinecone.

Tato struktura umožňuje systému využívat přímo odpovědi z metadat bez spuštění generátoru v případech, kdy je nalezeno velmi vysoké skóre podobnosti mezi dotazem a některou častou otázkou.


### **Retriever**
- Uživatelský dotaz je převeden na embedding.
- Vyhledávání probíhá ve dvou krocích:
  1. Pokus o nalezení odpovědi mezi záznamy `text_response`.
  2. Pokud není nalezena odpověď s dostatečnou podobností, pokračuje se ve vyhledávání mezi `text_query` a případně se aktivuje generátor.

### **Generátor**
- Spouští se pouze tehdy, když žádný záznam typu `text_response` nedosáhne požadované míry shody, ale některý `text_query` překročí minimální prahovou hodnotu.
- Použit je model `gpt-3.5-turbo` přes OpenAI API.

---

## 🗂️ Struktura kódu

- `indexing3.py` – Skript pro vytvoření embeddingů a jejich uložení do vektorové databáze Pinecone. Každému vektorovému záznamu jsou přiřazena metadata, která určují jeho využití: buď jako **přímá odpověď** (`text_response`), nebo jako **kontext pro generování odpovědi** (`text_query`).  
  Díky tomu lze při vyhledávání nejprve prohledat pouze záznamy s příznakem `text_response` a pokusit se odpovědět bez zapojení generátoru. Pokud není nalezena dostatečně podobná odpověď, pokračuje se vyhledáváním v blocích `text_query`, které slouží jako kontext pro jazykový model.

- `main3.py` – Skript obsahující rozhodovací mechanismus, který na základě skóre podobnosti vybírá, zda použít odpověď z metadat nebo spustit generátor.
- `evaluation3.py` – Skript pro vyhodnocení přesnosti, spotřeby tokenů a typologie odpovědí. Struktura odpovídá skriptu z předchozího experimentu.
- `text_pairs3.txt` – Tematicky seskupené dotazy s odpovídajícím kontextem (dotaz–kontext), označené jako `text_query`.
- `text_pairs_resp3.txt` – Datová sada často kladených otázek s jednoznačnými odpověďmi, označená jako `text_response`.
- `outputs3.txt` – Výstupní soubor s odpověďmi generovanými modelem GPT, pokud došlo k aktivaci generátoru.
- `questions_for_processing3.txt` – Seznam dotazů, které nebyly zodpovězeny (nebylo dosaženo minimální hodnoty skóre), určený pro další analýzu a rozšíření dat:contentReference[oaicite:0]{index=0}.


---

## 📊 Výsledky

| Verze | Podmínky generování       | Přesnost (ACC %) | Tokeny | Poměr dotazů zodpovězených bez LLM |
|-------|---------------------------|------------------|--------|------------------------------------|
| 3a    | Skóre-based rozhodování   | 92               | 18 021 | 37 %                               |

---

## 🔍 Shrnutí přínosů

Experiment 3 ukázal, že **řízení generování odpovědí na základě skóre podobnosti** umožňuje výrazně snížit náklady na provoz systému a zároveň **zachovat vysokou kvalitu výstupů**. Tato strategie je klíčovým krokem směrem k efektivnímu využití RAG architektur v praxi.



<img width="501" alt="image" src="https://github.com/user-attachments/assets/397e3963-32a8-431d-84ac-1f418a44038b">

## 🔍 Shrnutí problému v experimentu 3
- Generátor často nedokázal využít celý obsah relevantního textu – například odpověď zahrnovala jen část z více potřebných informací.
![image](https://github.com/user-attachments/assets/bb5356a2-c83c-400b-a6c5-f05165e23c41)


