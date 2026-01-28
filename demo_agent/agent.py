from google.adk.agents.llm_agent import Agent
import logging
from datetime import datetime

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    logger = logging.getLogger(__name__)
    # Usage inside your code or tools
    logger.info("city: %s", city)
    now = datetime.now()
    return {"status": "success", "city": city, "time": str(now)}


# Have a tool that looks at a given webpage, and provides a single fact from it
# Have another tool that can receive that fact, and double check it against wikipedia
# If the fact exists, then print success, else print fail.

def analyse_page():
    link = "https://web.archive.org/web/20150123055134/http://www.cmt.com/news/1600309/cmt-insider-interview-taylor-swift-part-1-of-2/"
    
    return {"status": "success", "fact": ""}

def double_check():
    pass

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="Gives out facts about bands",
    instruction="""
    You are a X.
    Use the Y to do the job.
    """,
    tools=[get_current_time],
)