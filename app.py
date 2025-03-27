import os
import json
import requests
from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask(__name__)

# Global dictionary to store the two prompt components.
system_prompt = {
    "manual": None,
    "url": None
}

# Global variable to store the API key.
API_KEY = "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"
CORS(app, resources={r"/*": {"origins": "*"}})


# Endpoint to set (or update) the API key.
@app.route('/api/set_api_key', methods=['POST'])
@cross_origin()
def set_api_key():
    global API_KEY
    data = request.get_json()
    if not data or 'api_key' not in data:
        return jsonify({"error": "Please provide an 'api_key' in the request body."}), 400

    API_KEY = data['api_key']
    return jsonify({"message": "API key set successfully"}), 200

# Endpoint to set (or update) the manual prompt.
@app.route('/api/set_prompt', methods=['POST'])
@cross_origin()
def set_prompt():
    global system_prompt
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Please provide a 'prompt' field in the request body."}), 400

    system_prompt["manual"] = data['prompt']
    return jsonify({
        "message": "Manual prompt updated successfully.",
        "system_prompt": system_prompt
    }), 200

# Endpoint to set (or update) the prompt fetched from a URL.
@app.route('/api/set_prompt_from_url', methods=['POST'])
@cross_origin()
def set_prompt_from_url():
    global system_prompt
    data = request.get_json()
    if not data or 'url' not in data or 'user_id' not in data:
        return jsonify({"error": "Please provide a 'url' and 'user_id' field in the request body."}), 400

    url = data['url']
    user_id = data['user_id']
    try:
        response = requests.get(f"{url}?userId={user_id}")
        response.raise_for_status()
        url_prompt_json = response.json()  # Expecting JSON response.
        # print(url_prompt_json)
    except Exception as e:
        return jsonify({"error": f"Error fetching prompt from URL: {e}"}), 500

    # Convert the JSON to a nicely formatted string if it's a dict, 
    # otherwise just convert to a string.
    if isinstance(url_prompt_json, dict):
        url_prompt = json.dumps(url_prompt_json, indent=2)
    else:
        url_prompt = str(url_prompt_json)

    # Update the system prompt with a more descriptive message.
    system_prompt["url"] = f"""
You have the following data in JSON format:
{url_prompt}

When the user asks you questions, reference the data above.
"""

    return jsonify({
        "message": "URL prompt updated successfully.",
        "system_prompt": system_prompt
    }), 200

# Endpoint to get the full system prompt (combining both components).
@app.route('/api/get_prompt', methods=['GET'])
@cross_origin()
def get_prompt():
    global system_prompt
    if system_prompt["manual"] is None and system_prompt["url"] is None:
        return jsonify({"error": "No system prompt has been set yet."}), 404

    # Combine the two components with a newline in between.
    combined_prompt = ""
    if system_prompt["manual"]:
        combined_prompt += system_prompt["manual"]
    if system_prompt["url"]:
        if combined_prompt:
            combined_prompt += "\n"
        combined_prompt += system_prompt["url"]

    return jsonify({"system_prompt": combined_prompt}), 200

# Endpoint to call the ChatGroq model.
@app.route('/api/chat', methods=['POST'])
@cross_origin()
def chat():
    data = request.get_json()
    if not data or "human_message" not in data:
        return jsonify({"error": "Please provide a 'human_message' field in the request body."}), 400

    if not API_KEY:
        return jsonify({"error": "API key not set. Please set it via /api/set_api_key."}), 500

    # Instantiate the ChatGroq client with the provided API key.
    llm = ChatGroq(
        model="llama-3.1-8b-instant",  # Use your desired model.
        api_key=API_KEY,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Get the combined system prompt.
    manual = system_prompt.get("manual") or ""
    url_component = system_prompt.get("url") or ""
    combined_prompt = manual + "\n" + url_component if manual and url_component else manual or url_component

    messages = []
    if combined_prompt:
        messages.append(("system", combined_prompt))
    messages.append(("human", data["human_message"]))

    try:
        ai_response = llm.invoke(messages)
        AI_MSG=ai_response.content
    except Exception as e:
        return jsonify({"error": f"LLM invocation error: {e}"}), 500

    return jsonify({"response": AI_MSG}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
