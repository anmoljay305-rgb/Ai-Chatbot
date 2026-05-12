from transformers import pipeline

def get_llm():
    return pipeline(
        "text-generation",
        model="distilgpt2",
        max_length=200
    )