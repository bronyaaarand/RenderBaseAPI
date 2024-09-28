from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests as req

app = Flask(__name__)

client = MongoClient("mongodb+srv://rinputin482:Rinputin482qh@cluster0.5n8iybx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["raiden"]
collection = db["const"]

chat_colletion = db["dify_response"]

intents_labels = {
    'technical': 0,
    'statistic': 1,
    'contact': 2,
}

uri_dify_api = 'https://api.dify.ai/v1/chat-messages'
@app.route('/access-token', methods = ['GET'])
def access_token():
    token_document = collection.find_one({"name": "auth_code"})

    if token_document and "value" in token_document:
        return jsonify({"access_token": token_document["value"]})
    else:
        return jsonify({"error": "auth_code not found"}), 404
    
@app.route('/dify-message', methods = ['POST'])
def dify_message():
    agent_response = ""
    data = request.get_json()
    customer_request = data["customer_message"] if data["customer_message"] else "No idea"
    dify_body = {    
                "inputs": {},
                "query": customer_request,
                "response_mode": "blocking",
                "conversation_id": "",
                "user": "abc-123"
            }
    dify_auth = {
                'Authorization': 'Bearer app-lgrPbd1uUHYWUorb3WSPORqN'
            }
    dify_response = req.post(uri_dify_api, json=dify_body, headers=dify_auth)
    agent_response = dify_response.json()["answer"]
    message_id = dify_response.json()["message_id"]
    
    record = {
            'message_id': message_id,
            'customer_request': customer_request,
            'agent_response': agent_response
        }
    
    result = chat_colletion.insert_one(record)

    return jsonify(
        {
            'message_id': message_id,
            'customer_request': customer_request,
            'agent_response': agent_response
        }
    )

@app.route('/dify-history', methods = ['GET'])
def dify_history():
    documents = list(chat_colletion.find({}, {'_id': False}))[::-1]

    return jsonify(documents)


if __name__ == "__main__":
    app.run(debug= True)