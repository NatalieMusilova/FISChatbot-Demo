# FISChatbot-Demo
## 🤖Popis projektu
Tento chatbot je součástí mé diplomové práce a jeho hlavním účelem je optimalizace nákladů na provoz a zlepšení kvality odpovědí poskytovaných zájemcům o studium na Fakultě informatiky a statistiky (FIS). Chatbot využívá moderní technologie a inovativní přístupy ke správě dotazů a zpracování odpovědí.
## 🛠️  Použité technologie:
### RAG (Retrieval-Augmented Generation) architektura
Chatbot využívá tuto architekturu pro efektivní kombinaci vyhledávání relevantních informací a generování odpovědí. Tento přístup umožňuje chatbotovi poskytovat přesnější a rychlejší odpovědi tím, že propojuje vyhledávání v databázích s generováním odpovědí pomocí jazykových modelů.
### Vektorová databáze
Pro ukládání a rychlé vyhledávání informací je využívána vektorová databáze, která umožňuje chatbotovi rychle nalézt relevantní části textů na základě podobnosti dotazů a existujících dokumentů.
Zdrojem pro tyto texty jsou veřejně dostupné informace z webových stránek FIS, VŠE a dalších relevantních webů.
Tyto texty byly následně předzpracovány, rozděleny na tematické úseky a doplněny metadaty, což umožňuje přesné a efektivní vyhledávání při zodpovídání dotazů.

### Jazykový model
Pro generování odpovědí je použit model gpt-3.5-turbo prostřednictvím API od OpenAI.

### Další použité technologie

- **Streamlit** – framework pro webovou aplikaci
- **text-embedding-ada-002** – embedding model pro převod dotazu a dokumentů do vektorové podoby



## 🎯 Cíl projektu:
Hlavním cílem diplomové práce je zkoumat možnosti, jak snížit náklady na jeho provoz a současně zlepšit kvalitu poskytovaných odpovědí.

## 📁 Struktura repozitáře

Tento chatbot je testován v několika experimentech, jejichž cílem je porovnat kvalitu odpovědí a náklady na tokeny u různých přístupů. Přesnost odpovědí je analyzována na základě referenční sady otázek, které jsou uložené v příloze A diplomové práce.

- Každá experimentální verze chatbota má svou vlastní složku, například experiment1/, experiment2/ a podobně. Každá z těchto složek obsahuje samostatný kód a související dokumentaci.
- README.md soubory ve složkách experimentů poskytují podrobnosti o každé verzi chatbota, včetně implementovaných funkcí a technických specifikací.

Kód je rozdělen tak, aby každá verze mohla být testována a analyzována nezávisle, což umožňuje snadné porovnání výsledků mezi různými experimentálními verzemi. Pro snadnou navigaci v repozitáři jsou v hlavním README.md uvedeny odkazy na jednotlivé experimentální verze, což umožňuje rychlý přístup ke každému kódu a jeho dokumentaci.

- [Experiment 1](experiment1/README.md) – Popis experimentální verze 1.
- [Experiment 2](experiment2/README.md) – Popis experimentální verze 2.
- [Experiment 3](experiment3/README.md) – Popis experimentální verze 3.

  Podrobné výsledky experimentů jsou dostupné v diplomové práci v kapitole 5.

## 🚀 Finální verze a spuštění
Nejlepší a nejlépe fungující verze chatbota je implementována ve skriptu main.py. Tato verze kombinuje všechny poznatky získané během experimentování a optimalizací v jednotlivých verzích.
### Knihovny a závislosti
Projekt je napsán v jazyce Python a využívá následující klíčové knihovny:
- **openai** –  zajišťuje přístup k jazykovým modelům (např. gpt-3.5-turbo) a embedding modelu text-embedding-ada-002. Používá se pro generování odpovědí a převod textů do vektorové podoby. Kód je kompatibilní s verzí openai==0.28
- **pinecone-client** – knihovna pro komunikaci s vektorovou databází Pinecone, kde jsou uloženy embeddingy textových úseků. ⚠️ **Důležité:** Kód používá novou syntaxi z verze 5.0.1. Starší verze (např. 2.x nebo 1.x) nejsou kompatibilní.
- **streamlit** – framework pro jednoduché a rychlé webové rozhraní. V tomto projektu slouží jako hlavní uživatelské prostředí chatbota.
- **datetime, io** – vestavěné knihovny Pythonu používané pro vytváření časových záznamů v logu dotazů a pro export těchto logů do .txt souborů, které si uživatel může stáhnout ze Streamlit aplikace.

### Co dělá tento kód

1. **Zpracuje dotaz uživatele:**  
   Nejprve vezme to, co uživatel napsal, a převede to na speciální číselnou podobu (tzv. „embedding“), aby mohl najít podobné texty v databázi.

2. **Vyhledávání odpovědi:**  
   Systém nejprve porovnává uživatelský dotaz s vektory označenými příznakem text_response. Tyto vektory obsahují nejčastější otázky a jejich předpřipravené odpovědi. Pokud je nalezen vektor s podobností (skóre) ≥ 0.9, systém neprovádí generování, ale přímo použije odpověď z metadat daného vektoru. Tento přístup šetří tokeny a zajišťuje rychlou reakci na běžné dotazy.

3. **Pokud není nalezen žádný vektor s příznakem text_response:**  
   Retriever pokračuje a hledá odpověď mezi vektory označenými příznakem text_query. Tyto vektory reprezentují tematické otázky a úseky textu, které mohou odpověď obsahovat. Systém vybírá ty, které mají skóre ≥ 0.82, přičemž se vybírají 2 nejbližší výsledky.

4. **Generování odpovědi:**  
   Pokud byly nalezeny vhodné texty z text_query, předá se jejich obsah generátoru (jazykovému modelu GPT-3.5), který vytvoří odpověď přizpůsobenou uživatelskému dotazu​.

5. **Pokud není nalezen žádný vektor s dostatečnou podobností:**  
   Uživatel dostane zprávu, že momentálně nejsou k dispozici žádná relevantní data.  
   Chatbot si takový dotaz **uloží do dočasné paměti**, aby bylo možné jej stáhnout jako součást souboru `unanswered_log.txt`.  
   > 🎓 V rámci této diplomové práce jde o demonstraci funkčnosti — v ostrém provozu by tyto dotazy bylo možné předat systému **Aphinit** k pozdějšímu zpracování.

6. **Záznam a export informací o odpovědi**  
   Chatbot si pro každý dotaz pamatuje:
   - samotný dotaz a odpověď  
   - jaké texty byly použity  
   - jaká byla jejich podobnost (skóre)  
   - kolik tokenů bylo spotřebováno  

7. **Možnost stažení záznamů**  
   Uživatel si může stáhnout:
   - `chatbot_log.txt` – přehled všech dotazů, odpovědí, skóre podobnosti a spotřeby tokenů  
   - `unanswered_log.txt` – seznam dotazů, na které se nepodařilo najít odpověď

   > 📌 Tato tlačítka pro stažení se zobrazí **pouze tehdy**, pokud chatbot během relace skutečně něco zaznamená.  
   > 🔒 **Bezpečnost a soukromí:**  
   > – Dotazy a odpovědi jsou uchovávány pouze **během otevřené relace (aktuální stránky)**.  
   > – Po obnovení nebo zavření stránky se veškerá data **automaticky smažou**.  
   > – Nic není odesíláno na žádný externí server, **kromě dotazů směrem k OpenAI API** pro vygenerování odpovědi.

