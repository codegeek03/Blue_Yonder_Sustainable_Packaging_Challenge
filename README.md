# Smart Packaging Recommender

A FastAPI application that recommends optimal packaging materials for products using specialized AI agents, groq for chain-of-thought reasoning, and Tavily for web research.

## 🚀 Features

- Product-based packaging material recommendations
- Multiple specialized agents for comprehensive analysis:
  - Research Agent (using Tavily for web search)
  - Quality Assessment Agent
  - Environmental Impact Agent
  - Regulatory & Consumer Behavior Agent 
  - Logistics & Cost Agent
  - Orchestrator Agent (Final Decision Maker)
- Interactive Web UI
- RESTful API endpoints
- Chain-of-thought reasoning using groq
- Free web research using Tavily

## 🏗️ Project Structure

```
smart-packaging-recommender/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research.py      # Research Agent using Tavily
│   │   ├── quality.py       # Quality Assessment Agent
│   │   ├── environmental.py # Environmental Impact Agent
│   │   ├── regulatory.py    # Regulatory & Consumer Behavior Agent
│   │   ├── logistics.py     # Logistics & Cost Agent
│   │   └── orchestrator.py  # Orchestrator Agent (LLM Judge)
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py     # API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── models.py        # Pydantic models
│   └── templates/           # UI templates
│       └── index.html
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── test_api.py
│   └── test_agents.py
├── requirements.txt         # Project dependencies
├── .env.example            # Example environment variables
├── .gitignore
└── README.md               # This file
```

## 🔧 Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-packaging-recommender.git
cd smart-packaging-recommender
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Access the application:
- Web UI: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔑 Environment Variables

Create a `.env` file with the following variables:
```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## 🚀 API Usage

### Get Packaging Recommendation

```bash
curl -X POST "http://localhost:8000/api/get-packaging" \
     -H "Content-Type: application/json" \
     -d '{"product_name": "lipstick"}'
```

Example Response:
```json
{
  "best_material": "Biodegradable Composite",
  "overall_scores": {
    "Paper": 80,
    "Plastic": 75,
    "Biodegradable Composite": 85
  },
  "explanation": "Biodegradable Composite achieves the highest overall score due to its superior environmental performance and strong compliance ratings despite a slightly higher logistics cost."
}
```

## 🧪 Running Tests

```bash
pytest tests/
```

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request