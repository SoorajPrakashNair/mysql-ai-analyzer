AI-Powered MySQL Performance Analyzer
=================================================

This project is about building a **local AI tool** that helps analyze and improve MySQL database performance using a local LLaMA model and MCP server. The idea is to make performance tuning easier by letting AI understand logs, find bottlenecks, and suggest improvements — all locally, without using cloud APIs.

🧰 Tools & Tech Stack
---------------------
- **Ollama** (to run LLaMA locally)
- **LLaMA 3.1 8B** model
- **MySQL** (local DB setup with test data)
- **MCP SDK** (for server + tooling)
- **Python** (used in tools and MCP setup)

🛠️ What I Set Up
-----------------

### 🧠 Local LLaMA Model
- Installed Ollama:  
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- Pulled the model:
  ```bash
  ollama pull llama3:8b
  ```
- Ran a basic test:
  ```bash
  ollama run llama3:8b
  ```

### 🗄️ MySQL Setup
- Installed MySQL locally
- Created a sample DB with a few tables and dummy data
- Enabled **slow query log** to test performance tools

### 🔧 MCP Server + Tools
- Installed MCP SDK
- Created tools that:
  - `analyse_slow_queries`: Parses the MySQL slow query log
  - `check_table_indexes`: Lists table indexes
  - `get_performance_metrics`: Fetches CPU, memory & MySQL stats

### 🔗 AI Integration
- Connected the local LLaMA model to my MCP tools
- Asked questions like:
  - "What indexes should I add?"
  - "Find my slowest queries"
- Compared AI suggestions with actual MySQL `EXPLAIN` output — pretty close!

📝 Notes
--------
- Running everything locally (no cloud/GPT)
- Helpful for **offline tuning** or secure environments
- AI can give real-time DB tuning advice, making dev life easier

📦 Deliverable
--------------
✅ Fully working local AI system that:
- Reads logs  
- Checks performance  
- Suggests fixes  
- Uses **no cloud APIs**

Includes:
- Source code
- MCP tools
- Setup scripts
- This README ✅
