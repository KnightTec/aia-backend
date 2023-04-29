import openai
import json
import requests
import nltk
nltk.download("punkt")
from bs4 import BeautifulSoup
from typing import *
import configparser


def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    return stripped_text


def tokenize_string(string):
    tokens = nltk.word_tokenize(string)
    return tokens


commands = []
actions_map = {}


def question_command_action(gpt_input):
    return gpt_input


question_command = {
    "name": "generate questions",
    "description": "generate a list of questions for a provided description in JSON",
    "input format": [{
        "type": "<question type here>",
        "question": "<your generated question here>"
    }]
}
commands.append(question_command)
actions_map[question_command["name"]] = question_command_action


def get_request_command_action(gpt_input):
    url = gpt_input["url"]
    response = requests.get(url)
    if response.status_code != 200:
        action_failed(f"get request action for url {url} failed")
    else:
        text_content = remove_html_tags(response.text)
        token_content = tokenize_string(text_content)
        text_content = " ".join(token_content)
        action_success(f"get request for url {url}", text_content)


get_request_command = {
    "name": "request website",
    "description": """
        If a user provides you with an url you can now get the content from this website with this action.
        Don't tell the user that you can't browse the web but instead create an action with the url.
        """,
    "input format": {
        "url": "<url>"
    }
}

actions_map[get_request_command["name"]] = get_request_command_action
commands.append(get_request_command)

SYSTEM_PROMPT = """
You are a system that executes a set of actions.
All your responses must be in the defined JSON format!
Your goal is to identify if the user wishes to execute any of the actions you know.
Don't execute actions where you don't feel like the user asked for them.
If not provide an empty list of actions.
For each command that you know you are given a name and a description.
Each command also tells you what the input format has to look like.
You strictly follow the provided format and generate a input in the provided format for each action
you believe the user wants to execute. 
Your response always consists of two sections:
1. The "actions" section contains all the actions you want to execute.
2. In the "answer" section you give a friendly response to the user and tell him about what you did. 
Each of your responses has the following JSON format:
{
    "actions" : [
        { 
            "action": "<action name>"
            "input": <your response strictly following the expected json format> 
        }
    ],   
    "answer": "<Explain to the user what you decided to execute. 
    If there were no actions don't mention it and just tell him about your knowledge.>" 
}
Your responses can never deviate from this format in any case! You can have an empty list of actions if yu think you
don't have an appropriate action.
Here is a list of the JSON descriptions of the commands that you know: 
"""

SYSTEM_PROMPT += json.dumps(commands)

config = configparser.ConfigParser()
config.read("config.ini")
openai.api_key = config["OpenAI"]["key"]

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

CASE_QUESTIONS_PROMPT = \
    """
    Business Case Description:
    
    <bc_description_here>
    
    Can you create a list of questions about this Business Case that will help you understand this business case better
    and that can help you find out in which areas they can use artificial intelligence to decrease production cost.
    Think about what datasets could help you understand the business better and ask for these datasets in your
    questions as well. The questions about the datasets should ask for specific datasets about the company
    and the market, that the company could posses. Don’t include questions about how artificial intelligence
    can improve the business as this is what you should ultimately answer at the end of this conversation.
    You can give the questions the following types: "simple", "dataset".
    """

BUSINESS_CASE = \
    """
    The fruit juice producer has noticed a growing demand for organic fruit juices in the market.
    They currently only produce conventional fruit juices and have no organic offerings.
    Research shows that the demand for organic fruit juices has been steadily increasing over the past few years.
    Consumers are increasingly concerned about their health and the environment, and are willing to pay a premium
    for organic products. By expanding their product line to include organic fruit juices, the producer could tap
    into this growing market and potentially increase their revenue. Producing organic fruit juice requires sourcing
    organic fruits, which can be more expensive than conventional fruits.
    Additionally, the producer would need to invest in equipment and facilities to meet organic certification standards.
    However, by entering the organic juice market, the producer could potentially increase their 
    revenue and market share, as well as improve their brand image and reputation.
    """


def use_action_gpt(message: str) -> Any:
    message += "\nOnly answer in the systems JSON format!"

    print("########### Message ############")
    print(message)
    print()

    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    print("###### response 1 #######")
    print(response)
    print()

    reply = response["choices"][0]["message"]["content"]

    messages.append({"role": "assistant", "content": reply})
    json_response = json.loads(reply)

    print("############ JSON ################")
    formatted_json = json.dumps(json_response, indent=4)
    print(formatted_json)
    print()

    print("############ Answer ###############")
    print(json_response["answer"])
    print()

    actions = json_response["actions"]
    for action in actions:
        # calls the action function
        actions_map[action["action"]](action["input"])

    print("###### response 2 #######")
    print(response)
    print()

    final_reply = response["choices"][0]["message"]["content"]
    json_response = json.loads(final_reply)
    return json_response["answer"]


def action_failed(action_details: str):
    message = f"Action {action_details} failed." \
              + "Please repeat the previous response without that action and adapt the \"answer\" section accordingly."
    use_action_gpt(message)


def action_success(action_details: str, action_result: str):
    message = f"Action {action_details} was a success. Here are the results: " \
              + action_result + "\n" \
              + "Here are your new instructions:" \
              + "For \"actions\" remove the successfully executed action and only created new actions if the results indicate that." \
              + "In the answer summarize your findings from the action."
    use_action_gpt(message)


def ask_for_case_questions(case_description: str) -> Any:
    message = CASE_QUESTIONS_PROMPT.replace("<bc_description_here>", case_description)
    return use_action_gpt(message)


def summarize_webpage_content(webpage_url: str) -> Any:
    return use_action_gpt(f"Can you check {webpage_url} and provide an answer that summarizes the webpages content?")


if __name__ == '__main__':
    # http://ztrxyv.com/
    use_action_gpt("Can you check https://www.cqse.eu/en/ and provide an answer that summarizes the webpages content?")
