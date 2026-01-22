## Bug autopsy (Day3)

1) Objaw:
- Różne pytania zwracały te same fragmenty i te same odpowiedzi.

2) Przyczyna źródłowa:
- Wewnątrz ask_query(question) zmienna `question` była NADPISYWANA przez STAŁY STRING.

3) Dowód (co wydrukowaliśmy / sprawdziliśmy):
- API wydrukowało req.query i było ono różne dla dwóch żądań.
- query_rag wydrukowało pytanie DEBUG i było ono INNE niż req.query.

4) Naprawa:
- Usunięto linię, która nadpisywała `question`, więc osadzanie + pobieranie + monit wykorzystują parametr funkcji.

5) Wniosek:
- Gdy wyniki nie zmieniają się wraz z danymi wejściowymi, przed dostosowaniem parametrów należy najpierw sprawdzić przepływ danych za pomocą logów.