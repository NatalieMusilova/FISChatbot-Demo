# FISChatbot-Demo
## Popis projektu
Tento chatbot je součástí mé diplomové práce a jeho hlavním účelem je optimalizace nákladů na provoz a zlepšení kvality odpovědí poskytovaných zájemcům o studium na Fakultě informatiky a statistiky (FIS). Chatbot využívá moderní technologie a inovativní přístupy ke správě dotazů a zpracování odpovědí.
## Použité technologie:
### RAG (Retrieval-Augmented Generation) architektura
Chatbot využívá tuto architekturu pro efektivní kombinaci vyhledávání relevantních informací a generování odpovědí. Tento přístup umožňuje chatbotovi poskytovat přesnější a rychlejší odpovědi tím, že propojuje vyhledávání v databázích s generováním odpovědí pomocí jazykových modelů.
### Vektorová databáze
Pro ukládání a rychlé vyhledávání informací je využívána vektorová databáze, která umožňuje chatbotovi rychle nalézt relevantní části textů na základě podobnosti dotazů a existujících dokumentů.
Zdrojem pro tyto texty jsou veřejně dostupné informace z webových stránek Fakulty informatiky a statistiky (FIS), Vysoké školy ekonomické v Praze (VŠE) a dalších relevantních webů.
Tyto texty byly následně předzpracovány, rozděleny na tematicky koherentní úseky a doplněny metadaty, což umožňuje přesné a efektivní vyhledávání při zodpovídání dotazů.

### Jazykový model
Pro generování odpovědí je použit model gpt-3.5-turbo prostřednictvím API od OpenAI.


## Cíl projektu:
Hlavním cílem diplomové práce je zkoumat možnosti, jak snížit náklady na jeho provoz a současně zlepšit kvalitu poskytovaných odpovědí.
- Každá experimentální verze chatbota má svou vlastní složku, například experiment1/, experiment2/ a podobně. Každá z těchto složek obsahuje samostatný kód a související dokumentaci.
- README.md soubory ve složkách experimentů poskytují podrobnosti o každé verzi chatbota, včetně implementovaných funkcí a technických specifikací.

Kód je rozdělen tak, aby každá verze mohla být testována a analyzována nezávisle, což umožňuje snadné porovnání výsledků mezi různými experimentálními verzemi. Pro snadnou navigaci v repozitáři jsou v hlavním README.md uvedeny odkazy na jednotlivé experimentální verze, což umožňuje rychlý přístup ke každému kódu a jeho dokumentaci.

- [Experiment 1](experiment1/README.md) – Popis experimentální verze 1.
- [Experiment 2](experiment2/README.md) – Popis experimentální verze 2.
- [Experiment 3](experiment3/README.md) – Popis experimentální verze 3.
