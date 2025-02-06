# app.py
from flask import Flask, request, jsonify
from workflow import predict_custom_agent_answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint to get chatbot response.
    Expected JSON payload:
      { "input": "User's question here" }
    """
    data = request.get_json()
    if not data or "input" not in data:
        return jsonify({"error": "Invalid request payload"}), 400
    
    try:
        result = predict_custom_agent_answer(data)
        return jsonify(result)
    except Exception as e:
        # In production, you might log the error and return a generic error message.
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
