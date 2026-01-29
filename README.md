# 🤖 Fund Analytics Chatbot

A conversational AI chatbot that answers questions about fund portfolios, trades, and holdings using local LLMs (Ollama) and function calling. No cloud dependencies, no API costs.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Setup & Configuration](#setup--configuration)
- [Usage](#usage)
- [Performance Optimizations](#performance-optimizations)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## 📌 Overview

The Fund Analytics Chatbot is a **local-first, cost-free** solution for analyzing fund data via natural language. Instead of writing SQL or navigating spreadsheets, users ask questions in plain English:

- *"Show me top 5 holdings"*
- *"How many trades for fund XYZ?"*
- *"Compare all funds by market value"*

The chatbot:
1. Understands the query intent using a local LLM (Mistral via Ollama)
2. Maps the query to an analytics function (function calling pattern)
3. Executes the function against CSV data (Pandas)
4. Formats results into clear, factual natural language
5. Maintains conversation context across multiple turns

**Key benefit:** All processing happens locally. No data leaves your machine. No subscription fees.

---

## ✨ Features

- ✅ **Local LLM** — Uses Ollama (free, offline-capable, Mistral model)
- ✅ **Function Calling** — Precise query routing via LLM reasoning
- ✅ **CSV Data** — Load trades and holdings from CSV files
- ✅ **Streamlit UI** — Chat interface with persistent session state
- ✅ **Conversation Memory** — Session state stores chat history and cached results
- ✅ **Anti-hallucination** — Structured data only; no invented details
- ✅ **Performance Optimized** — Categorical dtypes, precomputed lowercase, caching
- ✅ **Error Handling** — Graceful fallbacks for missing data or connection issues

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend LLM** | Ollama + Mistral |
| **Data Processing** | Pandas + NumPy |
| **UI Framework** | Streamlit |
| **Language** | Python 3.8+ |
| **HTTP Client** | Requests |
| **Logging** | Python logging |

---

## 📁 Project Structure

```
fund-chatbot/
├── app.py                          # Streamlit UI entry point
├── data/
│   ├── trades.csv                  # Trade records
│   └── holdings.csv                # Portfolio holdings
├── src/
│   ├── __init__.py
│   ├── analytics.py                # Pure data functions (7 analytics)
│   └── data_loader.py              # LLM orchestration, session state
├── notebooks/
│   └── (optional exploratory analysis)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Ollama installed ([https://ollama.ai](https://ollama.ai))
- pip or conda

### Step 1: Clone / Setup Project

```bash
cd fund-chatbot
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install streamlit pandas numpy requests
```

### Step 3: Install & Start Ollama

Download Ollama from [https://ollama.ai](https://ollama.ai), then:

```bash
# Pull the Mistral model (first time only, ~5GB download)
ollama pull mistral

# Start Ollama server (runs on localhost:11434)
ollama serve
```

**Note:** Keep this terminal window open. Ollama listens on `http://localhost:11434/api/generate`.

---

## ⚙️ Setup & Configuration

### CSV Data Format

Ensure your CSV files have these columns (case-sensitive):

**trades.csv:**
- `PortfolioName` — Fund name
- (other trade fields)

**holdings.csv:**
- `PortfolioName` — Fund name
- `SecName` — Security name
- `SecurityTypeName` — Type (e.g., "Equity", "Bond")
- `Qty` — Quantity
- `MV_Base` — Market value
- `PL_YTD` — Year-to-date profit/loss

### Environment Variables (Optional)

None required. Ollama runs locally by default at `http://localhost:11434`.

To use a remote Ollama instance, edit `src/data_loader.py`:

```python
OLLAMA_URL = "http://your-remote-host:11434/api/generate"
```

---

## 💬 Usage

### Start the Chatbot UI

```bash
# Terminal 1: Start Ollama (if not already running)
ollama serve

# Terminal 2: Start Streamlit app
streamlit run app.py
```

The app opens at **http://localhost:8501**.

### Example Queries

1. **"Show me the top 5 holdings"**
   - Calls `get_top_holdings(limit=5)`
   - Returns formatted table of largest positions

2. **"How many trades for CoYold 1?"**
   - Calls `get_total_trades(fund="CoYold 1")`
   - Returns count of trades for that fund

3. **"Compare all funds by market value"**
   - Calls `get_fund_comparison()`
   - Returns sorted table of total values per fund

4. **"What's the yearly performance?"**
   - Calls `get_yearly_fund_performance()`
   - Returns P&L aggregated by fund

5. **"What holdings do we have by type?"**
   - Calls `get_fund_stats_by_type()`
   - Returns breakdown: Equities, Bonds, etc.

### UI Features

- **Chat History** — All messages persist in session state
- **Clear Chat** — Button to reset conversation
- **Sidebar Info** — Available funds, metrics, cached data explorer
- **Quick Tips** — Suggested queries

---

## 🧠 How It Works

### Architecture Flow

```
User Query
    ↓
[Streamlit Input]
    ↓
[LLM Prompt with Function Descriptions]
    ↓
[Ollama Generates Function Call Directive]
    ↓
[Parse & Execute Analytics Function]
    ↓
[Validate Result (not empty?)]
    ↓
[LLM Formats Structured Data → Natural Language]
    ↓
[Append to Session State & Display]
```



## 📝 Requirements

Create `requirements.txt`:

```
streamlit==1.28.0
pandas==2.0.0
numpy==1.24.0
requests==2.31.0
```

Install:

```bash
pip install -r requirements.txt
```

---

## 🔒 Security & Limitations

- **Local only:** No data uploaded to cloud
- **No authentication:** Run on trusted networks only
- **CSV immutable:** Updates require restarting app
- **LLM limitations:** Mistral may occasionally misinterpret complex queries
- **No write operations:** Chatbot is read-only (reports, no updates)

---

## 🚀 Future Enhancements

1. **Database backend** — SQLite with indexes for large datasets
2. **Richer visualizations** — Inline charts (Plotly, Matplotlib)
3. **Export results** — PDF/CSV report generation
4. **Multi-model support** — Switch between Mistral, LLaMA, Neural-Chat
5. **API endpoint** — FastAPI wrapper for programmatic access
6. **Role-based access** — Restrict queries per user
7. **Audit logging** — Track all queries and responses
8. **Batch processing** — Queue multiple queries

---

## 📚 References

- [Ollama Documentation](https://ollama.ai)
- [Streamlit Docs](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org)
- [Function Calling Pattern](https://platform.openai.com/docs/guides/function-calling)

---

## 📝 License

This project is open source and provided as-is for educational and commercial use.

---

## 👤 Author

Built by Divya for fund portfolio analytics.

---

## ❓ Support

For issues:
1. Check [Troubleshooting](#troubleshooting)
2. Verify CSV column names match `analytics.py`
3. Ensure Ollama is running and reachable
4. Check logs: `streamlit run app.py --logger.level=debug`

---

**Happy querying! 🚀**