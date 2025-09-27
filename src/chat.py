# The chat logic (uses agent + PDF retriever):

from langchain_core.messages import HumanMessage, AIMessage
from .pdf_processor import process_pdf
from .agent import langgraph_agent_executor, config, embeddings
import re

vector_store = None

# streaming mode
"""
"values" → clean, just the outputs.
"updates" → state changes (less clean, but informative).
"debug" → everything, good for development.
"""

# def format_latex(text: str) -> str:
#     """Ensure math equations are inside $$...$$"""
#     text = re.sub(r"\$(.*?)\$", r"$$\1$$", text)  # inline → block
#     return text


# ---Smart chat ---
async def chat_fn(message, pdf_file):        
    global vector_store
    output = ""

    # Handle PDF upload
    if pdf_file is not None:
        process_pdf(pdf_file, vector_store, embeddings)
        yield f"📄 PDF '{pdf_file.name}' added to knowledge base.\n\nNow ask me questions about it!"
        # return

    # Handle user message
    if message:
        if vector_store is None:
            # Normal LLM agent (no docs yet)
            async for chunk in langgraph_agent_executor.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="updates"
            ):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    last_message = chunk["agent"]["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        output = last_message.content
                        # output = smart_latex_format(last_message.content)

                        yield output
        else:
            # Retrieval mode with FAISS
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            relevant_docs = retriever.invoke(message)
            # Build the context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])

            augmented_msg = f"""
            Here is the retrieved context from the uploaded PDF (may be partial or incomplete):
            ---
            {context}
            ---

            Now answer the student’s question:
            {message}
            """
            print("################ context: \n",relevant_docs)
            async for chunk in langgraph_agent_executor.astream(
                {"messages": [HumanMessage(content=augmented_msg)]},
                config=config,
                stream_mode="updates"
            ):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    last_message = chunk["agent"]["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        output += last_message.content
                        # output = smart_latex_format(last_message.content)

                        yield output
