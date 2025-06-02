Simple Agents Workflow with OpenAI Agents SDK and Tools
Task
Create a basic workflow with three agents using the OpenAI Agents SDK, Chainlit for the UI, and Gemini LLM via LiteLLM:

urdu_agent: Handles queries in Urdu.
english_agent: Handles queries in English.
triagent: Checks if the query is in Urdu or English and sends it to the right agent.
The UI will use Chainlit to take user input and show responses.
Use Gemini LLM via LiteLLM to process queries and generate responses.

Additional Requirements

Add a few simple tools to enhance the agents' capabilities.
Include a dummy weather tool as an example, which takes a city name as a parameter and returns a random weather condition from a predefined list of 4-5 options (e.g., sunny, cold, windy, rainy, cloudy).

Example Weather Tool
Tool Name: get_weatherDescription: Returns a random weather condition for a given city.
Parameters: city (string)
Output: Randomly selects and returns one weather condition from: ["sunny", "cold", "windy", "rainy", "cloudy"].

Example:  

Input: get_weather("Lahore")  
Output: "The weather in Lahore is sunny."
