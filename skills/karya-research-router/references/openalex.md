# OpenAlex discovery guidance

Official documentation: <https://docs.openalex.org/>

OpenAlex is a scholarly metadata graph useful for discovering works and building a reproducible literature set. Configure `OPENALEX_API_KEY` for reliable production use; limited anonymous behavior may change with the service.

## Search modes

- keyword search: broad lexical discovery and filtering;
- boolean query: combine explicit concepts when supported by the API;
- semantic search: related-concept discovery with smaller result limits.

Use year, open-access, work type, concept, and citation filters only when they serve the contract. Record the exact query and filters.

## Evidence boundary

OpenAlex titles, metadata, citation counts, and reconstructed abstracts help locate work. They do not replace reading the original paper. Citation count is not a quality score, and absence from OpenAlex is not proof that evidence does not exist.

## Local utility

Run:

```powershell
python scripts/search-openalex.py "query" --mode keyword --limit 20 --year-from 2020
```

Use `--open-access` when appropriate and `--out results.json` for a durable retrieval artifact.
