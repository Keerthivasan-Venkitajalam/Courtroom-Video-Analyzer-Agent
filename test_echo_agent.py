"""
test_echo_agent.py
Test script for the baseline Echo voice agent.
"""
import asyncio
from agent import start_echo_agent
from constants import SESSION_ID

if __name__ == "__main__":
    print("Testing Echo Voice Agent...")
    print("This will simulate audio echo and measure round-trip latency")
    print("Press Ctrl+C to stop\n")
    
    asyncio.run(start_echo_agent(SESSION_ID))
