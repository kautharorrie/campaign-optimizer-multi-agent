# 📄 Technical Specifications: Campaign Performance Optimization Assistant

This document provides a deeper breakdown of the technical components of the Campaign Performance Optimization Assistant including API definitions, file structure, tools, and service flow logic.

---

## 1. **API Definitions**

### 1.1 `/api/query`

| Method      | POST                                                        |
| ----------- | ----------------------------------------------------------- |
| Description | Receives user query and initiates the orchestration process |
| Body        | `{ "query": string, "user_id": string }`                    |
| Response    | `200 OK` `{ "session_id": string, "status": "processing" }` |

### 1.2 `/api/state/{session_id}`

| Method      | GET                                                         |
| ----------- | ----------------------------------------------------------- |
| Description | Retrieves the current state of the orchestration process    |
| Params      | `session_id: string`                                        |
| Response    | `{ "state": string, "last_agent": string, "next": string }` |

### 1.3 `/api/feedback`

| Method      | POST                                                |                |
| ----------- | --------------------------------------------------- | -------------- |
| Description | Submit feedback on recommendation for reinforcement |                |
| Body        | \`{ "session\_id": string, "feedback": "positive"   | "negative" }\` |

### 1.4 `/api/upload`

\| Method | POST | | Description | Uploads campaign-related documents | | Body | Multipart/form-data with document and user info | | Response | `{ "status": "uploaded", "filename": string }` |

---

## 2. **File Structure**

```plaintext
/campaign-assistant
├── /agents
│   ├── orchestration_agent.py
│   ├── data_gathering_agent.py
│   ├── analysis_agent.py
│   └── recommendation_agent.py
│
├── /data
│   ├── campaigns.json        # Mock database
│   └── /uploads              # Uploaded campaign files
│
├── /tools
│   ├── web_search.py
│   ├── wikipedia_lookup.py
│   ├── summarizer.py
│   └── pattern_detector.py
│
├── /api
│   └── routes.py
│
├── /config
│   └── settings.py
│
├── main.py                   # FastAPI entrypoint
└── graph.py                  # LangGraph state machine definition
```

---

## 3. **LangGraph State Machine Design**

```plaintext
[DATA_GATHERING] --> [ANALYSIS] --> [RECOMMENDATION_GENERATION]
     ^                                               ↓
     |<----------- [IMPROVEMENT_ITERATION] <---------
```

Each state triggers the corresponding agent. Based on the recommendation quality, feedback may loop the state back for more data or refined analysis.

---

## 4. **Mock Database Format (**``**\*\*\*\*)**

```json
[
  {
    "campaign_id": "001",
    "channel": "Google Ads",
    "budget": 1500,
    "clicks": 300,
    "impressions": 10000,
    "conversions": 25,
    "duration": "2 weeks"
  },
  ...
]
```

---

## 5. **Agent Responsibilities Summary**

| Agent              | Input                 | Output                 | Tools                                           |
| ------------------ | --------------------- | ---------------------- | ----------------------------------------------- |
| **Orchestration**  | User Query / Feedback | Workflow Decisions     | LangGraph                                       |
| **Data Gathering** | Campaign ID or Doc    | Campaign Metrics       | Web Search, Wikipedia, JSON, File Reader        |
| **Analysis**       | Metrics & Context     | Insights & Weak Points | Summarizer, Pattern Matcher, Prompt Engineering |
| **Recommendation** | Insights              | Structured Suggestions | Template Generator, Feedback Handler            |

---

## 6. **Environment Variables / Config (**``**\*\*\*\*)**

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WIKI_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"
USE_MOCK_DB = True
UPLOAD_FOLDER = "./data/uploads"
```

---

## 7. **Dependencies**

```toml
# pyproject.toml (excerpt)
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.110.0"
langchain = "^0.1.20"
pydantic = "^2.7.1"
utils = "custom local tools"
```

---

Let me know if you'd like to add data validation rules, test scenarios, or service diagrams.

include those and anything you feel are important to this use-case
