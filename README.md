# Automated-SQL-Reporting-Pipeline-with-AI-Powered-Failure-Diagnosis
SelfHealSQL

An AI-assisted, self-diagnosing SQL reporting pipeline for automated business reporting and SQL failure diagnosis.

SelfHealSQL is a practical data engineering project that simulates how a real analytics/reporting system can run business-critical SQL queries automatically, persist successful results, capture structured failures, and use a generative AI agent to explain what likely went wrong.

The project combines SQL Server, Python, scheduled automation, structured error logging, and generative AI into one end-to-end workflow.

The project description defines the goal as a self-diagnosing reporting pipeline that runs daily business metrics, stores successful outputs, captures failures, and uses AI to turn failures into structured diagnoses rather than raw stack traces.

Why This Project?

In a typical reporting environment, a scheduled SQL query may work for weeks and then suddenly fail because of:

Unexpected data values

Invalid dates

Schema changes

Incorrect data types

Missing or renamed columns

Other changes in the underlying data

A normal pipeline may simply produce an exception and require a developer or analyst to inspect the failure manually.

SelfHealSQL explores a more useful pattern:

Scheduled Report
       │
       ▼
Execute SQL Queries
       │
       ├──────────────► Success ──────► CSV Report
       │
       ▼
    Failure
       │
       ▼
Structured Failure Log
       │
       ▼
AI Diagnostic Agent
       │
       ▼
Root Cause + Affected Area
+ Confidence + Suggested Fix

The goal is not to let AI blindly modify production data. Instead, AI acts as a diagnostic assistant that interprets the available failure context and recommends the next debugging step.

Features

Automated Business Reporting

The runner executes five business-focused SQL reports:

Daily sales

Top-selling products

Sales by city

Failed transactions

Top customer segments

Successful query results are exported to timestamped CSV files.

Structured Failure Capture

When a query fails, the runner does not terminate the entire reporting process. It catches the exception and records structured information including:

Query name

Timestamp

Error message

Error type

SQL text

Python traceback

This information is stored as JSON in the logs/ directory.

AI-Powered SQL Diagnosis

The diagnostic agent reads previously captured failure JSON files and sends the relevant context to the Google Gemini API.

The model is instructed to return structured JSON containing:

likely_cause

affected_area

confidence

suggested_fix

This converts an unstructured SQL/Python error into an actionable diagnostic result.

Duplicate Diagnosis Prevention

The diagnostic agent checks whether a corresponding diagnosis already exists before processing a failure. This prevents the same failure log from being repeatedly diagnosed.

Synthetic Data Generation

The project includes a Faker-based data seeding script that generates realistic test data for:

300 customers

40 products

3,000 orders

Orders contain weighted statuses representing:

Completed

Failed

Pending

This provides a reproducible local environment for testing the reporting pipeline.

Failure-Oriented Testing

The project is designed to be tested by deliberately introducing bad data or schema conditions and checking whether the diagnostic agent can identify the likely failure pattern instead of merely repeating the error message.

Architecture

SelfHealSQL is organized as a small end-to-end data pipeline. SQL Server stores the business data, runner.py executes the reporting layer, successful results become CSV reports, and failed executions become structured JSON artifacts that are passed to the AI diagnostic layer.

End-to-End Architecture

flowchart TD
    A[Windows Task Scheduler] --> B[runner.py]

    B --> C[(SQL Server<br/>SelfHealSQL_DB)]

    C --> D{Execute 5<br/>Business Queries}

    D -->|Success| E[Generate CSV Reports]
    E --> F[reports/]

    D -->|Failure| G[Capture Failure Context]
    G --> H[logs/failure_*.json]

    H --> I[diagnose_agent.py]
    I --> J[Build Diagnostic Prompt]
    J --> K[Google Gemini API]

    K --> L[Structured Diagnosis]
    L --> M[diagnoses/diagnosis_*.json]

    M --> N[Developer / Data Team]
    F --> N

    style A fill:#f5f5f5,stroke:#333,stroke-width:1px
    style C fill:#f5f5f5,stroke:#333,stroke-width:1px
    style K fill:#f5f5f5,stroke:#333,stroke-width:1px
    style N fill:#f5f5f5,stroke:#333,stroke-width:1px

Pipeline Flow

┌─────────────────────────────┐
│   Windows Task Scheduler    │
│       Scheduled Job         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         runner.py           │
│      Query Runner           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         SQL Server          │
│       SelfHealSQL_DB        │
└──────────────┬──────────────┘
               │
               ▼
       ┌───────────────┐
       │ Execute Query │
       └───────┬───────┘
               │
       ┌───────┴────────┐
       │                │
    SUCCESS           FAILURE
       │                │
       ▼                ▼
┌────────────┐   ┌─────────────────┐
│ CSV Report │   │ Failure JSON    │
│ reports/   │   │ logs/           │
└─────┬──────┘   └────────┬────────┘
      │                    │
      │                    ▼
      │           ┌──────────────────┐
      │           │ diagnose_agent.py│
      │           └────────┬─────────┘
      │                    │
      │                    ▼
      │           ┌──────────────────┐
      │           │  Gemini API      │
      │           │  AI Diagnosis    │
      │           └────────┬─────────┘
      │                    │
      │                    ▼
      │           ┌──────────────────┐
      │           │ Diagnosis JSON   │
      │           │ diagnoses/       │
      │           └────────┬─────────┘
      │                    │
      └──────────┬─────────┘
                 ▼
        ┌─────────────────────┐
        │ Data Team / Analyst │
        │ Reports + Diagnosis │
        └─────────────────────┘

Component Responsibilities

Component

Responsibility

Windows Task Scheduler

Triggers the reporting workflow on a schedule

runner.py

Connects to SQL Server, executes each SQL report, saves successful results, and captures failures

SQL Server

Stores customers, products, orders, and order details

reports/

Stores successful query results as timestamped CSV files

logs/

Stores structured failure JSON files

diagnose_agent.py

Finds undiagnosed failures and sends their context to Gemini

Google Gemini API

Analyzes the SQL failure and produces a structured diagnosis

diagnoses/

Stores AI-generated diagnosis JSON files

Failure-Diagnosis Flow

The most important part of the architecture is the failure path:

sequenceDiagram
    participant S as SQL Server
    participant R as runner.py
    participant L as logs/
    participant A as diagnose_agent.py
    participant G as Gemini API
    participant D as diagnoses/

    R->>S: Execute business SQL query
    S-->>R: SQL error
    R->>L: Save structured failure JSON
    A->>L: Find undiagnosed failures
    L-->>A: Failure details
    A->>G: Send query + error + SQL context
    G-->>A: Structured diagnosis
    A->>D: Save diagnosis JSON

This separation keeps report execution, failure logging, and AI diagnosis independent. The AI agent does not directly modify the database; it produces a diagnosis and suggested next step for investigation.

Technology Stack

Layer

Technology

Database

Microsoft SQL Server

Database Driver

ODBC Driver 17 for SQL Server

Database Connectivity

pyodbc

Reporting Queries

T-SQL

Automation

Windows Task Scheduler

Runtime

Python

Synthetic Data

Faker

Configuration

python-dotenv

AI

Google Gemini API

AI SDK

google-genai

Report Format

CSV

Failure Format

JSON

The dependencies are defined in requirements.txt.

Database Design

SelfHealSQL uses four related SQL Server tables.

Customers
    │
    │ 1 ──────────────── N
    ▼
Orders
    │
    │ 1 ──────────────── N
    ▼
OrderDetails
    │
    │ N ──────────────── 1
    ▼
Products

Customers

Stores customer information and segmentation.

Important fields include:

CustomerID

FirstName

LastName

Email

City

State

Segment

SignupDate

Products

Stores product and pricing information.

Important fields:

ProductID

ProductName

Category

Price

Orders

Stores order-level information.

Important fields:

OrderID

CustomerID

OrderDate

Status

TotalAmount

Supported statuses in the generated dataset include:

Completed

Failed

Pending

OrderDetails

Stores individual product line items for each order.

Important fields:

OrderDetailID

OrderID

ProductID

Quantity

UnitPrice

The complete database definition is provided in schema.sql.

Business Queries

1. Daily Sales

File:

01_daily_sales.sql

Calculates:

Total sales

Number of orders

The query looks at the previous day and only includes completed orders.

2. Top-Selling Products

File:

02_top-selling_product.sql

Returns the top five products based on units sold and includes:

Product name

Total units sold

Total revenue

Only completed orders are included.

3. Sales by City

File:

03_sales_by_city.sql

Returns the top ten cities based on completed-order sales.

Metrics include:

City

Total sales

Order count

4. Failed Transactions

File:

04_failed_transactions.sql

Reports failed transactions from the most recent seven-day period.

Metrics include:

Failed order count

Failed order value

5. Top Customer Segment

File:

05_top_segment.sql

Aggregates completed orders by customer segment.

Metrics include:

Segment

Total revenue

Order count

Average order value

Query Runner

runner.py is responsible for executing the reporting pipeline.

Its workflow is:

Start
  │
  ▼
Connect to SQL Server
  │
  ▼
Load query definitions
  │
  ▼
For each business query
  │
  ├── Execute SQL
  │      │
  │      ├── Success → Save CSV
  │      │
  │      └── Failure → Save failure JSON
  │
  ▼
Print run summary
  │
  ▼
End

The runner maps friendly query names to SQL files:

QUERIES = {
    "daily_sales": "01_daily_sales.sql",
    "top_products": "02_top-selling_product.sql",
    "sales_by_city": "03_sales_by_city.sql",
    "failed_transactions": "04_failed_transactions.sql",
    "top_segment": "05_top_segment.sql",
}

Successful results are written to:

reports/

with timestamped filenames such as:

reports/daily_sales_2026-08-13_080000.csv

Failure Handling

The runner catches exceptions independently for each query.

This is important because a failure in one report should not prevent the remaining reports from being attempted.

For example:

daily_sales          → SUCCESS
top_products         → SUCCESS
sales_by_city        → FAILED
failed_transactions  → SUCCESS
top_segment          → SUCCESS

The runner can still produce the successful reports while recording the failed query.

A failure record is saved under:

logs/

and contains information similar to:

{
  "query_name": "sales_by_city",
  "timestamp": "...",
  "error_message": "...",
  "error_type": "...",
  "sql_text": "...",
  "traceback": "..."
}

This structured format gives the AI diagnostic layer machine-readable failure context.

AI Diagnostic Agent

diagnose_agent.py is the AI component of SelfHealSQL.

It searches the logs/ directory for failure files that do not yet have corresponding diagnosis files.

For each new failure:

Failure JSON
     │
     ▼
Extract:
- Query name
- Error type
- Error message
- SQL text
     │
     ▼
Construct diagnostic prompt
     │
     ▼
Gemini API
     │
     ▼
Parse JSON response
     │
     ▼
Save diagnosis

The agent uses the google-genai SDK and reads the API key from an environment variable.

The prompt asks the model to act as a SQL Server data diagnostics assistant and return only valid JSON.

Expected output:

{
  "likely_cause": "short explanation",
  "affected_area": "table/column/data pattern",
  "confidence": "high",
  "suggested_fix": "concrete next debugging step"
}

The agent then adds:

{
  "query_name": "...",
  "diagnosed_at": "...",
  "original_error": "..."
}

to the saved diagnosis.

Example Diagnosis

A failure can be transformed from a raw database error into something easier for a developer to act on:

{
  "likely_cause": "A non-numeric value was introduced into a field expected to contain numeric data.",
  "affected_area": "Orders.TotalAmount",
  "confidence": "high",
  "suggested_fix": "Inspect recent rows and validate the data type and values stored in TotalAmount."
}

The exact diagnosis depends on the error context provided to the model.

Defensive AI Response Handling

The diagnostic agent expects JSON from the model.

Because generative models can occasionally return markdown fences or malformed output, the implementation includes defensive handling:

Strip markdown fences when necessary.

Attempt to parse the response with json.loads().

If parsing fails, save a fallback diagnosis.

Preserve the raw model response for manual inspection.

This is a useful production-oriented pattern because downstream automation should not assume that an LLM will always produce perfectly formatted output.

Synthetic Data Generation

seed_data.py creates realistic test data using Faker.

The default dataset contains:

300 Customers
40 Products
3000 Orders

Products are distributed across categories such as:

Electronics
Home & Kitchen
Clothing
Books
Sports
Toys

Customers are assigned to:

Regular
Premium
VIP

Orders use weighted statuses:

Completed ≈ 90%
Failed    ≈ 7%
Pending   ≈ 3%

Orders are generated across approximately the previous 90 days.

This gives the project enough data to make the reporting queries meaningful while keeping the environment lightweight enough for local development.

Project Structure

Recommended repository structure:

SelfHealSQL/
│
├── 01_daily_sales.sql
├── 02_top-selling_product.sql
├── 03_sales_by_city.sql
├── 04_failed_transactions.sql
├── 05_top_segment.sql
│
├── schema.sql
├── seed_data.py
├── runner.py
├── diagnose_agent.py
├── requirements.txt
├── .env
├── .gitignore
│
├── reports/
│   └── *.csv
│
├── logs/
│   └── failure_*.json
│
└── diagnoses/
    └── diagnosis_*.json

Generated directories such as reports/, logs/, and diagnoses/ can be created automatically by the Python scripts.

Prerequisites

Before running the project, install:

Python

Microsoft SQL Server / SQL Server Express

SQL Server Management Studio (SSMS)

ODBC Driver 17 for SQL Server

A Google Gemini API key

Windows Task Scheduler if scheduled execution is desired

Installation

1. Clone the repository

git clone <your-repository-url>
cd SelfHealSQL

2. Create a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

Dependencies:

faker
pyodbc
python-dotenv
google-genai

Database Setup

Open SQL Server Management Studio and create/select the SelfHealSQL_DB database.

Then execute:

schema.sql

The schema creates:

Customers
Products
Orders
OrderDetails

with primary-key and foreign-key relationships.

Seed the Database

After creating the schema:

python seed_data.py

The script connects to:

localhost\SQLEXPRESS

using Windows Authentication by default.

If your SQL Server instance is different, update the connection configuration in the Python scripts.

Configure the Gemini API

Create a .env file in the project root:

GEMINI_API_KEY=your-api-key-here

Do not commit this file.

Add it to .gitignore:

.env
venv/
__pycache__/
reports/
logs/
diagnoses/

The diagnostic agent loads the API key using python-dotenv.

Run the Reporting Pipeline

Execute:

python runner.py

The runner connects to SQL Server and executes all five reporting queries.

A successful run creates timestamped CSV files in:

reports/

Example:

reports/
├── daily_sales_2026-08-13_080000.csv
├── top_products_2026-08-13_080000.csv
├── sales_by_city_2026-08-13_080000.csv
├── failed_transactions_2026-08-13_080000.csv
└── top_segment_2026-08-13_080000.csv

If a query fails, a JSON failure record is created in:

logs/

Run the AI Diagnosis

After failures have been logged:

python diagnose_agent.py

The agent finds undiagnosed failure files and generates corresponding JSON diagnoses.

Example:

logs/
└── failure_sales_by_city_2026-08-13_080000.json

diagnoses/
└── diagnosis_sales_by_city_2026-08-13_080000.json

If there are no new failures:

No new failures to diagnose. All caught up.

Windows Task Scheduler

The reporting portion of the project is intended to run automatically every morning using Windows Task Scheduler.

A typical setup is:

Windows Task Scheduler
        │
        ▼
Python runner.py
        │
        ▼
SQL Server
        │
        ├── Success → reports/*.csv
        │
        └── Failure → logs/*.json
                         │
                         ▼
                   diagnose_agent.py
                         │
                         ▼
                  diagnoses/*.json

For a fully automated deployment, configure the scheduled tasks so that the runner executes first and the diagnostic process runs afterward when applicable.

The exact Task Scheduler configuration depends on the local Python installation and project path.

Testing the Self-Diagnosis Workflow

The most important part of the project is not simply running successful SQL queries. It is testing how the pipeline behaves when the data environment becomes unreliable.

A practical test cycle is:

1. Start with valid data
        ↓
2. Run runner.py
        ↓
3. Confirm reports are generated
        ↓
4. Introduce a controlled data/schema problem
        ↓
5. Run runner.py again
        ↓
6. Confirm failure JSON is created
        ↓
7. Run diagnose_agent.py
        ↓
8. Inspect diagnosis JSON
        ↓
9. Compare diagnosis with the actual injected problem

Potential failure patterns include:

Invalid values in fields expected to be numeric

Malformed date values

Unexpected data types

Missing columns

Schema changes

Other SQL Server query failures

The purpose of these tests is to determine whether the agent can identify a meaningful root cause from the available failure context rather than simply echoing the original error.

Important Implementation Detail

The current implementation separates query execution and AI diagnosis into two Python programs:

runner.py
diagnose_agent.py

runner.py writes failure JSON files, while diagnose_agent.py reads those files and generates diagnoses.

This separation is useful because it keeps the database/reporting layer independent from the AI layer.

It also makes it possible to:

Retry diagnosis later

Re-run diagnosis without re-running SQL

Replace the AI provider

Test the SQL pipeline independently

Test the AI layer using stored failure fixtures

Error Isolation Philosophy

SelfHealSQL follows a simple principle:

A failed report should become diagnostic data, not just an exception.

Instead of treating:

SQL Error → Stop → Developer investigates

the project turns it into:

SQL Error
   ↓
Structured Failure
   ↓
AI Analysis
   ↓
Probable Cause
   ↓
Affected Area
   ↓
Recommended Next Step

This makes the pipeline easier to observe and debug.

Current Scope vs. Future Production Enhancements

SelfHealSQL is a local proof-of-concept designed to demonstrate the architecture and workflow.

For a production-grade implementation, the following improvements could be added.

Automatic Orchestration

Instead of scheduling the runner and diagnostic process separately, use a single orchestration entry point:

Scheduled Job
     ↓
Run Reports
     ↓
Detect Failures
     ↓
Run AI Diagnosis
     ↓
Generate Final Run Summary

Richer Failure Context

The current failure record primarily contains the query execution context:

Query name

Error

SQL

Traceback

A stronger diagnostic system could additionally collect:

Table name

Column name

Schema metadata

Recent rows

Column data types

Query execution metadata

Relevant constraints

Automatic Data Validation

Add pre-query data-quality checks such as:

NULL checks
Type validation
Date validation
Duplicate detection
Range checks
Referential integrity checks

Alerting

Add notifications through:

Email

Microsoft Teams

Slack

Other incident/alerting systems

Retry Strategy

Some failures may be transient. A production version could implement:

Query fails
   ↓
Retry
   ↓
Still fails?
   ├── No → Save report
   └── Yes → Diagnose + Alert

AI Safety Controls

The AI agent should remain diagnostic rather than directly modifying production data.

A production implementation should also consider:

API key security

Sensitive data filtering

Prompt-injection protection

Rate limits

Audit logs

Human approval for suggested changes

Strict JSON schema validation

Design Decisions

Why SQL Server?

SQL Server provides a realistic relational database environment for practicing:

Joins

Aggregations

Filtering

Grouping

Foreign-key relationships

Reporting queries

Database error handling

Why Python?

Python acts as the orchestration layer between:

SQL Server
     ↕
Business Queries
     ↕
File System
     ↕
AI API

It also provides convenient libraries for database connectivity, file processing, JSON handling, environment variables, and API integration.

Why Structured JSON?

JSON provides a consistent contract between the SQL failure pipeline and the AI diagnostic layer.

Instead of passing an unstructured log around, the system stores predictable fields such as:

query_name
error_type
error_message
sql_text
timestamp

The AI layer then produces a similarly structured diagnosis.

What This Project Demonstrates

SelfHealSQL demonstrates several practical engineering concepts in one project:

Data Engineering

SQL Server database design

Relational modeling

Foreign keys

Synthetic data generation

Business metric queries

Scheduled reporting

Python Automation

Database connectivity with pyodbc

SQL file execution

CSV generation

JSON logging

Exception handling

Environment configuration

Applied AI

Generative AI API integration

Prompt design

Structured output

JSON parsing

AI-assisted debugging

Confidence-based diagnosis

Reliability Engineering

Failure isolation

Structured logging

Diagnostic artifacts

Repeatable testing

Separation between execution and diagnosis

Limitations

The current project should be considered a local proof-of-concept, not a production-ready autonomous repair system.

In particular:

The AI recommends fixes; it does not automatically modify the database.

The current runner stores the SQL error, SQL text, and traceback; richer table/column/sample-data extraction can be added.

AI diagnosis is a separate step from the query runner.

The project uses a local SQL Server connection configuration.

No notification/alerting system is currently implemented.

Production deployment would require stronger secret management, validation, monitoring, and security controls.

These limitations are intentional opportunities for future development rather than requirements for the core demonstration.

Future Roadmap

Phase 1
✓ SQL Server database
✓ Synthetic data
✓ Business reporting queries
✓ Python query runner
✓ CSV reporting
✓ Structured failure logging
✓ AI diagnosis

Phase 2
□ Automatic runner → diagnosis orchestration
□ Rich schema/data context
□ Data-quality validation
□ Automatic retries
□ Email/Teams/Slack alerts

Phase 3
□ Dashboard for report health
□ Historical failure analytics
□ AI diagnosis evaluation metrics
□ Model/provider abstraction
□ Centralized logging
□ Dockerized deployment

Phase 4
□ Production orchestration
□ Cloud database support
□ CI/CD
□ Monitoring and observability
□ Human-approved remediation workflows

Example End-to-End Scenario

Imagine the sales_by_city report suddenly fails after a database change.

Instead of:

Pipeline Failed
SQL Exception
Developer starts debugging manually

SelfHealSQL follows:

sales_by_city.sql
       │
       ▼
SQL Server Error
       │
       ▼
runner.py catches exception
       │
       ▼
logs/failure_sales_by_city_....json
       │
       ▼
diagnose_agent.py
       │
       ▼
Gemini
       │
       ▼
{
  "likely_cause": "...",
  "affected_area": "...",
  "confidence": "...",
  "suggested_fix": "..."
}
       │
       ▼
diagnoses/diagnosis_sales_by_city_....json

The developer receives a structured starting point for investigation rather than having to interpret a raw stack trace alone.

Resume / Portfolio Summary

SelfHealSQL — AI-Assisted SQL Reporting & Failure Diagnosis

Built an automated SQL Server reporting pipeline that executes business-critical analytics queries, exports successful results to timestamped CSV reports, captures structured SQL failures, and uses a generative AI diagnostic agent to identify probable root causes and recommend debugging steps. Developed synthetic test data and failure scenarios to validate the diagnostic workflow.

Key Technologies

Python · SQL Server · T-SQL · pyodbc · Gemini API · Faker · JSON · CSV · Windows Task Scheduler

Author

Dev Gupta

Data / AI / Software Engineering Project
