## 🧭 Motivace pro experiment 3

Na základě těchto zjištění byl navržen mechanismus podmíněného výběru textových úseků:

- Pokud je skóre podobnosti velmi vysoké (např. > 0.9), systém využije přímo odpověď z metadat bez zapojení generátoru.
- Pokud je skóre nízké (např. < 0.8), generátor se nespustí vůbec a dotaz je uložen k dalšímu zpracování.
- Pouze při střední úrovni shody je spuštěno generování s využitím relevantního kontextu.

Tento přístup výrazně snižuje zbytečné využívání zdrojů, zvyšuje kvalitu výstupu a zlepšuje nákladovou efektivitu celého systému.


<img width="501" alt="image" src="https://github.com/user-attachments/assets/397e3963-32a8-431d-84ac-1f418a44038b">

## 🔍 Shrnutí problému v experimentu 3
- Generátor často nedokázal využít celý obsah relevantního textu – například odpověď zahrnovala jen část z více potřebných informací.
![image](https://github.com/user-attachments/assets/bb5356a2-c83c-400b-a6c5-f05165e23c41)


