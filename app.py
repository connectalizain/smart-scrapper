import os
import asyncio
from dotenv import load_dotenv, find_dotenv
import chainlit as cl
# from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from tools import scrape_yp_listing

_: bool = load_dotenv(find_dotenv())


set_tracing_disabled(disabled=True)  # Disable tracing for this example

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash", openai_client=external_client
)

# Initialize Agent and attach the tool
agent = Agent(
    name="YP Extractor",
    model=llm_model,
    tools=[scrape_yp_listing],
    instructions="""
    You are a YellowPages.ca data extraction expert.

    When given a YellowPages.ca search results page URL:
      1. Call scrape_yp_listing(url)
      2. Collect all available listings on that page
      3. Return a JSON array of business details, including:
         - name (string)
         - phone (string)
         - website (string or 'Not found')
      4. Do NOT open individual business pages.
      5. Return data in only clean TABLE form (In rows and columns) — no commentary or text around it.
    """,
)


@cl.on_chat_start
async def start():
    await cl.Message(content="🕵️ Send me a any YellowPage URL — I’ll scrape and summarize contacts using my tool!").send()

@cl.on_message
async def handle_message(message: cl.Message):
    user_input = message.content.strip()
    
    # Start a message to stream tokens with 🤖 Assistant
    msg = cl.Message(content="🤖 Data: ")
    await msg.send()
    stream = Runner.run_streamed(agent, user_input)
    try:
        async for event in stream.stream_events():
            #  Stream model tokens
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                await msg.stream_token(event.data.delta)

            #  Notify when a tool is called
            elif event.type == "run_item_stream_event" and event.name == "tool_called":
                await cl.Message(
                    content=f"🔧 Tool called: {event.item.raw_item.name}"
                ).send()

    finally:
        # Ensure the spinner stops and message finalizes
        await msg.update()