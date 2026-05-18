# Project Context: AI-Powered Restaurant Recommendation System

This document captures the full requirements and design context from `docs/problemStatement.txt`. Use it as the single source of truth when implementing or extending this project.

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations.

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM to generate personalized, human-like recommendations
4. Displays clear, useful results to the user

## Data Source

| Item | Detail |
|------|--------|
| **Dataset** | Zomato restaurant data on Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related attributes |

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract fields needed for filtering and display: name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect preferences from the user:

| Preference | Examples / notes |
|------------|------------------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant records that match user input
- Pass structured, filtered results into an LLM prompt
- Design a prompt that enables the LLM to **reason** and **rank** options

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants
- **Explain** why each recommendation fits the user
- **Optionally** summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format. Each result should include:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation (why it was recommended)

## Architecture Summary

```
[Hugging Face Dataset] → [Preprocess / Filter] → [Structured candidates]
                                                        ↓
[User preferences] ──────────────────────────→ [LLM prompt + ranking]
                                                        ↓
                                              [Formatted recommendations]
```

## Key Technical Decisions (to be made during implementation)

- **Runtime / UI**: Web app, CLI, or API — not specified in the problem statement
- **LLM provider**: Not specified; choose based on API access and cost
- **Filtering**: Apply hard filters (location, budget, rating) before LLM; use LLM for ranking and natural-language explanations
- **Prompt design**: Critical path — must include user prefs, candidate list, and instructions for ranking + justification

## Success Criteria

- End-to-end flow: ingest data → collect prefs → filter → LLM recommend → display results
- Recommendations feel personalized and are explained in natural language
- Output is readable and actionable (name, cuisine, rating, cost, explanation)

## Reference

- Original problem statement: `docs/problemStatement.txt`
