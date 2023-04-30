from flask import Flask, jsonify, request
from flask_cors import CORS
from intial_question_prompt import ask_for_case_questions, summarize_webpage_content, process_replies

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

cache = {}


@app.route('/init/use_case', methods=['POST'])
def init_use_case():
    data = request.get_json()
    case_description = data['case_description']
    json_output = ask_for_case_questions(case_description=case_description)
    return jsonify(json_output)


@app.route('/init/summarize_webpage', methods=['POST'])
def init_summarize_webpage():
    data = request.get_json()
    url = data['webpage_url']
    json_output = summarize_webpage_content(webpage_url=url)
    return jsonify(json_output)


@app.route('/process_replies', methods=['POST'])
def process_replies_endpoint():
    data = request.get_json()
    answer = process_replies(data)
    print("YY")
    print(answer)
    return jsonify({"solution": answer})

# IMPORTANT!!!!!!!
# RESTART THE SERVER BEFORE STARTING A NEW CHAT

if __name__ == '__main__':
    app.run(debug=True)
