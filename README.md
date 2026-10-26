# Multimodal Hybrid RAG System

> A source-grounded, multimodal question-answering system for discovering the history of places through text and images.

This project is designed to answer questions about Japanese history and places using text or image queries. It combines OCR and image processing, dense vector search, BM25 keyword search, result fusion, reranking, grounded language-model generation, citations, guardrails, conversation memory, evaluation, and observability.

The structure below is the planned implementation layout. Every file and directory is documented with a short inline `#` explanation, while the tree layout is preserved for quick reference.

## Project Structure

history-rag/
│
├── config/
│   ├── settings.yaml
│   ├── logging.yaml
│   └── prompts.yaml
│
├── data/
│   ├── raw/                        # Original Japan history PDFs
│   ├── interim/                    # Extracted PDF text
│   ├── processed/                  # Validated structured JSON
│   ├── chunks/                     # Chunked documents + metadata
│   ├── evaluation/                 # Questions, references, test cases
│   └── vector_store/               # Persistent vector index (local dev)
│
├── notebooks/
│   ├── data_exploration.ipynb
│   ├── chunking_experiments.ipynb
│   ├── embedding_experiments.ipynb
│   └── retrieval_evaluation.ipynb
│
├── src/
│   └── history_rag/
│       ├── __init__.py
│       │
│       ├── ingestion/
│       │   ├── pdf_loader.py
│       │   ├── text_extractor.py
│       │   ├── ocr_processor.py
│       │   └── json_converter.py
│       │
│       ├── chunking/
│       │   ├── text_splitter.py
│       │   └── metadata_enricher.py
│       │
│       ├── embeddings/
│       │   ├── embedding_model.py
│       │   └── embedding_pipeline.py
│       │
│       ├── retrieval/
│       │   ├── dense_retriever.py
│       │   ├── bm25_retriever.py
│       │   ├── hybrid_retriever.py
│       │   └── fusion.py
│       │
│       ├── reranking/
│       │   └── reranker.py
│       │
│       ├── generation/
│       │   ├── llm_client.py
│       │   ├── answer_generator.py
│       │   ├── output_parser.py
│       │   ├── block_delimiter.py
│       │   └── citation_formatter.py
│       │
│       ├── guardrails/
│       │   ├── input_validator.py
│       │   ├── evidence_checker.py
│       │   ├── citation_validator.py
│       │   ├── output_validator.py
│       │   └── retry_policy.py
│       │
│       ├── evaluation/
│       │   ├── retrieval_evaluator.py
│       │   ├── generation_evaluator.py
│       │   ├── citation_evaluator.py
│       │   └── evaluation_dataset.py
│       │
│       ├── suggestions/
│       │   ├── suggestion_generator.py
│       │   └── suggestion_ranker.py
│       │
│       ├── memory/
│       │   ├── conversation_memory.py
│       │   ├── session_manager.py
│       │   └── memory_store.py
│       │
│       ├── multimodal/
│       │   ├── image_processor.py
│       │   ├── image_query_handler.py
│       │   └── image_retriever.py
│       │
│       ├── graph/
│       │   ├── state.py
│       │   ├── workflow.py
│       │   ├── routing.py
│       │   ├── checkpointer.py
│       │   └── nodes/
│       │       ├── input_node.py
│       │       ├── intent_node.py
│       │       ├── retrieval_node.py
│       │       ├── reranking_node.py
│       │       ├── generation_node.py
│       │       ├── validation_node.py
│       │       ├── suggestion_node.py
│       │       ├── memory_node.py
│       │       └── human_review_node.py
│       │
│       ├── observability/
│       │   ├── logging_config.py
│       │   ├── tracing.py
│       │   ├── metrics.py
│       │   └── request_context.py
│       │
│       ├── schemas/
│       │   ├── document.py
│       │   ├── answer.py
│       │   ├── citation.py
│       │   ├── suggestion.py
│       │   └── feedback.py
│       │
│       ├── api/
│       │   ├── main.py
│       │   ├── dependencies.py
│       │   ├── middleware.py
│       │   └── routes/
│       │       ├── chat.py
│       │       ├── streaming.py
│       │       ├── feedback.py
│       │       ├── review.py
│       │       └── health.py
│       │
│       └── utils/
│           ├── config_loader.py
│           ├── file_handler.py
│           └── exceptions.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── chat.js
│       ├── streaming.js
│       ├── suggestions.js
│       └── human_review.js
│
├── scripts/
│   ├── ingest_pdfs.py
│   ├── build_index.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_generation.py
│   └── run_api.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   └── test_streaming.py
│
├── docker/
│   └── Dockerfile
│
├── .env.example
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
## Request Flow

```text
Text or image query
        |
        v
Input validation and intent detection
        |
        v
Text/OCR/image processing
        |
        v
Dense retrieval + BM25 retrieval
        |
        v
Fusion and reranking
        |
        v
Evidence-grounded answer generation
        |
        v
Citation and output validation
        |
        v
Answer, sources, suggestions, and optional human review
```

## Development Workflow

1. Place source PDFs in `data/raw/`.
2. Copy `.env.example` to `.env` and set `GLM_API_KEY` with your GLM API key.
3. Run `python -m scripts.data_ingestion` to extract and normalize source content.
   The generated JSON is written to `data/processed/kyoto_cultural_history.json`.
   Its `processing.token_usage` field contains aggregate prompt, completion,
   total-token, and request counts; each page also contains `token_usage`.
4. Run `scripts/build_index.py` to create chunks, embeddings, and search indexes.
5. Run the evaluation scripts before changing retrieval or generation settings.
6. Start the API with `scripts/run_api.py`.
7. Use the frontend to submit text or image questions.
8. Run unit, integration, and evaluation tests before contributing changes.

## Responsible Use

Historical sources can be incomplete, conflicting, or biased. Answers should show supporting sources, communicate uncertainty, protect uploaded data, and avoid presenting unsupported generated content as established fact.

## License

This project is distributed under the [MIT License](LICENSE).
