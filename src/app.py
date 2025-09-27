# Gradio UI entry point:
import gradio as gr
from .chat import chat_fn
from .agent import embeddings
from .pdf_processor import load_faiss


with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Tutor")

    # Session state: each user gets their own
    session_state = gr.State(value=None)
    
    with gr.Row():
        text_input = gr.Textbox(label="Your Question")
        text_submit = gr.Button("Ask Question")

    with gr.Row():
        pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
        pdf_submit = gr.Button("Upload PDF")

    with gr.Column():
        gr.Markdown("### AI Response")  # Visible header
        output = gr.Markdown()

 
    dummy_pdf = gr.State(value=None)
    dummy_text = gr.State(value=None)

    text_submit.click(fn=chat_fn, inputs=[text_input, dummy_pdf, session_state], outputs=[output, session_state])
    pdf_submit.click(fn=chat_fn, inputs=[dummy_text, pdf_input, session_state], outputs=[output, session_state])

if __name__ == "__main__":
    print("🚀 Launching Gradio app...")
    demo.launch(share=True)
