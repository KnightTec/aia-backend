from flask import Flask, jsonify, request
from intial_question_prompt import ask_for_case_questions
from intial_question_prompt import summarize_webpage_content

app = Flask(__name__)

cache = {}

# TODO: add api key to .ini


@app.route('/init/use_case', methods=['POST'])
def init():
    data = request.get_json()
    case_description = data['case_description']
    json_output = ask_for_case_questions(case_description=case_description)
    return jsonify(json_output)


@app.route('/init/summarize_webpage', methods=['POST'])
def init():
    data = request.get_json()
    url = data['webpage_url']
    json_output = summarize_webpage_content(webpage_url=url)
    return jsonify(json_output)


if __name__ == '__main__':
    app.run(debug=True)
