from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

# This data comes from your successful PySpark Hive run!
DASHBOARD_DATA = {
    "model_accuracy": 74.77,
    "total_analyzed": 20000,
    "top_failing_banks": {
        "City Union": 270,
        "IndusInd": 263,
        "AU Small": 262,
        "Canara": 261,
        "PNB": 259
    }
}

@app.route('/')
def home():
    # Serves the HTML dashboard
    return render_template('index.html', data=DASHBOARD_DATA)

@app.route('/predict', methods=['POST'])
def predict():
    # This endpoint simulates querying your MLlib Random Forest model
    req_data = request.json
    amount = float(req_data.get('amount', 0))
    bank = req_data.get('bank', '')
    
    # Simulate ML logic based on your real data
    risk_score = random.uniform(0.1, 0.4) 
    if bank in ["City Union", "IndusInd", "AU Small"]:
        risk_score += 0.4  # High risk banks
    if amount > 5000:
        risk_score += 0.15 # High amounts are riskier
        
    status = "HIGH RISK (Likely Failure)" if risk_score > 0.6 else "SAFE (Likely Success)"
    
    return jsonify({
        "status": status,
        "confidence": f"{min(risk_score * 100 + 20, 99.9):.1f}%",
        "risk_level": risk_score
    })

if __name__ == '__main__':
    print("🚀 Starting Payment Analytics Dashboard...")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
