# LLM + agent setup

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from .prompts import combined_prompt
from dotenv import load_dotenv
load_dotenv()

# Models
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-lite", streaming=True)
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

# Memory
memory = MemorySaver()

# Agent
langgraph_agent_executor = create_react_agent(
    llm,
    tools=[],
    prompt=combined_prompt,
    checkpointer=memory
)

config = {"configurable": {"thread_id": "test-thread"}}
