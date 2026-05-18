# Zomato AI Restaurant Recommender

AI-powered restaurant recommendations using the [Zomato Hugging Face dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) and an LLM (later phases).

## Documentation

- [Context](docs/context.md) — requirements
- [Architecture](docs/architecture.md) — system design
- [Implementation plan](docs/implementation-plan.md) — phased delivery
- [Schema mapping](docs/schema-mapping.md) — dataset column mapping (Phase 1)
- [Edge cases](docs/edge-cases.md)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # optional overrides
```

## Phase 1: Data ingestion

Ingest and cache the dataset (first run downloads from Hugging Face; later runs use `data/restaurants.json`):

```bash
python scripts/ingest.py
```

Force refresh:

```bash
python scripts/ingest.py --force
```

Dev subset (faster):

```bash
python scripts/ingest.py --max-rows 1000
```

Bootstrap via main entrypoint:

```bash
python src/main.py
```

## Phase 3: LLM ranking

Full pipeline with OpenAI (requires `LLM_API_KEY`) or offline fallback:

```bash
python scripts/recommend_demo.py --location Bangalore --budget medium --cuisine Italian --min-rating 4.0
```

Mock provider (no API key):

```bash
python scripts/recommend_demo.py --location Bangalore --budget medium --cuisine Italian --provider mock
```

Ollama (local):

```bash
set LLM_PROVIDER=ollama
set LLM_MODEL=llama3.2
python scripts/recommend_demo.py --location Bangalore --budget medium --cuisine Italian
```

## Phase 2: Filtering

Validate preferences and filter cached restaurants (no LLM):

```bash
python scripts/filter_demo.py --location Bangalore --budget medium --cuisine Italian --min-rating 4.0
```

## Tests

```bash
pytest
```

## Project layout

```text
src/
  domain/           # Models, normalization
  infrastructure/   # Config, ingestion, repository
  application/      # (Phase 4+)
  presentation/     # (Phase 5+)
scripts/ingest.py
tests/unit/
data/               # Cached restaurants (gitignored)
```
