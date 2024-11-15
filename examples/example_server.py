import json
import requests
import random
from transformers import AutoTokenizer

# Load the activation data from the JSON file
with open("path_to_contexts", "r") as f:
    activation_data = json.load(f)
# Load the explanation data
with open("path_to_explanations", "r") as f:
    explanation_data = json.load(f)
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b")

actual_data = activation_data["features"][10]
activations = actual_data["activations"]
for activation in activations:
    activation["tokens"] = tokenizer.batch_decode(activation["tokens"]) # If you have the tokens already decoded, you can skip this step
feature_index = actual_data["feature_index"]
print(feature_index)
explanation = explanation_data[str(feature_index)]
# Server URL
BASE_URL = "http://localhost:5000"

# API key and model (replace these with your actual values)
API_KEY = "your_api_key_here"
MODEL = "meta-llama/llama-3.1-70b-instruct:free"

def test_generate_explanation():
    url = f"{BASE_URL}/generate_explanation"
    
    # Prepare the request data
    data = {
        "activations": activations[:10], # Using only 10 activations for testing
        "api_key": API_KEY,
        "model": MODEL
    }
    
    # Send the request
    response = requests.post(url, json=data)
    
    print("Generate Explanation Response:")
    print(response.status_code)
    print(response.json())

def test_generate_score(score_type):
    if score_type == "embedding":
        url = f"{BASE_URL}/generate_score_embedding"
        data = {
            "activations": activations, # Using only the other activations for testing
            "explanation": explanation,
        }
    else:
        url = f"{BASE_URL}/generate_score_fuzz_detection" 
        data = {
            "activations": activations[10:], # Using only the other activations for testing
            "explanation": explanation,
            "api_key": API_KEY,
            "model": MODEL,
            "type": score_type
        }
        
    # Send the request
    response = requests.post(url, json=data)
    
    print(f"Generate Score ({score_type}) Response:")
    #print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    #test_generate_explanation()
    #test_generate_score("fuzz")
    #test_generate_score("detection")
    test_generate_score("embedding")
