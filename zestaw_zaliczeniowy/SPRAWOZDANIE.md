# Sprawozdanie — Zestaw Zaliczeniowy AAP

**Autor:** Dominik Kozieł · **Dataset:** `stanfordnlp/imdb` (50 000 recenzji) · **Środowisko:** Python 3.11.9, PySpark 4.1.1, JDK 17

Notebook `AAP_Zestaw_Zaliczeniowy.ipynb` jest **uruchamialny od góry do dołu** (zweryfikowane przez `jupyter nbconvert --execute`, 0 błędów, 14/14 komórek kodu wykonanych). Poniżej zwięzłe omówienie każdego zadania wraz z faktycznymi wynikami z wykonania.

## Setup

```bash
source ../.venv/bin/activate          # venv repo (PySpark z Lab 5)
pip install datasets scikit-learn
python preflight_download.py          # cache datasetu imdb (raz, ~9s)
jupyter notebook AAP_Zestaw_Zaliczeniowy.ipynb
```

Spark wykrywa `JAVA_HOME` automatycznie (na macOS `openjdk@17` z Homebrew).

---

## Lab 1 — Dekoratory (`@retry` + `@cache_to_disk`)

- `retry` ponawia przy wyjątku z exponential backoff (`delay * backoff**próba`); po wyczerpaniu prób re-raise ostatniego wyjątku.
- `cache_to_disk` używa `md5(repr(args))` jako klucza; cache hit **nie wykonuje ciała** funkcji.
- **Wynik:** empiryczny sukces **99/100 = 0.990** vs teoria `1 - 0.5^5 = 0.969`; cache: `r1 == r2 == True`, 100 plików.
- **Insight:** kolejność dekoratorów ma znaczenie (`@cache_to_disk` na zewnątrz → cache hit przed retry). Cache na dysku trzeba czyścić na starcie, inaczej benchmark mierzyłby stare wyniki, nie retry.

## Lab 2 — Współbieżność (multiprocessing CPU-bound)

- `sentiment_score` (lexicon-based) zapisany do **modułu** `sentiment_lib.py` — wymóg picklowalności przy `spawn` na macOS.
- **Wynik (5000 recenzji, 10 rdzeni):** sekwencyjnie **0.131 s**, ThreadPool **0.175 s**, multiprocessing **0.116 s**. Najszybszy: multiprocessing.
- **Insight:** ThreadPool najwolniejszy — GIL serializuje pracę CPU-bound. multiprocessing wygrywa, ale minimalnie, bo praca/element jest mała i narzut IPC prawie zjada zysk; przewaga procesów rośnie dopiero przy cięższej pracy na element. `chunksize=100` ogranicza narzut serializacji.

## Lab 3 — Testowanie (pytest dla `Tokenizer`)

- `Tokenizer` (HTML strip + lower + `re.findall(r"\w+", re.UNICODE)` + filtr `min_length`) + `vocab`.
- Testy: fixtures (`tokenizer`, `imdb_sample`), `parametrize` (6 przypadków brzegowych z polskimi diakrytykami), `xfail` (e-mail), test integracyjny na imdb. Uruchamiane przez `subprocess` (ścieżki absolutne).
- **Wynik:** **9 passed, 1 xfailed**. Unikalnych tokenów na 100 recenzji: **5053**.
- **Insight:** słownik rośnie sub-liniowo (prawo Heapsa); `parametrize` właściwy gdy ten sam assert na wielu wejściach; `xfail` dokumentuje znany dług bez wywracania CI.

## Lab 4 — Bazy danych (NoSQL-style JSON w SQLite)

- Tabela `reviews_json(id, doc)` z dokumentem JSON (`stats`, `tags`); 4 zapytania przez `json_extract`.
- **Wynik:** rozkład klas 1000/1000; avg word_count neg 224.7 / pos 232.2; `tags LIKE '%movie%'` → 169 (łapie też „movies"); top5 najdłuższe pozytywne. **Rozmiar:** SQL 3 215 360 B < JSON 3 518 464 B; **read agg:** SQL 0.0005 s « JSON 0.0175 s.
- **Insight:** dla tego problemu (agregacje po wymiarach) wygrywa klasyczny SQL — JSON powtarza nazwy kluczy w każdym wierszu i wymaga parsowania przy każdym odczycie. `LIKE` na zserializowanej tablicy to pseudo-NoSQL (dopasowanie podciągu, nie członkostwa). JSON opłaca się przy zmiennym schemacie i dostępie „cały dokument po kluczu".

## Lab 5 — PySpark (window functions)

- `df_words` → ranking w klasie (`row_number`), top 3 per klasa, różnica od średniej klasowej (`avg().over(partitionBy)`), moving average w oknie 50 wierszy (`rowsBetween(-49, 0)`), wykres liniowy 2 klas.
- **Wynik:** top 3 (neg: 1020/1018/1014 słów; pos: 1000/998/996); diff od średniej do +789.5; wykres `moving_avg.png`.
- **Insight:** window ≠ groupBy (zachowuje wiersze). `rowsBetween` (nie `rangeBetween`), bo `id` nieciągłe po shuffle. Lazy eval — błąd okna wybucha dopiero przy akcji; `toPandas()` ściąga do drivera (ryzyko OOM na produkcji).

## Lab 6 — Data Quality (kontrakt + raport JSON)

- `DataContract.add_rule(name, check, severity)` (fluent API) + `DataValidator.validate` zwracający raport; reguły `error` które padną → `raise` (fail fast), raport zapisany **przed** wyjątkiem.
- 6 reguł + bonus `no_html_tags`. **Wynik:** wszystkie reguły `error`/`warning` OK poza `no_html_tags` → **WARN 1189/2000 (59.5%)**; kontrakt zaliczony. Raport: `_workspace/data_quality_report.json`.
- **Insight:** dwa poziomy severity = audyt (warning, raportuje) vs kontrakt (error, blokuje). HTML w imdb jako `warning` daje sygnał „wyczyść przed treningiem" bez blokowania zbioru. W produkcji potrzeba obu: audyt znajduje nowe problemy, kontrakt pilnuje by znane nie wróciły.

---

## Artefakty (`_workspace/`)

`sentiment_bench.png`, `moving_avg.png` (wykresy) · `data_quality_report.json` (raport DQ) · `tokenizer.py` + `test_tokenizer.py` + `sentiment_lib.py` (moduły) · `imdb_json.db`, `imdb_sql_timed.db` (bazy) · `flaky_cache/` (cache Lab 1).
