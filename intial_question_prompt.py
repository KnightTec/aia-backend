import openai
import json

commands = []

question_command = {
    "name": "generate questions",
    "description": "generate a list of questions for a provided description in JSON",
    "input format": [{
        "type": "<question type here>",
        "question": "<your generated question here>"
    }]
}

commands.append(question_command)

SYSTEM_PROMPT = """
You are a system that executes a set of commands.
Your goal is to identify if the user wishes to execute any of these commands.
For each command that you know you are given a name and a description.
Each command also tells you what the input format has to look like.
You strictly follow the provided format and generate a response in the provided format for each action
you believe the user wants to execute. 
Your response always consists of two sections:
1. The "actions" section contains all the actions you want to execute.
2. In the "answer" section you give a friendly response to the user and tell him about what you did. 
Each of your responses has the following JSON format:
{
    "actions" : [
        { 
            "action": "<action name>"
            "response": <your response strictly following the expected json format> 
        }
    ],   
    "answer": "<explain the user what actions you decided to execute and why you believe these are the right actions>" 
}
Here is a list of the JSON descriptions of the commands that you know: 
"""

SYSTEM_PROMPT += json.dumps(commands)

openai.api_key = "#Key"

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


def ask_for_case_questions(case_description: str):
    message = CASE_QUESTIONS_PROMPT.replace("<bc_description_here>", case_description)

    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response["choices"][0]["message"]["content"]

    messages.append({"role": "assistant", "content": reply})

    print("\n" + reply + "\n")


if __name__ == '__main__':
    ask_for_case_questions(BUSINESS_CASE)
