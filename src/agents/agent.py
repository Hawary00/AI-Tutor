# LLM + agent setup

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from src.prompts import combined_prompt
from dotenv import load_dotenv
load_dotenv()
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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

# if __name__ == "__main__":
#     # Visualize the graph
#     from langchain_core.runnables.graph import MermaidDrawMethod

#     # Render graph to PNG (bytes)
#     img_bytes = langgraph_agent_executor.get_graph().draw_mermaid_png(
#         draw_method=MermaidDrawMethod.PYPPETEER
#     )
#     # Save it locally
#     with open("graph.png", "wb") as f:
#         f.write(img_bytes)

#     print("Graph saved as graph.png ✅")
