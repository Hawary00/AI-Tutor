# # The chat logic (uses agent + PDF retriever):

from langchain_core.messages import HumanMessage, AIMessage
from .pdf_processor import process_pdf
from .agents.agent import langgraph_agent_executor, config, embeddings
import uuid

# Per-user storage
user_vector_stores = {}
user_memories = {}

# Helper functions for sessions
def get_user_session(session_state=None):
    """
    Ensure session_state is always a dict with a 'session_id'.
    If None or dict, generate a new session_id.
    """
    if session_state is None or not isinstance(session_state, dict):
        return {"session_id": str(uuid.uuid4())}
    if "session_id" not in session_state:
        session_state["session_id"] = str(uuid.uuid4())
    return session_state
    

def get_user_vector_store(session_state):
    session_state = get_user_session(session_state)
    session_id = session_state["session_id"]
    if session_id not in user_vector_stores:
        user_vector_stores[session_id] = None  # FAISS will be initialized on PDF upload
    return user_vector_stores[session_id]

def set_user_vector_store(session_state, vector_store):
    session_state = get_user_session(session_state)
    session_id = session_state["session_id"]
    user_vector_stores[session_id] = vector_store

# ---Smart chat ---
async def chat_fn(message, pdf_file, session_state=None):
    session_state = get_user_session(session_state)
    session_id = session_state["session_id"]
    print("Session ID:", session_id)

    vector_store = get_user_vector_store(session_state)
    output = ""

    # Handle PDF upload
    if pdf_file is not None:
        vector_store = process_pdf(pdf_file, vector_store, embeddings, session_id=session_id)  # assign the returned FAISS store
        set_user_vector_store(session_state, vector_store)
        output =  f"📄 PDF '{pdf_file.name}' added to your knowledge base.\n\nNow ask me questions!"
        yield output, session_state

    # Handle user message
    if message:
         # Normal LLM   
        if vector_store is None:
            # Normal LLM agent (no docs yet)
            async for chunk in langgraph_agent_executor.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="updates"
            ):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    print("response from the model(llm):", chunk)
                    last_message = chunk["agent"]["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        output = last_message.content
                        yield output, session_state
        else:
            # Retrieval mode with FAISS # Retrieval + RAG
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            relevant_docs = retriever.invoke(message)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])

            augmented_msg = f"""
            Here is the retrieved context from your uploaded PDFs:
            ---
            {context}
            ---
            Now answer the student’s question:
            {message}
            """
            async for chunk in langgraph_agent_executor.astream(
                {"messages": [HumanMessage(content=augmented_msg)]},
                config=config,
                stream_mode="updates"
            ):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    print(f"Retrieved {len(relevant_docs)} documents for question: {message}")
                    print("response from RAG:", chunk)
                    last_message = chunk["agent"]["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        output += last_message.content
                        yield output, session_state
