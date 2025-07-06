from model import query_huggingface_model

def recommend_trades(processed_data):
    """
    Feed preprocessed data to the Hugging Face model and return recommendations.
    """
    payload = {
        "inputs": processed_data  # Adjust this key as needed for your model
    }
    model_response = query_huggingface_model(payload)
    return model_response
