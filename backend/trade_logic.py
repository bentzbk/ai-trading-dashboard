from model import query_huggingface_model

def recommend_trades(live_data):
    """
    Prepare the input for the Hugging Face model and get trade recommendations.
    """
    # Format the payload as required by your Hugging Face model
    payload = {
        "inputs": live_data  # Adjust this structure to match your model's expected input
    }
    model_response = query_huggingface_model(payload)
    # Optionally, add post-processing for technical checks or formatting
    return model_response
