# Testing & Observability Guide

This document outlines the testing strategy, manual LLM evaluation procedures, performance verification, and logging expectations for the restaurant recommendation system.

---

## 1. Automated Testing

To run the full suite of automated tests (including unit and integration tests):

```bash
pytest
```

To run with coverage information:

```bash
pytest --cov=src tests/
```

### Key Tested Behaviors:
- **Hard Filters**: Deterministic location, budget, cuisine, and minimum rating filtering.
- **Cache Ingestion**: Local cache hit mechanism and fallback to cache on Hugging Face API errors.
- **LLM Error Recovery**: Multi-try strict JSON recovery and rating-based fallback.
- **Prompt Injection Sanitation**: Cap and character stripping on `additional_preferences`.
- **E2E Flow**: Full request-response cycles for happy path, empty candidate sets, and LLM downtime.

---

## 2. Manual LLM Evaluation (Evaluation Checklist)

Since LLM outputs are non-deterministic, developers should perform manual evaluations periodically. Run the recommendation script using a real LLM provider (e.g., Groq, OpenAI, Ollama) and cross-examine results against the following checklist:

| Verification Item | Success Criteria | Action on Failure |
|-------------------|------------------|-------------------|
| **Zero Hallucination** | Every restaurant in the output recommendations MUST have an ID that matches one of the input candidates from the dataset. | If the parser retries and still fails, verify prompt templates and ensure LLM temperature is $\le 0.4$. |
| **Constraint Alignment** | Explanations must mention how the restaurant matches the requested location, budget, and cuisine. | Check the PromptBuilder system prompt to ensure constraints are clearly stated. |
| **Additional Preferences** | If the user provided additional preferences (e.g. "rooftop seating", "family-friendly"), the explanations must explicitly address those requirements. | Verify `additional_preferences` is injected cleanly into the prompt user message without formatting bugs. |
| **Rank Integrity** | Recommendations must be sorted by rank $1 \dots K$ with no duplicate ranks. | Check `RankingOrchestrator._to_recommendations` ranking logic. |

### Sample Evaluation Command:
```bash
python scripts/recommend_demo.py --location bangalore --budget medium --cuisine Italian --additional "outdoor seating"
```

---

## 3. Performance Smoke Test & Ingestion Cache

### A. Ingestion Cache Hit Verification
To ensure that ingestion is not repeated on every request (which would cause massive startup/network delays):

1. **First Run (Cold Path)**: Run the ingestion/demo script. You should see a log entry confirming download from Hugging Face:
   ```text
   Ingesting dataset from Hugging Face: ManikaSaini/zomato-restaurant-recommendation
   ```
2. **Subsequent Runs (Warm Path)**: Run the script again. The service must load from the local cache instead:
   ```text
   Loading restaurants from cache: data/restaurants.json
   ```

### B. Latency Observability
Check application logs to observe candidate filtering count and LLM completion latency. Each LLM request logs latency and the size of the candidate set:

```text
INFO:domain.ranking.ranking_orchestrator:LLM completion latency: 1.234s for model gpt-4o-mini. Candidates considered: 15
```

- **Target Latency**: LLM completions should complete under 3 seconds under normal network conditions.
- **Candidate Cap**: Confirm that the number of candidate restaurants sent to the LLM never exceeds the `MAX_CANDIDATES` environment variable (default: 30), keeping tokens bounded.
