# 🤖 MyAnalyst: Autonomous Data Analysis & Exploration Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Data-Pandas%20%7C%20NumPy-150458?logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/Visualization-Plotly%20%7C%20Seaborn-3F4F75?logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Tests-111%20Passed-success?logo=pytest&logoColor=white" alt="Pytest" />
  <img src="https://img.shields.io/badge/Architecture-Modular%20%26%20Decoupled-purple" alt="Architecture" />
</p>

<p align="center">
  <b>Transform raw, messy datasets into actionable intelligence with automated diagnostics, interactive visual analytics, and conversational AI agents.</b>
</p>

---

## 🌟 Executive Overview

**MyAnalyst** is an enterprise-grade, modular data intelligence workbench. Built with strict separation of concerns, it unites:
- **Pure Analytical Engines** (100% deterministic, UI-independent statistics & profiling),
- **Reusable Streamlit UI Components** (type-aware inputs, health score hero cards, interactive charts, and multi-modal chat), and
- **Autonomous AI Agents** (natural language reasoning, code synthesis, and automated execution).

---

## 🚀 Key Feature Pillars

| 🩺 Dataset Health & Audit | 🧹 Data Cleansing & Imputation | 📊 Dynamic Chart Studio | 💬 Conversational AI Analyst |
| :--- | :--- | :--- | :--- |
| Composite quality score (`0-100`) and letter grade (`A`–`F`) with bounded deductions for nulls, duplicates, and outliers. | Interactive imputation (Mean, Median, Mode, Drops) and non-destructive Winsorization outlier capping. | Context-aware chart recommendation with dynamic axis bindings across 7 visualization types. | Chat interface featuring thought traces, syntax-highlighted code expanders, and figure rendering. |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Ingestion Layer
        Raw["Multi-Format Data (CSV, Excel, JSON, SQLite)"]
        Sidebar["components/sidebar.py"]
        State["Centralized Session State (utils/session_state.py)"]
        Raw --> Sidebar --> State
    end

    subgraph Analytical Core ["analysis/ (Pure & Tested)"]
        Prof["profiling.py (Health Score & Audit)"]
        Stats["statistics.py (Descriptive Stats)"]
        Miss["missing_values.py (Imputation)"]
        Dups["duplicates.py (Deduplication)"]
        Outs["outliers.py (IQR & Z-score)"]
        Corrs["correlations.py (Matrices & Collinearity)"]
    end

    subgraph Modular UI Library ["components/ (Streamlit Widgets)"]
        DS["dataset_summary.py (KPI Cards)"]
        DP["data_preview.py (Searchable Table)"]
        CS["column_selector.py (Smart Dropdowns)"]
        AR["analysis_result.py (Badges & Cards)"]
        CSelect["chart_selector.py (Plot Configurator)"]
        Chat["chat_interface.py (AI Chat Stream)"]
    end

    subgraph Application Views ["ui/ & app.py"]
        EDA["Tab 1: Exploratory Data Analysis (ui/Data_Analysis.py)"]
        Viz["Tab 2: Visual Analytics (ui/Data_Visualization.py)"]
        AI["Tab 3: Ask Your Data (ui/Ask_your_data.py)"]
        ML["Tab 4: Predictive Modeling (ui/Predictive_Modeling.py)"]
    end

    State --> Analytical Core
    Analytical Core --> Modular UI Library
    Modular UI Library --> Application Views
```

---

## 📦 Complete Modular UI Library (`components/`)

All 7 UI components are modular, isolated, and unit-tested:

| Component | Module | Responsibility & Capabilities |
| :--- | :--- | :--- |
| **Ingestion Sidebar** | [`components/sidebar.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/sidebar.py) | Multi-source ingestion (Upload, Samples, History), format detection, active dataset badge, and safe reset. |
| **KPI Metric Cards** | [`components/dataset_summary.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/dataset_summary.py) | 5-column metric dashboard: Rows, Columns, Missing (%), Duplicate count, and Memory footprint. |
| **Data Preview** | [`components/data_preview.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/data_preview.py) | Paginated DataFrame preview with live row search, column visibility toggle, and CSV download. |
| **Smart Column Selector** | [`components/column_selector.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/column_selector.py) | Analytical type classification (Numeric, Categorical, Datetime, Boolean) with single- and multi-select dropdowns. |
| **Analysis Cards & Badges** | [`components/analysis_result.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/analysis_result.py) | Health Grade hero card (A-F), deduction breakdown, distribution badges, and diagnostic alerts. |
| **Chart Configurator** | [`components/chart_selector.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/chart_selector.py) | Dynamic visualization configurator with type-filtered axes, binning sliders, and standardized validation contracts. |
| **Chat Interface** | [`components/chat_interface.py`](file:///C:/Users/Anuj%20Kumar/Desktop/Agentic_Data_Analyst/components/chat_interface.py) | Multi-modal conversational interface with collapsible thoughts, syntax-highlighted code blocks, tables, and figures. |

---

## 🔬 Pure Analytical Engines (`analysis/`)

All computation logic lives in pure, stateless functions decoupled from Streamlit:

- **`analysis/profiling.py`**:
  - `calculate_health_score(df)`: Evaluates missingness, duplication, outliers, and constant columns to assign a composite score (`0-100`) and letter grade (`A`-`F`).
  - `generate_dataset_audit(df)`: Master diagnostic audit aggregating shape, memory, distribution, and actionable text warnings.
- **`analysis/outliers.py`**:
  - `detect_outliers_iqr()` & `detect_outliers_zscore()`: Robust anomaly detectors with zero-variance protection.
  - `cap_outliers()` & `drop_outliers()`: Safe Winsorization clamping and outlier filtering.
- **`analysis/correlations.py`**:
  - `calculate_correlation_matrix()`: Pearson, Spearman, and Kendall correlation matrices.
  - `get_top_correlations()`: Extracts unique pairs with direction and strength ratings.
  - `get_correlation_overview()`: Multicollinearity alerts ($|r| > 0.85$).
- **`analysis/missing_values.py`**:
  - `get_missing_summary()` & `get_missingness_overview()`: Column and overall missingness metrics.
  - `impute_missing_values()`: Mean, median, mode, and dropping strategies.
- **`analysis/duplicates.py`**:
  - `get_duplicate_summary()` & `drop_duplicates_clean()`: Duplicate detection and safe deduplication.
- **`analysis/statistics.py`**:
  - `get_numeric_summary()`, `get_categorical_summary()`, and `get_distribution_stats()`.

---

## 📁 Repository Directory Structure

```
Agentic_Data_Analyst/
│
├── app.py                          # Main Streamlit application entry point & router
├── nextstep.txt                    # Active development roadmap & phase tracking
├── plan.md                         # Master system architecture reference
├── README.md                       # Comprehensive platform documentation
├── pyproject.toml / uv.lock        # Project dependencies & package metadata
│
├── .streamlit/
│   └── config.toml                 # Streamlit UI theme and server configuration
│
├── data/
│   ├── sample/                     # Built-in demo datasets (CSV, Excel, SQLite)
│   ├── uploaded/                   # Stored user uploads
│   └── processed/                  # Transformed datasets
│
├── utils/                          # Cross-cutting foundational helpers
│   ├── file_handler.py             # Multi-format ingestion (CSV, Excel, JSON, SQLite)
│   ├── helpers.py                  # Formatters & column classification
│   ├── history.py                  # Upload history and sample dataset discovery
│   └── session_state.py            # Centralized Streamlit session state management
│
├── analysis/                       # Pure statistical & analytical engines
│   ├── profiling.py                # Dataset health score (0-100, A-F) & diagnostic audit
│   ├── statistics.py               # Descriptive stats, skewness, kurtosis
│   ├── missing_values.py           # Missing value analysis & imputation
│   ├── duplicates.py               # Duplicate detection & deduplication
│   ├── correlations.py             # Correlation matrices & top pairs
│   └── outliers.py                 # Outlier detection (IQR, Z-score) & Winsorization
│
├── components/                     # Modular, reusable Streamlit UI components
│   ├── sidebar.py                  # Ingestion sidebar & active dataset badge
│   ├── dataset_summary.py          # Metric KPI cards
│   ├── data_preview.py             # Interactive searchable table
│   ├── column_selector.py          # Smart type-aware dropdowns
│   ├── analysis_result.py          # Health cards, warning callouts & badges
│   ├── chart_selector.py           # Visual plot configuration panel
│   └── chat_interface.py          # Streamlit chat interface with code expander
│
├── tests/                          # Automated unit & interactive UI preview suites
│   ├── test_analysis_result.py     # Unit tests for analysis results
│   ├── test_analysis_result_ui.py  # Interactive UI preview for cards & badges
│   ├── test_chart_selector.py      # Unit tests for chart selector
│   ├── test_chart_selector_ui.py   # Interactive UI preview for chart selector
│   ├── test_chat_interface.py       # Unit tests for chat interface
│   ├── test_chat_interface_ui.py   # Interactive UI preview for chat interface
│   ├── test_column_selector.py     # Unit tests for column selector
│   ├── test_column_selector_ui.py  # Interactive UI preview for column selector
│   ├── test_data_preview.py        # Unit tests for data preview
│   ├── test_data_preview_ui.py     # Interactive UI preview for data preview
│   ├── test_dataset_summary.py     # Unit tests for dataset summary
│   ├── test_summary_ui.py          # Interactive UI preview for summary cards
│   ├── test_profiling.py           # Unit tests for health score & audits
│   └── test_sidebar.py             # Unit tests for sidebar component
│
├── visualization/                  # Chart builders & recommender heuristics
├── agent/                          # Autonomous AI Analyst core (LLM & code execution)
└── ui/                             # Application views (EDA, Viz, Chat, AutoML)
```

---

## 🚦 Interactive Component Previews

Test and inspect individual UI components in isolation before assembling pages:

```powershell
# 1. Preview Chart Selector with Live Plot Rendering
streamlit run tests/test_chart_selector_ui.py

# 2. Preview Conversational Chat Interface with Code Expanders
streamlit run tests/test_chat_interface_ui.py

# 3. Preview Health Score Hero Card & Diagnostic Alerts
streamlit run tests/test_analysis_result_ui.py

# 4. Preview Smart Type-Aware Column Dropdowns
streamlit run tests/test_column_selector_ui.py

# 5. Preview Paginated Data Table with Search
streamlit run tests/test_data_preview_ui.py
```

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`uv` recommended, or `venv`)

### 2. Setup Environment
```powershell
# Clone the repository
git clone https://github.com/your-username/Agentic_Data_Analyst.git
cd Agentic_Data_Analyst

# Create virtual environment & activate
uv venv
.venv\Scripts\activate

# Install dependencies in editable mode
uv pip install -e .
```

### 3. Run Automated Tests
Execute the full test suite (111 tests):
```powershell
pytest
```

### 4. Launch the Platform
```powershell
streamlit run app.py
```

---

## 🗺️ Project Roadmap

- [x] **Phase 1: Ingestion & Foundation**: Multi-format ingestion, sample datasets, session state.
- [x] **Phase 2: Analytical Engines**: Statistics, missing values, duplicates, outliers, correlations, health scoring.
- [x] **Phase 3: Modular UI Components**: All 7 UI widgets built, exported, and verified (111 unit tests passing).
- [ ] **Phase 4: Exploratory Data Analysis View**: Full EDA dashboard in `ui/Data_Analysis.py` wired into `app.py`.
- [ ] **Phase 5: Visual Analytics**: Plotly chart builders, automated chart recommender, and visual plot studio.
- [ ] **Phase 6: Autonomous AI Analyst**: Google Gemini / OpenAI agent integration with sandboxed Python code runner.
- [ ] **Phase 7: Predictive Auto-ML**: Automated classification & regression baselines with feature importance.

---

<p align="center">
  <sub>Built with ❤️ for rapid, autonomous data science.</sub>
</p>
