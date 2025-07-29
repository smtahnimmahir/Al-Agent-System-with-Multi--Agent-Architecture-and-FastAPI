# Multi‑Agent AI System

A scalable, maintainable, and modular AI agent framework built with FastAPI and LangChain. Orchestrate multiple specialized agents (data processing, decision‑making, communication) through a single RESTful interface, following software engineering best practices.

---

## 🚀 Key Features

- **Multi‑Agent Architecture**  
  Each agent inherits from a common `BaseAgent` and focuses on a single responsibility (e.g., data processing, decision making, communication). Easily add or swap agents without touching core orchestration logic.

- **LLM Integration**  
  Pluggable support for any large language model via LangChain, with built‑in helpers for prompt templates, chaining, and memory.

- **FastAPI REST API**  
  Production‑grade HTTP endpoints to trigger agent workflows, inspect state, and retrieve results via OpenAPI (Swagger) UI.

- **Modular & Extensible**  
  Clear directory structure with reusable modules—drop in new agents, services, or tools with minimal wiring.

- **Automated Testing**  
  Pytest suite covering agent logic, API endpoints, and edge cases to ensure reliability.

---

## 📂 Project Structure



## Project Structure

```
multi-agent-system/
│
├── app/
│   ├── agents/           # Agent classes (base, communicator, data processor, etc.)
│   ├── api/              # FastAPI endpoints and middleware
│   ├── core/             # Config, logging, and custom exceptions
│   ├── models/           # Pydantic schemas and state models
│   └── services/         # LLM service, graph builder, and tools
│
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── tests/                # Test suite
└── test_api.py           # API test script
```

---

## 🏗️ Architecture Overview

1. **BaseAgent**  
   Abstract class defining lifecycle hooks (`pre_process`, `process`, `post_process`, `execute`) and shared utilities (logging, error handling, statistics).

2. **OrchestratorAgent**  
   - Routes incoming requests to the appropriate agent(s) based on `task_type` or LLM‑driven classification.  
   - Maintains execution order and aggregates results.

3. **DataProcessorAgent**  
   - Extracts entities, transforms raw inputs, and performs analysis.  
   - Outputs structured data for downstream decision making.

4. **DecisionMakerAgent**  
   - Generates options, scores them, selects the best choice, and optionally validates against external data sources.

5. **CommunicatorAgent**  
   - Formats final outputs in a user‑friendly style (text, JSON).  
   - Supports adaptive tone, localization, and summarization.

---

## Getting Started

### 1. Setup with Conda (Recommended)
It is recommended to use [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html):

#### Clean up any old packages
```bash
conda clean --all
```
#### Create and activate environment
```bash
conda create -n agentsystem python=3.10.8
conda activate agentsystem
```
### 2. Install Dependencies

#### From project root
```bash
pip install -r requirements.txt
```
#### Or individually, for clarity:
```bash
pip install langchain langgraph langsmith langchain‑groq langchain_community langchain‑tavily
pip install fastapi uvicorn
```

### 3. Configure Environment

Edit `app/core/config.py` or set environment variables as needed for your LLM API keys and settings.

---

## Running the Application

Start the FastAPI server:

```bash
python .\main.py
```

Open the interactive API docs in your browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

#### Press CTRL+C in the terminal to stop.
---


## API Usage & Running Tests

### Example Endpoint

- **POST** `/api/v1/process`

**Request Body:**
```json
{
  "query": "Explain machine learning to a 10-year-old",
  "task_type": "communication"
}
```

**Response:**
```json
{
  "result": "Machine learning is like teaching a computer to learn from examples..."
}
```

---

## Running Tests

### 1. Unit Tests

```bash
pytest tests/
```

### 2. API Test Script

Make sure the server is running, then:

```bash
python test_api.py
```

This will send example requests to the API and print the responses.

---

## Agent Details

### OrchestratorAgent

- **Purpose:** Routes queries to the appropriate agents based on task type.
- **Routing:** Uses keyword matching and LLM-based classification to determine the task type and agent path.

### DataProcessorAgent

- **Purpose:** Extracts, transforms, and analyzes data from queries.
- **Capabilities:** Entity extraction, data point extraction, numerical/text analysis, and structured output.

### DecisionMakerAgent

- **Purpose:** Evaluates options and makes decisions based on processed data.
- **Capabilities:** Generates options, evaluates them, makes a final decision, and validates with external data if needed.

### CommunicatorAgent

- **Purpose:** Formats and communicates results in a user-friendly way.
- **Capabilities:** Determines communication style, prepares messages, formats output, and generates actionable insights.

---

## How to Add a New Agent

1. **Inherit from `BaseAgent`** and implement the `process` method.
2. **Register your agent** in the orchestrator or graph builder.
3. **Update routing logic** if your agent handles a new task type.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

---

## License

[MIT](LICENSE)

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Anaconda](https://www.anaconda.com/)
