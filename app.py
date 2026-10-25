import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Load the pre-trained modeling pipeline
model_path = "superkart_model.joblib"
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    raise FileNotFoundError(f"Model file '{model_path}' not found!")

@app.route("/v1/predict", methods=["POST"])
def predict():
    try:
        # Get JSON data from POST request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Convert request dictionary into a single-row DataFrame
        input_df = pd.DataFrame([data])
        
        # Make prediction using our pipeline
        prediction = model.predict(input_df)[0]
        
        return jsonify({"prediction": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/v1/predictbatch", methods=["POST"])
def predict_batch():
    try:
        # Expecting a CSV file to be uploaded
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        # Read the CSV directly into a DataFrame
        input_df = pd.read_csv(file)
        
        # Generate predictions for all rows
        predictions = model.predict(input_df)
        
        # Convert predictions to a dictionary mapping row index to predicted value
        results = {str(i): float(pred) for i, pred in enumerate(predictions)}
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run the application on host 0.0.0.0 and port 7860
    app.run(host="0.0.0.0", port=7860)
