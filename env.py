import getpass
import os

api_key="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"
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: {api_key}")





    # # Endpoint to set (or update) the API key.
# @app.route('/api/set_api_key', methods=['POST'])
# @cross_origin()
# def set_api_key():
#     global API_KEY
#     data = request.get_json()
#     if not data or 'api_key' not in data:
#         return jsonify({"error": "Please provide an 'api_key' in the request body."}), 400

#     API_KEY = data['api_key']
#     return jsonify({"message": "API key set successfully"}), 200

# # Endpoint to set (or update) the manual prompt.
# @app.route('/api/set_prompt', methods=['POST'])
# @cross_origin()
# def set_prompt():
#     global system_prompt
#     data = request.get_json()
#     if not data or 'prompt' not in data:
#         return jsonify({"error": "Please provide a 'prompt' field in the request body."}), 400

#     system_prompt["manual"] = data['prompt']
#     return jsonify({
#         "message": "Manual prompt updated successfully.",
#         "system_prompt": system_prompt
#     }), 200