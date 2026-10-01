# 🤖 Agentic Data Analyst

An intelligent, autonomous data analysis assistant built with **Streamlit**, **Pandas**, **Scikit-Learn**, and **LLMs**.

This application bridges the gap between raw business datasets and actionable decisions by combining traditional Exploratory Data Analysis (EDA) with an autonomous AI agent capable of answering natural language questions, generating charts on the fly, uncovering hidden anomalies, and building predictive models.

---

## 📌 Table of Contents
- [1. System Architecture](#1-system-architecture)
- [2. Completed Modules & Capabilities](#2-completed-modules--capabilities)
- [3. Project Folder Architecture](#3-project-folder-architecture)
- [4. Master Implementation Roadmap](#4-master-implementation-roadmap)
- [5. How to Run & Test](#5-how-to-run--test)

---

## 1. System Architecture

```mermaid
flowchart TD
    User([User]) -->|Uploads CSV / Excel / SQLite / JSON / Feather| Ingestion[1. Ingestion Engine\nutils/file_handler.py]
    Ingestion --> History[History & Session State\nutils/history.py | utils/session_state.py]
    
    History --> AnalysisEngine[2. Pure Statistical & Analysis Engines\nanalysis/]
    
    subgraph AnalysisModule [Analysis Engines analysis/]
        AnalysisEngine --> Stats[statistics.py\nDescriptive Stats, Skewness, Kurtosis]
        AnalysisEngine --> Miss[missing_values.py\nOverview, Patterns, Imputation]
        AnalysisEngine --> Dups[duplicates.py\nDetection & Removal]
        AnalysisEngine --> Corr[correlations.py\nPearson, Spearman, Top Pairs]
        AnalysisEngine --> Outliers[outliers.py\nIQR, Z-Score, Capping, Dropping]
        AnalysisEngine --> Profiling[profiling.py\nHealth Score 0-100, Grade A-F, Audit & Alerts]
    end
    
    Profiling --> UI[3. UI Views & Tabs\nui/]
    UI --> Tab1[Tab 1: Comprehensive EDA\nui/Data_Analysis.py]
    UI --> Tab2[Tab 2: Visual Exploration\nui/Data_Visualization.py]
    UI --> Tab3[Tab 3: Autonomous AI Analyst\nui/Ask_your_data.py]
    UI --> Tab4[Tab 4: Predictive Auto-ML\nui/Predictive_Modeling.py]
    
    subgraph AgenticCore [Autonomous AI Analyst agent/]
        Tab3 -->|Natural Language Query| PromptEngine[agent/prompts.py]
        PromptEngine --> LLM[Gemini / OpenAI Connector\nagent/agent.py]
        LLM -->|Executable Code| Sandbox[Safe Code Executor\nagent/tools.py]
        Sandbox -->|Tables & Charts| Synthesis[Insight Generation]
    end
    
    Synthesis --> User
```

---

## 2. Completed Modules & Capabilities

### 🔬 Pure Statistical & Analytical Engine (`analysis/`)
All analysis modules are pure functions (taking `pd.DataFrame` or `pd.Series` and returning structured dicts, DataFrames, or tuples) keeping backend logic cleanly decoupled from UI code:

1. **`analysis/profiling.py` (Dataset Health & Diagnostic Audit)**:
   - `calculate_health_score(df)`: Computes an objective data hygiene score (`0 - 100`) and letter grade (`A` through `F`) with bounded deduction penalties for missingness (up to -30), duplicates (up to -20), severe outliers (up to -20), and zero-variance constant columns (up to -15).
   - `generate_dataset_audit(df)`: Master diagnostic audit aggregating shape, memory footprint, column type distribution, duplicate counts, outlier counts, health scores, and actionable human-readable warning alerts.
2. **`analysis/outliers.py` (Anomaly Detection & Cleaning)**:
   - `detect_outliers_iqr(series, factor=1.5)`: Tukey's IQR rule with lower/upper fences, indices, and flags.
   - `detect_outliers_zscore(series, threshold=3.0)`: Standard deviation / Z-Score anomaly detector with zero-variance protection.
   - `get_outliers_summary(df, method='iqr')`: Tabular summary across all numeric columns sorted descending by outlier count.
   - `cap_outliers(df, column, factor=1.5)`: Non-destructive Winsorization clamping.
   - `drop_outliers(df, columns=None, factor=1.5)`: Deduplicated outlier row removal.
3. **`analysis/correlations.py` (Multivariate Relationships)**:
   - `calculate_correlation_matrix(df, method)`: Safe numeric correlation supporting Pearson, Spearman, and Kendall.
   - `get_top_correlations(df, threshold, top_n)`: Unpacks upper-triangle pairs, measures direction and strength (Very Strong, Strong, Moderate, Weak), and ranks by absolute correlation.
   - `get_target_correlations(df, target_column)`: Feature-to-target correlation ranking.
   - `get_correlation_overview(df)`: Multicollinearity warnings and high-level correlation metrics.
4. **`analysis/missing_values.py` (Missingness Diagnostics & Imputation)**:
   - `get_missing_summary(df)`: Column-level breakdown sorted by missing percentage.
   - `get_missingness_overview(df)`: KPI metrics (total missing cells, global missing %, affected columns).
   - `impute_missing_values(df, strategy)`: Supports `mean`, `median`, `mode`, `drop_rows`, `drop_cols`, and custom mappings.
5. **`analysis/duplicates.py` (Duplicate Detection & Removal)**:
   - `get_duplicate_summary(df, subset)`: Detects redundant rows, calculating counts and percentages.
   - `drop_duplicates_clean(df, subset, keep)`: Safe deduplication on DataFrame copies with index resetting.
6. **`analysis/statistics.py` (Descriptive & Distributional Stats)**:
   - `get_numeric_summary(df)`: Comprehensive metrics including mean, std, quantiles, IQR, skewness, and kurtosis.
   - `get_categorical_summary(df)`: Unique counts, mode values, mode frequency percentages, and missing counts.
   - `get_distribution_stats(series)`: Skewness/kurtosis heuristics and human-readable distribution shape classification.

### 🛠️ Foundational Utilities (`utils/`)
- **`utils/file_handler.py`**: Ingestion support for `.csv`, `.xlsx`, `.xls`, `.json`, `.feather`, and `.sqlite`/`.db`.
- **`utils/history.py`**: Discovers sample datasets (`data/sample/`) and persists recently uploaded files.
- **`utils/helpers.py`**: Safe formatters (`format_bytes`, `format_number`, `format_percentage`) and column dtype classifier (`get_column_types`).
- **`utils/session_state.py`**: Centralized Streamlit session state management for persistent dataset access across tabs.

---

## 3. Project Folder Architecture

```
Agentic_Data_Analyst/
│
├── app.py                          # Main Streamlit application entry point & router
├── test.py                         # Interactive Streamlit UI preview for health score & audits
├── plan.md                         # Master implementation roadmap
├── README.md                       # Comprehensive documentation & progress tracker
├── pyproject.toml / requirements.txt # Dependencies
├── .env                            # API keys (GEMINI_API_KEY / OPENAI_API_KEY)
│
├── .streamlit/
│   └── config.toml                 # Custom Indigo UI theme and server configuration
│
├── data/
│   ├── sample/                     # Built-in demo datasets (CSV, Excel, SQLite)
│   ├── uploaded/                   # Stored user uploads
│   └── processed/                  # Exported / transformed datasets
│
├── utils/                          # Cross-cutting foundational helpers
│   ├── __init__.py
│   ├── file_handler.py             # Multi-format ingestion (CSV, Excel, JSON, SQLite)
│   ├── helpers.py                  # Formatting & column classification
│   ├── history.py                  # Upload history and sample dataset discovery
│   └── session_state.py            # Centralized Streamlit session state management
│
├── analysis/                       # Pure statistical & analytical engines (UI-independent)
│   ├── __init__.py                 # Exported public API
│   ├── profiling.py                # Dataset health score (0-100, A-F) & master diagnostic audit
│   ├── statistics.py               # Descriptive stats, skewness, kurtosis, quantiles
│   ├── missing_values.py           # Missing value analysis & imputation
│   ├── duplicates.py               # Duplicate detection & deduplication
│   ├── correlations.py             # Correlation matrices & top pairs
│   └── outliers.py                 # Outlier detection (IQR, Z-score) & cleaning
│
├── tests/                          # Automated unit test suites
│   ├── __init__.py
│   └── test_profiling.py           # Unit tests for health score, deductions, & audits
│
├── visualization/                  # Chart generation & rendering logic
│   ├── __init__.py
│   ├── charts.py                   # Plotly & Matplotlib chart builders
│   ├── chart_recommender.py        # Rule-based chart recommendations
│   └── chart_config.py             # Color palettes & layout presets
│
├── agent/                          # Autonomous AI Analyst core (LLM & code execution)
│   ├── __init__.py
│   ├── prompts.py                  # Schema context builders & prompt templates
│   ├── tools.py                    # Safe code execution sandbox
│   ├── planner.py                  # Intent parsing & query classification
│   └── agent.py                    # LLM orchestration loop
│
├── components/                     # Modular, reusable Streamlit UI components
│   ├── __init__.py
│   ├── dataset_summary.py          # Metric cards (Rows, Columns, Missing, Duplicates)
│   ├── data_preview.py             # Interactive table preview with search & sorting
│   ├── column_selector.py          # Smart column dropdowns grouped by dtype
│   ├── analysis_result.py          # Styled cards for statistical findings & alerts
│   ├── chart_selector.py           # Visual chart configuration panel
│   └── chat_interface.py          # Streamlit chat interface with code expander
│
└── ui/                             # Application views / tabs (imported into app.py)
    ├── __init__.py
    ├── Data_Analysis.py            # Tab 1: Comprehensive Exploratory Data Analysis (EDA)
    ├── Data_Visualization.py       # Tab 2: Interactive Visual Exploration & Plot Builder
    ├── Ask_your_data.py            # Tab 3: Autonomous AI Data Analyst Chatbot
    └── Predictive_Modeling.py      # Tab 4: Auto-ML Baseline Classification & Regression
```

---

## 4. Master Implementation Roadmap

### Phase 1: Core Foundation & Bug Fixes
- [x] Consolidate sample datasets into `data/sample/`.
- [x] Support multiple ingestion formats (CSV, Excel, JSON, SQLite) in `utils/file_handler.py`.
- [x] Centralize session state management in `utils/session_state.py`.
- [x] Standardize helper functions in `utils/helpers.py`.

### Phase 2: Pure Analytical & Statistical Engines (`analysis/`)
- [x] **Step 2.1 (`analysis/statistics.py`)**: Descriptive statistics, skewness, kurtosis, and distribution shapes.
- [x] **Step 2.2 (`analysis/missing_values.py`)**: Missingness breakdown, overview KPIs, and imputation.
- [x] **Step 2.3 (`analysis/duplicates.py`)**: Duplicate row inspection and safe removal.
- [x] **Step 2.4 (`analysis/correlations.py`)**: Pearson, Spearman, Kendall matrices, and top correlation pairs.
- [x] **Step 2.5 (`analysis/outliers.py`)**: IQR and Z-Score outlier detection, tabular summaries, Winsorization capping, and outlier dropping.
- [x] **Step 2.6 (`analysis/profiling.py`)**: Health score algorithm (`0 - 100`, grades `A`–`F`), deduction rules, and master dataset diagnostic audit.
- [x] **Step 2.7 (Export & Tests)**: Exported API in `analysis/__init__.py` and comprehensive unit tests in `tests/test_profiling.py`.

### Phase 3: Modular UI Components (`components/`)
- [ ] **Step 3.1 (`components/dataset_summary.py`)**: Metric summary cards (Rows, Columns, Missing %, Duplicates, Memory).
- [ ] **Step 3.2 (`components/data_preview.py`)**: Searchable and paginated data table.
- [ ] **Step 3.3 (`components/column_selector.py`)**: Type-filtered dropdown selector.
- [ ] **Step 3.4 (`components/analysis_result.py`)**: Badges, grade cards, and diagnostic alerts.

### Phase 4: Exploratory Data Analysis View (`ui/Data_Analysis.py`)
- [ ] Master health grade card & executive audit summary.
- [ ] Interactive missingness matrix & imputation controls.
- [ ] Outlier inspection sliders, capping, and row dropping actions.
- [ ] Correlation heatmaps and top collinearity inspector.

### Phase 5: Visualization Engine (`visualization/` & `ui/Data_Visualization.py`)
- [ ] Plotly & Matplotlib chart generators (Histogram, Box Plot, Scatter, Bar, Line).
- [ ] Smart rule-based chart recommender heuristics based on column dtypes.
- [ ] Interactive visual chart builder with color and layout presets.

### Phase 6: Autonomous AI Analyst (`agent/` & `ui/Ask_your_data.py`)
- [ ] LLM integration (Google Gemini / OpenAI).
- [ ] Safe Python code execution sandbox for pandas & matplotlib.
- [ ] Conversational chat interface with reasoning, expandable code blocks, and chart rendering.

### Phase 7: Predictive Auto-ML (`ui/Predictive_Modeling.py`)
- [ ] Problem type inference (Classification vs. Regression).
- [ ] Automated preprocessing pipeline (imputation, encoding, 80/20 split).
- [ ] Baseline model training (`RandomForest`, `HistGradientBoosting`).
- [ ] Metrics evaluation & feature importance plot.

---

## 5. How to Run & Test

### 1. Prerequisites & Environment Setup
- Python 3.12+
- Using `uv` (recommended) or `pip`:

```powershell
# Create and activate virtual environment
uv venv
.venv\Scripts\activate

# Install project dependencies
uv pip install -e .
```

### 2. Run the Unit Test Suite
Execute the test suite covering data health scoring, capping rules, grade mappings, and diagnostic audits:

```powershell
python -m unittest tests/test_profiling.py -v
```

### 3. Run the Health Score & Profiling UI Preview
Preview the interactive health score card, deduction breakdown, and live editable table:

```powershell
streamlit run test.py
```

### 4. Run the Main Application
```powershell
streamlit run app.py
```
