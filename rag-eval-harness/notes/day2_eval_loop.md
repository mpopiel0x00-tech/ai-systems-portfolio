# Day 2 — Eval loop (v0)

## Co mierzymy (1 zdanie każde)
1) format_valid: Czy LLM zwrócił poprawny format odpowiedzi i czy nie jest pusta
2) citation_count: ile razy w odpowiedzi występuje wzorzec cytowania [source1__0007]
3) citation_coverage: Czy w ogóle są cytowania
4) context_hit: czy expected_points (słowa-klucze) występują w zretrievowanym kontekście (tekst chunków), nie w samej odpowiedzi.
5) latency_ms: czas jednego testu end-to-end

## Co to są “buckets” i po co są (2–3 zdania):
- buckets to ustalone testy prewencyjne nałożone na wygenerowany output, sprawdz poprawność formatu odpowiedzi, jak precyzyjna jest odpowiedzi w stosunkku do skojarzeń.

## Bucket rules (własnymi słowami)
6) FORMAT_FAIL = Oznacza niepoprawny format (JSON) zwróconej odpowiedzi lub puste.
7) NO_RETRIEVAL = Retrieval zwrócił 0 chunków
8) WRONG_CONTEXT = retrieval zwrócił chunki, ale expected_points nie ma w retrieved_text -> system patrzy w złą część dokumentu
9) UNGROUNDED = answer nie ma cytowań (citation_count == 0), bez źródeł

## Jedna hipoteza (konkret)
10) Dlaczego wcześniej context_hit_rate było 0.0 i co naprawiliśmy?
- Bo wcześniej sprawdzany był expected_points przeciwko chunk_id zamiast przeciwko tekstom chunków

## Actionable next step (jedno zdanie)
11) Gdy 80% to WRONG_CONTEXT, pierwsza rzecz jaką zmieniam to expected_points (czy są w ogóle w dokumencie i czy są “retrievable”), potem retrieval params (chunk_size/top_k), potem prompt.
