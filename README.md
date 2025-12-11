<<<<<<< HEAD
# LLM Response Evaluation Pipeline

This repository contains a robust, automated pipeline designed to evaluate the reliability of Large Language Model (LLM) responses. It acts as an automated "Judge," measuring **Hallucination**, **Relevance**, and **Completeness** by strictly comparing AI responses against retrieved Context vectors.

## 📂 Project Structure

```
llm-eval-pipeline/
├── data/
│   ├── sample-chat-conversation-*.json  # Normalized conversation logs
│   ├── sample_context_vectors-*.json    # Normalized RAG context chunks
│   └── reports/                         # Generated JSON evaluation reports
├── evaluator.py         # Core logic (Semantic Similarity & Hallucination detection)
├── main.py              # Orchestrator (Loads data, runs checks, saves reports)
├── clean_data.py        # ETL script (Cleans & normalizes raw production data)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

## 🛠️ Technology Stack & Approach

- **Language:** Python 3.11.8
- **Core Engine:** sentence-transformers (Model: all-MiniLM-L6-v2)
- **Math Backend:** scikit-learn (Cosine Similarity), numpy

### Why this Architecture?

The assignment required a solution that minimizes latency and costs while maintaining accuracy. I chose a **Vector-based Similarity Approach** rather than using an LLM API (like GPT-4) as the primary judge for these reasons:

- **Zero Marginal Cost:** Running local embeddings costs $0.00 per evaluation, whereas API-based evaluation scales linearly with traffic.
- **Ultra-Low Latency:** My tests show an average evaluation time of 0.03 - 0.05 seconds, making it suitable for near real-time monitoring.
- **Deterministic:** Mathematical similarity provides a stable baseline for regression testing, unlike the variable outputs of generative models.

## 🚀 Setup & Usage

### 1. Installation
Clone the repository and install the required dependencies.

```bash
git clone https://github.com/YOUR-USERNAME/llm-eval-pipeline.git
cd llm-eval-pipeline
pip install -r requirements.txt
```

### 2. Prepare Data (ETL)
The raw input data often contains noise (invalid JSON syntax, metadata). Run the setup script to normalize the data into clean, processable JSON files.

```bash
python clean_data.py
```

### 3. Run Evaluation
Execute the main pipeline. This will auto-discover chat/context pairs in the data/ folder and generate reports.

```bash
python main.py
```
## 📊 Evaluation Logic & Metrics

The pipeline calculates three key metrics:

### 1. Relevance Score (0-100%)
- **Logic:** Calculates the Cosine Similarity between the User Query embedding and the Context embeddings.
- **Goal:** Determines if the retrieved context was actually useful for the user's question.

### 2. Completeness Score (0-100%)
- **Logic:** A weighted hybrid score combining Semantic Similarity (60%) and Keyword Overlap (40%) between the AI Response and the Context.
- **Goal:** Ensures the AI didn't miss key details present in the source text.

### 3. Hallucination / Factual Accuracy Check
- **Logic:** The AI response is split into individual sentences. Each sentence is embedded and compared against the context.
- **Threshold:** If a sentence has a similarity score < 0.55 against all context chunks, it is flagged as Unsupported.
- **Output:** A "Hallucination Ratio" (e.g., 40% of sentences are unsupported).

## 📈 Scalability Strategy

**Question:** If we run your script at scale (millions of conversations), how do you ensure latency and costs remain minimum?

To scale this solution to production levels (millions of daily active users), I propose the following architecture evolution:

### Asynchronous "Sidecar" Architecture:
- Evaluation should never block the user's request. I would decouple the evaluation process using a message queue (e.g., Kafka or Celery).
- The user gets their answer immediately (0ms added latency). The evaluation happens in the background.

### Statistical Sampling:
- It is unnecessary to evaluate 100% of interactions. I would implement a Sampling Strategy (e.g., evaluating random 5% of traffic, or 100% of "Thumb Down" feedback) to control compute costs.

### Tiered "Judge" System:
- **Tier 1 (Current Solution):** Fast, cheap local embeddings filter the majority of traffic.
- **Tier 2 (LLM Judge):** Only if Tier 1 detects a high hallucination risk (e.g., score < 0.6), trigger a more expensive GPT-4 call for a detailed audit. This reduces API costs by ~90% while maintaining high safety standards.

## 📝 Test Results

### Test Run 1 (Hallucination Scenario):
- **Scenario:** AI claimed a specific room price ("Rs 2000 subsidized") not found in the context.
- **Result:** The pipeline correctly flagged 40% of sentences as unsupported.
- **Performance:** Latency: 0.046s | Cost: ~$0.000015

### Test Run 2 (Standard Query):
- **Scenario:** Standard medical advice query.
- **Result:** Low hallucination ratio (1 sentence flagged), higher completeness.
- **Performance:** Latency: 0.029s | Cost: ~$0.000008

---

**Author:** Rahul Mondal  
**Date:** December 2025
=======
# LLM_Evaluation_Pipeline
>>>>>>> 9de8db0c4b006a25c4aaef39d25f60dc8e63d5d0
