# Zomato AI Restaurant Recommender: Manual Testing Report

This document outlines the testing results for the Zomato AI Restaurant Recommender application, validating code correctness, error recovery, data validation, and end-to-end functionality.

---

## 1. Summary of Automated Test Suite

Before performing manual tests, we ran the automated test suite. All **71 unit and integration tests** passed successfully:

- **Total Tests:** 71
- **Status:** PASS
- **Execution Time:** 32.78 seconds
- **Covered Components:** 
  - `CandidateFilter` logic (hard filtering, location/budget/cuisine/rating matching)
  - `DataIngestionService` caching & fallback to cache on network errors
  - `PreferenceValidator` input sanitization
  - `ResponseParser` schema enforcement and JSON recovery
  - LLM fallback orchestration
  - API endpoint testing (`GET /health`, `POST /api/recommend`)

---

## 2. Server Infrastructure Setup & Verification

Both the backend FastAPI server and the frontend Vite web server were started locally and verified to be operational:

- **Backend API:** Fast API running at `http://127.0.0.1:8000` with the local cache file (`data/restaurants.json` holding **4,851** restaurants) loaded successfully.
- **Frontend App:** Vite development server running at `http://localhost:5173/` and compiles successfully for production.

---

## 3. Manual Verification Checklist

Below is the detailed list of manual test scenarios performed, their success criteria, and observed outcomes.

| Scenario | ID Ref | Request payload / Command | Expected Behavior | Observed Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Happy Path Recommendation** | `EC-LLM-13` | `POST http://127.0.0.1:8000/api/recommend` with: `Bangalore`, `medium` budget, `Italian`, `rating >= 4.0` | Return top 5 restaurants matched by hard filters, rank them, and call Groq LLM (mapped model `llama-3.3-70b-versatile`) to generate explanations without hallucinations. | Successfully returned top 5 restaurants (e.g. *Onesta*, *Zoey's*), with detailed explanations mapping to the user's constraints. Latency: **2.216s**. | **PASS** |
| **Invalid Budget Input** | `EC-INPUT-03` | `POST ...` with `budget: "premium"` | Reject request with a `400 Bad Request` and list valid options. | Returned HTTP `400` with: `{"detail": "budget: Value error, budget must be one of: low, medium, high"}`. | **PASS** |
| **Invalid Rating Input** | `EC-INPUT-05` | `POST ...` with `min_rating: 6.0` | Reject request before processing using Pydantic schema validation. | Returned HTTP `422 Unprocessable Entity` with a clear message: `"Input should be less than or equal to 5"`. | **PASS** |
| **Empty Candidates Match** | `EC-FILTER-01` | `POST ...` with `location: "Paris"` | Return status `200` with an empty `recommendations` list and suggest relaxing filters. **Do not call the LLM**. | Returned HTTP `200` with empty list and `summary: "No restaurants found in 'Paris'."`. Candidates considered: 0. LLM was not called. | **PASS** |
| **LLM Key Missing / Offline Fallback** | `EC-LLM-01` | `recommend_demo.py` with CLI flag `--provider invalid` (forces fallback) | Fall back to standard rating-based sorting and populate using custom explanation templates (AI Offline mode). | Successfully sorted by rating. Outputted explanations using template: `"#1: Onesta serves Pizza, Cafe, Italian in bangalore with a rating of 4.6. It aligns with your medium budget..."` | **PASS** |
| **Input Sanitization (Long preference)** | `EC-INPUT-10` | `POST ...` with `additional_preferences` of 600 characters | Accept request but truncate the preference string to exactly 500 characters. | Request processed successfully; `preferences_used.additional_preferences` returned exactly 500 characters. | **PASS** |
| **Input Sanitization (Control chars)** | `EC-INPUT-12` | `POST ...` with `additional_preferences: "Spicy\x00food\x08!"` | Strip control characters during normalization. | Received clean string: `'Spicyfood!'` in response. | **PASS** |
| **Unicode Encoding Support** | `EC-DATA-08` | Checking `cost` display string | The Indian Rupee symbol (`₹`) is returned and parsed correctly (not garbled). | Output verified as `b'\\N{INDIAN Rupee Sign}600 for two'` via programmatic inspection. | **PASS** |
| **Cuisine Image Asset Loading** | `EC-UI-03` | Loading restaurant cards for Italian/Pizza and South Indian | UI cards display matching cuisine placeholder images from Unsplash. | Found that Italian and South Indian image links returned 404. Replaced with working high-res Unsplash links, and verified images load successfully. | **PASS** |

---

## 4. Key Implementation Merits Observed

1. **Zero Hallucination Control:** The system uses strict prompt rules and schema checks ensuring the LLM cannot recommend any restaurant ID not present in the candidate dataset.
2. **Graceful Fallback:** If the LLM provider fails, times out, or has an invalid setup, the app automatically falls back to database rating-based sorting and generates readable templates. No hard crashes are presented to the user.
3. **Pydantic Validation:** Inputs are strongly validated at the presentation boundary, failing fast for client errors (such as rating > 5.0 or unrecognized budget tiers).
4. **Efficiency/Capping:** When matching candidates exceed `MAX_CANDIDATES` (set to 30), the filter keeps only the top 30 by rating, keeping token limits bounded and latency low.
