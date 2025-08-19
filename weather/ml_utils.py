import os
import torch
from transformers import RobertaForSequenceClassification, RobertaTokenizerFast
from django.conf import settings

try:
    # Define model path
    model_path = os.path.join(settings.BASE_DIR, 'weather', 'models', 'address_classifier')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
except Exception as e:
    raise

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

tokenizer = RobertaTokenizerFast.from_pretrained(model_path)

# Load model
model = RobertaForSequenceClassification.from_pretrained(model_path)
model.to(device)
model.eval()

# Define labels
labels = {
    'City': 0,
    'GPS Coordinates': 1,
    'Town': 2,
    'Zip Code': 3,
    'Country': 4,
    'Landmarks': 5
}

def classify_address(address):
    try:
        inputs = tokenizer(
            address, 
            padding="max_length", 
            truncation=True, 
            max_length=32, 
            return_tensors="pt"
        )
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            pred_id = logits.argmax(dim=-1).item()
        
        # Convert prediction ID to label
        id2label = {v: k for k, v in labels.items()}
        predicted_type = id2label[pred_id]
        
        return predicted_type
        
    except Exception as e:
        raise

def classify_address_type(address):
    return classify_address(address)
