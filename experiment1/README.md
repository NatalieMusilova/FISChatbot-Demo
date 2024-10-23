### Základní architektura RAG systému

Tento experiment představuje **základní verzi RAG (Retrieval-Augmented Generation) systému**, který kombinuje vyhledávání relevantních informací a jejich následné využití k generování odpovědí pomocí velkých jazykových modelů (LLM). Architektura se skládá ze tří klíčových komponent:

1. **Indexování**  
   Tato komponenta zajišťuje přípravu a organizaci dat. Data jsou extrahována z webových zdrojů, očištěna, rozdělena na segmenty a následně převedena do vektorové reprezentace pomocí embedding modelu.

2. **Retriever**  
   Retriever je komponenta, která vyhledává relevantní informace na základě dotazu uživatele. Dotaz je převeden do vektorové podoby a následně porovnán s vektory uloženými v databázi. Výsledkem jsou nejrelevantnější textové pasáže, které jsou předány generátoru.

3. **Generátor**  
   Generátor kombinuje informace získané z retrieveru s uživatelským dotazem a pomocí LLM vytváří odpověď. Tento proces zajišťuje, že odpovědi jsou přesné a informačně bohaté.

Tato základní architektura slouží jako první krok k experimentům s optimalizací vyhledávání a generování odpovědí pomocí RAG modelů:

![Architecture Experiment 1](./arch_exp1.png)

### Příprava dat

Data pro systém jsou získávána pomocí webového scrapingu. Proces zahrnuje:

1. **Extrakci dat**:  
   - Pomocí knihovny BeautifulSoup a requests v Pythonu se získává textový obsah z webových stránek.

2. **Čištění dat**:  
   - Data jsou očištěna od HTML tagů a nežádoucích znaků, aby byla připravena pro další zpracování. Používají se metody Pythonu jako `strip()`, `replace()` nebo regulární výrazy.
