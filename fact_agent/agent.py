from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from google import genai
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # For creating response content
from typing import Optional
import random
import warnings
import os
warnings.filterwarnings("ignore")

# Use one of the model constants defined earlier
MODEL_GEMINI_FLASH = "gemini-2.5-flash-lite"

fact_agent = None
validation_agent = None
updating_agent = None

known_facts = [
    "She is born in 1989",
    "She is an American",
    "She has released over 10 albums",
    "She owns her own record label"
]

def get_fact() -> dict:
    """
    Gets a fact about a musician
    
    :return: A dictionary containing the fact.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'fact' key with the fact details.
            If 'error', includes an 'error_message' key.
    :rtype: dict
    """
    print("--call get_fact")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "interview.txt")
    if not os.path.exists(file_path):
        return {"status": "error", "error_message": f"File not found at {file_path}"}

    client = genai.Client()
    fileupload = client.files.upload(file=file_path)

    # Generate the fact using Gemini
    response = client.models.generate_content(
        model=MODEL_GEMINI_FLASH,
        contents=[
            fileupload,
            "This file is a transcript of an interview between an interviewer and the musician Taylor Swift. From this interview get a single fact that is 1 sentence long."\
            "Only return the fact. Do not include any markup in the response"
            ],
    )


    return {"status": "success", "fact": response.text}

def validate_fact(fact: str) -> dict:
    """
    Validates that the given fact is an actual fact about the musician and not made up.
    
    :param fact: The fact that the function will validate
    :type fact: str
    :return: A dictionary containing the fact.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'fact_is_valid' key that is a boolean (True/False). If true then it's valid, if false the fact is not valid.
            If 'error', includes an 'error_message' key.
    :rtype: dict
    """
    print("--call validate_fact")
    # Validate the fact against wikipedia.
    client = genai.Client()
    response = client.models.generate_content(
        model=MODEL_GEMINI_FLASH,
        contents=[
            "I have a fact about Taylor Swift that I want you to validate. Only use the webpage wikipedia to validate: https://en.wikipedia.org/wiki/Taylor_Swift"
            "Only return 'true' or 'false'"
            f"The fact is : {fact}"
            ],
    )

    return {"status": "success", "fact_is_valid": response.text}

def add_fact(fact: str):
    print(f"new fact addded {fact}")
    known_facts.append(fact)

def get_safe_fact() -> dict:
    """
    Will return a fact that is guaranteed to be accurate. This is from a predetermined list.
    
    :return: A dictionary containing the fact.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'fact' key with the fact details.
            If 'error', includes an 'error_message' key.
    :rtype: dict
    """
    print("--call get_safe_fact")

    i = random.randint(0,len(known_facts)-1)

    return {"status": "success", "fact": known_facts[i]}

def log_info():
    print("logging: ")
    print(f"known facts are : {known_facts}")


fact_agent = Agent(
        model=MODEL_GEMINI_FLASH,
        name="fact_agent",
        instruction="You are an agent that generates facts. To get a fact use the 'get_fact' function",
        description="Gets facts about a particular artist",
        tools=[get_fact],
        output_key="fact"
    )

validation_agent = Agent(
        model=MODEL_GEMINI_FLASH,
        name="validation_agent",
        instruction=
        "You are an agent who validates facts given to you. "\
        "The fact is '{fact}'."\
        "Use the 'validate_fact' function to judge if a fact is valid or not."\
        "If a fact is valid, then add that fact using the 'add_fact' function.",
        description="Validates any facts that are given to it.",
        tools=[validate_fact],
        output_key="fact_is_valid"
    )

updating_agent = Agent(
    model=MODEL_GEMINI_FLASH,
    name="validation_agent",
    instruction=
    "You are an agent who updates the fact list only if it's a valid fact. "\
    "The fact is either true or false. "\
    "If the fact is valid call the 'add_fact' function and add the fact '{fact}', then call the tool 'log_info'. If false then log info using 'log_info'. "\
    "fact = {fact_is_valid}",
    description="Validates any facts that are given to it.",
    tools=[add_fact, log_info]
)

# root_agent = Agent(
#     name="root_fact_agent",
#     model=MODEL_GEMINI_FLASH,
#     description="Main agent: Will leverage the sub agents to get facts about a musician.",
#     instruction="You are the main fact agent. Your job is to get facts from the fact_agent" \
#     "and then validate that fact using the validation_agent." \
#     "The flow for this is:" \
#     "1. Read the user input." \
#     "2. Get a fact from the fact_agent." \
#     "3. Validate the fact using the validation_agent." \
#     "4. If the fact is valid, then return the fact back to the user." \
#     "5. If the fact is not valid, then get a fact from 'get_safe_fact' and return that to the user." \
#     "6. Finally, call the 'log_info' function to print logging information.",
#     tools=[get_safe_fact, log_info],
#     sub_agents=[fact_agent, validation_agent],
#     output_key="lastest_fact"
# )
root_agent = SequentialAgent(
    name="root_agent",
    sub_agents=[fact_agent, validation_agent, updating_agent]
)
