# Project Story

HEX was created for an AI full-stack hackathon as a medical-textbook knowledge-integration prototype. It combines PDF parsing, knowledge-graph construction, semantic alignment across textbooks, report generation, and RAG question answering behind a FastAPI service and a React visualization frontend.

The competition work progressed from single-textbook extraction to a P2 flow with multiple uploads, cross-textbook deduplication, source tracking, interactive Cytoscape visualization, configurable thresholds, and concurrent job-state handling. The repository retains the requirements, architecture notes, submission guide, demo script, and final retrospective as evidence of both implementation and decision-making.

## Archive decision

The competition and its final review are complete. The project is archived rather than deleted because its combination of medical content integration, graph visualization, and documented architecture is a substantive public portfolio artifact.

During archive review on 2026-08-24, a local untracked conversation dump was removed because it contained a real API credential and machine-specific paths. It was never added to Git. Runtime `.env` files, textbook PDFs, vector indexes, and generated runtime data remain outside the repository boundary.
