import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/process"

# Test different queries
queries = [
    {
        "query": "Compare Python vs JavaScript for backend development",
        "task_type": "decision_making"
    },
    {
        "query": "Extract insights from sales data: Q1: $100k, Q2: $150k, Q3: $120k, Q4: $180k",
        "task_type": "data_processing"
    },
    {
        "query": "Explain machine learning to a 10-year-old",
        "task_type": "communication"
    }
]

for query_data in queries:
    response = requests.post(url, json=query_data)
    print(f"\nQuery: {query_data['query']}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
