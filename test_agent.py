import asyncio
from dotenv import load_dotenv
load_dotenv()

from vision_agents.core import Agent, User
from vision_agents.plugins import gemini, getstream

import os

async def main():
    agent = Agent(
        edge=getstream.Edge(),
        agent_user=User(name='A', id='a'),
        instructions='Do something',
        llm=gemini.Realtime(model="gemini-2.0-flash-exp", fps=5)
    )
    print("Agent creation successful!")

asyncio.run(main())
