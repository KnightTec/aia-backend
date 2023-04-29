from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

cache = {}

'''
Input: Initial problem statement
Output: First analysis
'''
@app.route('/init', methods=['POST'])
def init():
    data = request.get_json()
    prompt = data['prompt']
    length = data.get('length', 50)
    temperature = data.get('temperature', 0.5)
    headers = {
        'Authorization': f'Bearer {CHATGPT_API_KEY}:{CHATGPT_API_SECRET}'
    }

    payload = {
        'prompt': prompt,
        'length': length,
        'temperature': temperature
    }
    response = requests.post(CHATGPT_API_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'out': 'Failed to generate text'}), 500


if __name__ == '__main__':
    app.run(debug=True)
