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
- Použita tematicky strukturovaná datová sada (`text_pairs2.txt`) z experimentu 2.
- Metadata obsahují stručné odpovědi pro dotazy s vysokou mírou shody.
- Embeddingy vytvořeny pomocí `text-embedding-ada-002` a uloženy ve vektorové databázi Pinecone.

### **Retriever**
- Dotaz je převeden na embedding a porovnán s uloženými vektory.
- Podle skóre podobnosti se rozhoduje, zda a jak bude odpověď generována.

### **Generátor**
- Spouští se pouze při střední shodě.
- Použit model `gpt-3.5-turbo` přes OpenAI API.

---

## 🗂️ Struktura kódu

- `main3.py` – Hlavní skript s rozhodovacím mechanismem.
- `evaluation3.py` – Vyhodnocení přesnosti, spotřeby tokenů a typů odpovědí.
- `text_pairs2.txt` – Strukturovaná datová sada (stejná jako v experimentu 2).
- `outputs3.txt` – Vygenerované odpovědi, pokud došlo k zapojení generátoru.

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


