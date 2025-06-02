from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import os
from langdetect import detect

"""Loads environment variables and validates the Gemini API key."""
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    """Initializes the chat session with agents and configuration."""
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    """Sets up the AsyncOpenAI client to connect to the Gemini API."""

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )
    """Configures the Gemini-2.0-flash model for chat interactions."""

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    """Creates the configuration for running agents."""

    # Initialize English and Urdu agents
    english_agent = Agent(
        name="EnglishAssistant",
        instructions="You are a helpful assistant that responds only in English. Provide clear and concise answers.",
        model=model
    )
    """Creates an agent that responds in English."""

    urdu_agent = Agent(
        name="UrduAssistant",
        instructions="آپ ایک مددگار اسسٹنٹ ہیں جو صرف اردو میں جواب دیتے ہیں۔ واضح اور مختصر جوابات دیں۔",
        model=model
    )
    """Creates an agent that responds in Urdu."""

    # Store agents and config in session
    cl.user_session.set("english_agent", english_agent)
    cl.user_session.set("urdu_agent", urdu_agent)
    cl.user_session.set("config", config)
    cl.user_session.set("chat_history", [])
    """Stores agents, configuration, and chat history in the user session."""

    await cl.Message(content="Welcome to the AI Assistant! Type in English or Urdu, and I'll respond accordingly.").send()
    """Sends a welcome message to the user."""

@cl.on_message
async def main(message: cl.Message):
    """Processes incoming user messages and generates responses using the appropriate agent."""
    # Send a thinking message
    msg = cl.Message(content="Thinking...")
    await msg.send()
    """Displays a 'Thinking...' message to the user."""

    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    english_agent: Agent = cast(Agent, cl.user_session.get("english_agent"))
    urdu_agent: Agent = cast(Agent, cl.user_session.get("urdu_agent"))
    """Retrieves configuration and agents from the user session."""

    # Retrieve the chat history from the session
    history = cl.user_session.get("chat_history") or []
    """Fetches the chat history from the session or initializes an empty list."""

    # Append the user's message to the history
    history.append({"role": "user", "content": message.content})
    """Appends the user's message to the chat history."""

    try:
        # Detect the language of the input message
        detected_lang = detect(message.content)
        """Detects the language of the user's message (English or Urdu)."""

        # Choose the appropriate agent based on language
        selected_agent = urdu_agent if detected_lang == "ur" else english_agent
        """Selects the appropriate agent based on the detected language."""

        print(f"\n[CALLING_{selected_agent.name}_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(
            starting_agent=selected_agent,
            input=history,
            run_config=config
        )
        """Calls the selected agent to generate a response via the API."""

        response_content = result.final_output
        """Stores the agent's response."""

        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()
        """Updates the 'Thinking...' message with the agent's response."""

        # Update the session with the new history
        cl.user_session.set("chat_history", result.to_input_list())
        """Updates the chat history in the session."""

        # Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant ({selected_agent.name}): {response_content}")
        """Logs the user's message and the agent's response."""

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")
        """Handles any errors and displays them to the user."""