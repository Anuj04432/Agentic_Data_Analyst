# 📋 Master Project Plan: Agentic Data Analyst

This document is the definitive master roadmap and folder architecture reference for the **Agentic Data Analyst** project. All subsequent development steps must strictly follow the folder structure, module responsibilities, and phased execution plan defined below.

---

## 1. Complete Folder & File Architecture

```
Agentic_Data_Analyst/
│
├── app.py                          # Main Streamlit application entry point & router
├── plan.md                         # Master implementation roadmap (THIS FILE)
├── README.md                       # High-level project documentation
├── pyproject.toml / requirements.txt # Project dependencies
├── .env                            # API keys (GEMINI_API_KEY / OPENAI_API_KEY)
│
├── .streamlit/
│   └── config.toml                 # Streamlit UI theme and server configuration
│
├── assets/
│   ├── images/                     # UI icons and banner graphics
│   └── logo/                       # Application logo assets
│
├── data/
│   ├── sample/                     # Built-in demo datasets (CSV, Excel, SQLite)
│   ├── uploaded/                   # Stored user uploads
│   └── processed/                  # Exported / transformed datasets
│
├── utils/                          # Cross-cutting foundational helpers
│   ├── __init__.py
│   ├── file_handler.py             # File ingestion (CSV, Excel, JSON, Feather, SQLite)
│   ├── helpers.py                  # Formatting, text truncation, column name cleaning
│   ├── history.py                  # Upload history and sample dataset discovery
│   └── session_state.py            # Centralized Streamlit session state management
│
├── analysis/                       # Pure statistical & analytical engines (UI-independent)
│   ├── __init__.py
│   ├── profiling.py                # Overall dataset health score & high-level audit
│   ├── statistics.py               # Descriptive stats, skewness, kurtosis, quantiles
│   ├── missing_values.py           # Missing value analysis, heatmaps, and imputation
│   ├── duplicates.py               # Duplicate detection, inspection, and removal
│   ├── correlations.py             # Correlation matrices (Pearson, Spearman) & top pairs
│   └── outliers.py                 # Outlier detection (IQR, Z-score) & summary
│
├── visualization/                  # Chart generation & rendering logic
│   ├── __init__.py
│   ├── charts.py                   # Plotly & Matplotlib chart builders (Bar, Line, Scatter, Box, Heatmap)
│   ├── chart_recommender.py        # Rule-based chart recommendations based on column types
│   └── chart_config.py             # Reusable color palettes, themes, and layout presets
│
├── agent/                          # Autonomous AI Analyst core (LLM & code execution)
│   ├── __init__.py
│   ├── prompts.py                  # System prompts, few-shot examples, schema context builders
│   ├── tools.py                    # Safe code execution sandbox (executes pandas/matplotlib safely)
│   ├── planner.py                  # Intent parsing, query classification, step-by-step reasoning
│   └── agent.py                    # Main agent orchestration loop (LLM call -> code exec -> synthesis)
│
├── components/                     # Modular, reusable Streamlit UI components
│   ├── __init__.py
│   ├── sidebar.py                  # Shared sidebar (dataset picker, history, metadata badge)
│   ├── dataset_summary.py          # Metric cards (Rows, Columns, Missing %, Duplicates, Memory)
│   ├── data_preview.py             # Interactive data table with search, sorting, and pagination
│   ├── column_selector.py          # Smart column dropdowns (grouped by numeric/categorical/date)
│   ├── analysis_result.py          # Reusable display cards for statistical findings & alerts
│   ├── chart_selector.py           # Interactive visual chart configuration panel
│   └── chat_interface.py          # Streamlit chat interface (chat history, code expander, figure renderer)
│
└── ui/                             # Application views / tabs (imported into app.py)
    ├── __init__.py
    ├── Data_Analysis.py            # Tab 1: Comprehensive Exploratory Data Analysis (EDA)
    ├── Data_Visualization.py       # Tab 2: Interactive Visual Exploration & Plot Builder
    ├── Ask_your_data.py            # Tab 3: Autonomous AI Data Analyst Chatbot
    └── Predictive_Modeling.py      # Tab 4: Auto-ML Baseline Classification & Regression
```

---

## 2. Detailed Folder Responsibilities

| Folder | Responsibility | What Goes In Here | What Must NOT Go Here |
|---|---|---|---|
| `utils/` | Low-level utility functions | Streamlit session state wrappers, file format parsers, number/byte formatters, string sanitizers. | No Streamlit rendering/UI code (except `session_state.py`). No heavy ML models. |
| `analysis/` | Pure business logic & statistics | Functions that take `pd.DataFrame` and return raw stats, dictionaries, or dataframes (e.g. outlier masks, correlation pairs). | No `st.write` or UI code. Keep functions pure and unit-testable. |
| `visualization/` | Chart generation engine | Functions that generate Plotly / Matplotlib / Seaborn figures from data. Recommender heuristics. | No direct dataset loading or file parsing. |
| `components/` | Reusable Streamlit UI widgets | Renderable Streamlit blocks (KPI cards, column selectors, chat containers, preview tables). | No standalone scripts. These are imported by `app.py` and `pages/`. |
| `agent/` | LLM reasoning & agentic execution | LLM API connectors (Gemini / OpenAI), context builders, prompt templates, sandboxed Python code runner. | No frontend layout code. |
| `pages/` | Complete page views | High-level page workflows assembling components and analytical engines into cohesive user journeys. | Don't put raw computation algorithms directly in pages; delegate to `analysis/` and `visualization/`. |
| `data/` | Data storage | Sample datasets, user uploads, exported processed data. | No Python source code. |

---

## 3. Step-by-Step Implementation Roadmap

### Phase 1: Core Foundation & Bug Fixes (Immediate)
- [ ] **Step 1.1: Fix `utils/helpers.py`**:
  - Fix return type of `get_column_summary` when DataFrame is empty (return empty DataFrame, not string).
  - Align key names in `get_column_types` (`datetime` vs `date_cols`, include `all`).
  - Add missing helpers: `detect_outliers_iqr`, `get_top_correlations`, `format_context_for_llm`, `infer_problem_type`.
- [ ] **Step 1.2: Standardize `app.py` & Session State**:
  - Connect `utils/session_state.py` into `app.py` so uploaded/selected dataset persists across pages and reruns.
  - Fix dataset loading logic for both uploaded files and history files.
  - Fix radio button indentation and navigation bug.
- [ ] **Step 1.3: Clean Up Data Directories**:
  - Move sample datasets from `utils/saved_history/` into `data/sample/` and `data/uploaded/`.
  - Update `utils/history.py` to correctly scan and resolve paths.

---

### Phase 2: Statistical & Analytical Engine (`analysis/`)
- [ ] **Step 2.1: `analysis/statistics.py`**:
  - Full descriptive statistics: mean, std, quantiles, skewness, kurtosis, variance.
- [ ] **Step 2.2: `analysis/missing_values.py`**:
  - Missing value counts, percentages, missingness matrix / pattern detection, imputation methods.
- [ ] **Step 2.3: `analysis/duplicates.py`**:
  - Duplicate row detection, filtering, and dropping.
- [ ] **Step 2.4: `analysis/correlations.py`**:
  - Pearson & Spearman correlation matrices, top positively and negatively correlated pairs.
- [ ] **Step 2.5: `analysis/outliers.py`**:
  - IQR-based and Z-score outlier detection per numeric column.
- [ ] **Step 2.6: `analysis/profiling.py`**:
  - Composite health score and automated data audit summary.

---

### Phase 3: Modular UI Components (`components/`)
- [ ] **Step 3.1: `components/dataset_summary.py`**:
  - KPI metric cards: Total Rows, Columns, Missing (%), Duplicates, Memory Usage.
- [ ] **Step 3.2: `components/data_preview.py`**:
  - Paginated / head preview with column search and filter.
- [ ] **Step 3.3: `components/column_selector.py`**:
  - Dropdown widgets filtering columns by dtype (numeric only, categorical only, datetime only).
- [ ] **Step 3.4: `components/analysis_result.py`**:
  - Styled cards displaying warnings, skewness alerts, and outlier badges.

---

### Phase 4: Exploratory Data Analysis View (`pages/1_Data_Analysis.py`)
- [ ] **Step 4.1**: Build the complete EDA dashboard:
  - Metric summary cards at the top.
  - Interactive Data Preview.
  - Column Data Dictionary & Type breakdown.
  - Detailed Missing Values & Duplicates tab.
  - Statistical distributions & Outlier inspection tab.
  - Correlation matrix & Key relationships tab.

---

### Phase 5: Visualization Engine & Page (`visualization/` & `pages/2_Data_Visualization.py`)
- [ ] **Step 5.1: `visualization/charts.py`**:
  - Implement Plotly / Matplotlib chart functions: Histogram, Box Plot, Scatter Plot, Bar Chart, Line Chart, Correlation Heatmap.
- [ ] **Step 5.2: `visualization/chart_recommender.py`**:
  - Smart heuristic engine that auto-suggests the best chart based on user-selected columns.
- [ ] **Step 5.3: `pages/2_Data_Visualization.py`**:
  - Full interactive chart builder connected to current session dataset.

---

### Phase 6: Autonomous AI Analyst (`agent/` & `pages/3_Ask_Your_Data.py`)
- [ ] **Step 6.1: `agent/prompts.py`**:
  - System prompt instructing the LLM to act as an expert data analyst.
  - Schema & context injection formatter.
- [ ] **Step 6.2: `agent/tools.py`**:
  - Sandboxed Python execution environment that executes pandas code against `df`, capturing stdout, tabular outputs, and generated figures.
- [ ] **Step 6.3: `agent/agent.py`**:
  - LLM integration with Google Gemini (`google-genai`) / OpenAI.
  - Code generation, execution, self-correction on error, and final insight synthesis.
- [ ] **Step 6.4: `pages/3_Ask_Your_Data.py`**:
  - Chat interface (`st.chat_message`, `st.chat_input`) showing conversation history, executed code in expander, and resulting tables/plots.

---

### Phase 7: Predictive Auto-ML (`pages/4_Predictive_Modeling.py`)
- [ ] **Step 7.1**: Automatic target detection & problem type inference (Classification vs Regression).
- [ ] **Step 7.2**: Automated preprocessing pipeline (imputation, one-hot encoding, 80/20 train-test split).
- [ ] **Step 7.3**: Model training (`RandomForest`, `HistGradientBoosting`).
- [ ] **Step 7.4**: Evaluation metrics (Accuracy, F1, Confusion Matrix for Classification; $R^2$, MAE, RMSE for Regression) & Feature Importance chart.

---

## 4. Immediate Next Steps
1. Apply fixes to `utils/helpers.py`.
2. Connect `utils/session_state.py` into `app.py`.
3. Implement `analysis/` modules (`statistics.py`, `missing_values.py`, `outliers.py`, `correlations.py`).
