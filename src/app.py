# app.py
import gradio as gr
from .chat import chat_fn
from .agents.agent import embeddings
from .pdf_processor import load_faiss
from .agents.summarizer_agent import summarizer_agent
from langgraph.errors import GraphInterrupt
from langgraph.types import Command
import uuid
import gradio as gr
import uuid
from langgraph.errors import GraphInterrupt

import gradio as gr
import uuid
from langgraph.errors import GraphInterrupt
from .agents.summarizer_agent import summarizer_agent
from langgraph.types import Command
from langgraph.graph import END
# # --- Global session storage ---
# sessions = {}

# --- Streaming summarization ---
def summarize_video( video_path, session_state, progress=gr.Progress()):
    """Stream main points and summary progressively, then pause for feedback."""
    if video_path:
        initial_state = {"video_path": video_path}

    else:
        raise gr.Error("Please upload a file.")

    thread_id = str(uuid.uuid4())
    # sessions["last_thread"] = thread_id

    main_points, summary, revised_summary = "", "", ""
    print("--- Started thread_id:", thread_id)

    try:
        print("--- State snapshot:", summarizer_agent.get_state({"configurable": {"thread_id": thread_id}}).values)

        stream = summarizer_agent.stream(
            input=initial_state,
            config={"configurable": {"thread_id": thread_id}},
        )
        
        for event in stream:
            print(f"--- DEBUG: {event}") # Keep this for debugging

            # --- CORRECTED LOGIC ---
            # Check if the node name is a KEY in the event dictionary
            if "main_point_summarizer" in event:
                data = event["main_point_summarizer"]
                if "main_points" in data:
                    main_points += data["main_points"]
                    yield main_points, summary, revised_summary, "Generating main points...", gr.update(visible=False), gr.update(visible=False), thread_id

            elif "summarizer_writer" in event:
                data = event["summarizer_writer"]
                if "summary" in data:
                    summary += data["summary"]
                    message = "✏️ Review summary and provide feedback, or type 'save'."
                    yield main_points, summary, revised_summary, message, gr.update(visible=True), gr.update(visible=True), thread_id

            elif "__interrupt__" in event:
                # The graph has paused and is waiting for feedback.
                # Save the interrupt data and stop the loop.
                state = summarizer_agent.get_state({"configurable": {"thread_id": thread_id}})
                main_points = state.values.get("main_points", main_points)
                summary = state.values.get("summary", summary)
                revised_summary = state.values.get("revised_summary", revised_summary)
                message = "✏️ Review summary and provide feedback, or type 'save'."
                yield main_points, summary, revised_summary, message, gr.update(visible=True), gr.update(visible=True), thread_id
                return # Stop the generator
            
            elif event == END or "__end__" in event:
                state = summarizer_agent.get_state({"configurable": {"thread_id": thread_id}})
                main_points = state.values.get("main_points", "")
                summary = state.values.get("summary", "")
                revised_summary = state.values.get("revised_summary", "")
                message = "✅ Summary finalized and saved."
                yield main_points, summary, revised_summary, message, gr.update(visible=False), gr.update(visible=False), thread_id
                return

            # --- END OF CORRECTION ---

    except GraphInterrupt as e:
        pass

    # Yield 7 items
    yield main_points, summary, revised_summary, "✅ Finished summarization.", gr.update(visible=False), gr.update(visible=False), thread_id

    

def resume_with_feedback(feedback, thread_id):
    """Resume or finalize summarization based on feedback."""
    if not thread_id:
        raise gr.Error("No active session to resume.")

    config = {"configurable": {"thread_id": thread_id}}
    revised_summary_stream = ""

    # Determine if user requested save or provided feedback
    is_save = isinstance(feedback, str) and feedback.strip().lower() == "save"
    input_data = {"feedback": "" if is_save else (feedback or ""), "save": is_save}

    try:

        resume_cmd = Command(resume=input_data)
        print("---Resuming with command:", resume_cmd)

        stream = summarizer_agent.stream(resume_cmd, config=config)

        for event in stream:
            print(f"--- DEBUG (resume): {event}")

            # --- revision events ---
            if "summarizer_rewriter" in event:
                data = event["summarizer_rewriter"]
                if "revised_summary" in data:
                    revised_summary_stream += data["revised_summary"]
                    yield (
                        gr.update(visible=True),
                        gr.update(visible=True),
                        revised_summary_stream,
                        "🔄 Revising summary...",
                        gr.update(visible=True),
                        gr.update(visible=True),
                        thread_id,
                    )

            # # --- waiting for more feedback ---
            elif "__interrupt__" in event:
                print("--- Waiting for next feedback...")
                final_state = summarizer_agent.get_state(config)
                # main_points = final_state.values.get("main_points", "")
                # summary = final_state.values.get("summary", "")
                revised_summary = final_state.values.get("revised_summary", "")

                # ✅ Make feedback box + button visible again
                yield (
                    # main_points,
                    # summary,
                    gr.update(visible=True),
                    gr.update(visible=True),
                    revised_summary,
                    "Revision complete. You can provide more feedback or type 'save' to finish.",
                    gr.update(visible=True, value=""),   # show feedback input again
                    gr.update(visible=True),             # show feedback button again
                    thread_id,
                )
                return  # stops the generator so it doesn’t continue to “finalized” message
      

            # --- graph finished --
            elif "__end__" in event or event == END:
                print("--- Graph ended event detected.")
                final_state = summarizer_agent.get_state(config)
                main_points = final_state.values.get("main_points", "")
                summary = final_state.values.get("summary", "")
                revised_summary = final_state.values.get("revised_summary", summary)

                yield (
                    # main_points,
                    # summary,
                    gr.update(visible=True),
                    gr.update(visible=True),
                    revised_summary,
                    "✅ Summary saved successfully.",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    thread_id,
                )
                return  # ✅ stop generator cleanly

        
        # --- fallback if stream finishes silently ---
        final_state = summarizer_agent.get_state(config)
        print("--- stream finishes silently --- and the event is: ", event)
        yield (
            # final_state.values.get("main_points", ""),
            # final_state.values.get("summary", ""),
            gr.update(visible=True),
            gr.update(visible=True),
            final_state.values.get("revised_summary", ""),
            "✅ Summary finalized.",
            gr.update(visible=False),
            gr.update(visible=False),
            thread_id,
        )

    except Exception as e:
        raise gr.Error(f"Error resuming summarization: {e}")



# ---- Main Gradio App ---- #
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Tutor (Nemo) - All-in-One 🎓")

    session_state = gr.State(value=None)
    summarizer_session_state = gr.State(value=None) # <--- ADD THIS LINE

    # --- Section 1: Chat & PDF ---
    with gr.Tab("💬 Chat & PDF"):
        with gr.Row():
            text_input = gr.Textbox(label="Your Question")
            text_submit = gr.Button("Ask Question")

        with gr.Row():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            pdf_submit = gr.Button("Upload PDF")

        output = gr.Markdown("### AI Response")

        dummy_pdf = gr.State(value=None)
        dummy_text = gr.State(value=None)

        text_submit.click(fn=chat_fn, inputs=[text_input, dummy_pdf, session_state], outputs=[output, session_state])
        pdf_submit.click(fn=chat_fn, inputs=[dummy_text, pdf_input, session_state], outputs=[output, session_state])

    with gr.Tab("🎬 Video Summary"):
        gr.Markdown("## 🎬 AI Video Summarizer with Feedback")

        with gr.Row():
            # video_url = gr.Textbox(label="YouTube URL")
            video_file = gr.Video(label="Or upload local video")

            main_points_box = gr.Textbox(
            label="Main Points", 
            elem_id="main_points_box", 
            interactive=False,  # Makes it read-only
            lines=5             # Gives it some height
            )
            summary_box = gr.Textbox(
                label="Summary", 
                elem_id="summary_box", 
                interactive=False, 
                lines=5
            )
            revised_box = gr.Textbox(
                label="Revised Summary", 
                elem_id="revised_box", 
                interactive=False, 
                lines=5
            )
        status_box = gr.Markdown(label="Status", elem_id="status_box")

        feedback_input = gr.Textbox(label="Your Feedback", visible=True)
        feedback_btn = gr.Button("Submit Feedback", visible=True)

        start_btn = gr.Button("Start Summarization")

        # --- Start summarization ---
        start_btn.click(
            fn=summarize_video,
            inputs=[ video_file, summarizer_session_state],
            outputs=[
                main_points_box,
                summary_box,
                revised_box,
                status_box,
                feedback_input,
                feedback_btn,
                summarizer_session_state
            ],
        )

      
        feedback_btn.click(
            fn=resume_with_feedback,  # <--- CORRECT
            inputs=[feedback_input, summarizer_session_state],
            outputs=[
                main_points_box, 
                summary_box, 
                revised_box, 
                status_box, 
                feedback_input, 
                feedback_btn,
                summarizer_session_state
            ]
        )


# ---- Launch ---- #
if __name__ == "__main__":
    print("🚀 Launching Gradio app...")
    demo.launch(share=True)



