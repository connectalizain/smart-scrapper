import os
import asyncio
from dotenv import load_dotenv, find_dotenv
import chainlit as cl
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.responses import ResponseTextDeltaEvent
from agents import (
    set_tracing_disabled,
)
from tools import scrape_yp_listing
import json

_: bool = load_dotenv(find_dotenv())


set_tracing_disabled(disabled=True)  # Disable tracing for this example

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
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

    messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": user_input}
    ]

    try:
        response = await external_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            stream=True,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": scrape_yp_listing.__name__,
                        "description": scrape_yp_listing.__doc__,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "The URL to scrape"}
                            },
                            "required": ["url"],
                        },
                    },
                }
            ],
            tool_choice="auto",
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                if delta.content:
                    await msg.stream_token(delta.content)
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.function:
                            if tool_call.function.name == scrape_yp_listing.__name__:
                                await cl.Message(
                                    content=f"🔧 Tool called: {tool_call.function.name}"
                                ).send()
                                # The arguments are a JSON string, so we need to parse them
                                function_args = json.loads(tool_call.function.arguments)
                                tool_output = await scrape_yp_listing(**function_args)
                                await cl.Message(content=f"Tool output: {tool_output}").send()
                                # You might need to send this output back to the model for further processing
                                # For now, we just display it.

    except Exception as e:
        await cl.Message(content=f"An error occurred: {e}").send()
    finally:
        await msg.update()
