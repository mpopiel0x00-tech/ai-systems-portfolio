# Day 1 — System map (RAG skeleton)

## Pipeline (1–2 zdania na etap)
1) Ingest (src/ingest.py): wejście -> wyjście -> po co
- Input: Na input wchodzi nieprzetworzony raw plik z tekstem z folderu raw/.
- Output: Na wyjściu program dzieli raw tekst na pomniejsze chunki tekstu przydzielając każdemu chunkowi ID dokumentu z raw/ i indywidualne ID chunku i zamieszcza w pliku w folderze processed/
- Why: Aby umożliwić szukanie programowi cytowań na bazie skojarzeń duży plik tekstowy musi być podzielony na krótsze ciągi znaków.

2) Index (src/index_qdrant.py): wejście -> wyjście -> po co
- Input: Jako input wchodzi plik z gotowymi chunkami w processed/
- Output: kolekcja w Qdrant (docs_v1) zawierająca wektory embeddingów + payload (metadane + tekst).
- Why: żeby retrieval działał: Qdrant robi wyszukiwanie podobieństwa po wektorach.

3) Query (src/query_rag.py): wejście -> wyjście -> po co
- Input: pytanie (string) + prompt template + dostęp do Qdrant + modele (embedding + LLM).
- Output: odpowiedź LLM + lista retrieved_chunk_ids + czas + log runu.
- Why: retrieval znajduje kontekst, generation buduje odpowiedź “uziemioną” w kontekście.

## Data contracts (konkretnie)
4) Co jest w chunks.jsonl? (wymień pola)
- doc_id, chunk_id, text, char_len

5) Co jest w Qdrant payload? (wymień pola)
- Payload = “dodatkowe pola” przechowywane przy punkcie w Qdrant: doc_id, chunk_id, text

6) Co jest w logs/runs.jsonl dla run_type=index i run_type=query? (wymień 4–6 pól)
- index: ts, collection, qdrant_url, embed_model, chunt_count_in, points_written, embed_errors, elapsed_sec
- query: ts, question, top_k, retrieved_chunk_ids, answer, elapsed_sec

## Debug checklist (bez “zależy”)
7) Jeśli odpowiedź ma złe cytowania, sprawdzam:
- (a) Czy pytania są dobrze sformułowane
- (b) Czy TOP_K nie jest za niskie

8) Jeśli retrieval zwraca wciąż te same chunki, sprawdzam:
- (a) Czy pytania są różne semantycznie
- (b) Czy embedding model i kolekcja są te same + czy indeks nie został “zabetonowany” na jednym podobnym fragmencie (często: zbyt duże/mało zróżnicowane chunki, albo dokument ma powtarzalne akapity)
- (c) Czy query embedding faktycznie liczy się z pytania (a nie np. stały string)

client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=q_emb,
        limit=TOP_K,
        with_payload=True,
    )

prompt = PROMPT_PATH.read_text(encoding="utf-8").format(
        context=context,
        question=question,
    )