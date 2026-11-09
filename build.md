# Build & Architecture Specification

## Overview
This document details the build execution, architectural structure, and technical verification of the Library Management System (LMS) implemented according to `writing-block.md`.

## Architecture Layers
1. **Database Layer (`database/`)**:
   - SQLite (`lms.db`) with `PRAGMA foreign_keys = ON`.
   - SQLAlchemy Declarative Base with 6 relational tables: `users`, `books`, `issues`, `fines`, `payments`, `audit_logs`.
   - Automated idempotent migrations and seed data scripts.

2. **Backend Microservices (`services/`)**:
   - `userservice` (Port 8001): User registration, ID generation, login validation, profile management.
   - `bookservice` (Port 8002): Book catalog, stock level controls, soft archive deletion.
   - `issueservice` (Port 8003): Issue & return operations, loan period enforcement, overdue fine computation.
   - `paymentservice` (Port 8004): Simulated fine payments, partial payments, transaction reference generation.
   - `adminservice` (Port 8005): Library metrics, aggregates, Plotly charts data, audit log retrieval.

3. **Frontend Layer (`frontend/` & `app.py`)**:
   - Built with Streamlit and Plotly.
   - Dynamic role-based interface routing (Admin vs Member).
   - Responsive layouts, session persistence, and error handling.

4. **Utilities & Clients (`utils/`)**:
   - `api_client.py`: Centralized HTTP REST client for microservice interaction.
   - `auth.py`: Role and credential validation logic.
   - `helpers.py`: Formatting, transaction reference generation, data validation.

