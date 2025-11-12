from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
from moviepy.editor import VideoFileClip
import whisper
import re, tempfile, os
from dotenv import load_dotenv

# from langgraph.checkpoint.sqlite import SqliteSaver

# Load environment variables
load_dotenv()

# ---- Initialize Gemini ---- #
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-lite", streaming=True)

# ---- Define State ---- #
class SummaryState(dict):
    video_path: str = ""
    video_url: str = ""
    text: str = ""
    main_points: str = ""
    summary: str = ""
    feedback: str = ""
    revised_summary: str = ""
    save: bool = False


# ---- Whisper-based transcription ---- #
def extract_audio(video_path, audio_path="temp_audio.wav"):
    """Extract audio from video file."""
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path


def transcribe_with_whisper(video_path):
    """Transcribe a video file locally using OpenAI Whisper."""
    print("🎧 Extracting and transcribing audio with Whisper...")
    audio_path = extract_audio(video_path)
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path)
    os.remove(audio_path)  # clean up
    print("--- Transcription complete.")
    return result["text"]


# ---- YouTube Transcript helper ---- #
def extract_youtube_transcript(url: str):
    """Fetch transcript if available on YouTube."""
    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")
    video_id = video_id.group(1)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception:
        print("--- YouTube transcript not available. Downloading and transcribing locally...")
        import yt_dlp
        temp_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        ydl_opts = {"outtmpl": temp_path}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return transcribe_with_whisper(temp_path)


# ---- Graph Nodes ---- #
def video_loader(state: SummaryState):
    if state.get("video_url"):
        text = extract_youtube_transcript(state["video_url"])
    elif state.get("video_path"):
        text = transcribe_with_whisper(state["video_path"])
    else:
        raise ValueError("No video source provided.")
    return {"text": text}


def main_point_summarizer(state: SummaryState):
    prompt = f"Extract the main points from this transcript:\n\n{state['text']}"
    result = llm.invoke(prompt)
    # This 'yield's each token to your Gradio app's stream loop
    return {"main_points": result.content}


def summarizer_writer(state: SummaryState):
    prompt = f"Write a coherent summary from these points:\n\n{state['main_points']}"
    result = llm.invoke(prompt)
    return {"summary": result.content}


# For LangGraph Deploy
def user_feedback(state: SummaryState):
    """Pause the graph for user feedback."""
    payload = {
        "summary": state["summary"],
        "message": "Provide feedback or type 'save' to finish reviewing the summary.",
        "waiting_for_input": True,
    }

    user_input = interrupt(payload)

    # ✅ Normalize to dict
    if isinstance(user_input, str):
        # Convert plain text into proper dict for state updates
        if user_input.strip().lower() == "save":
            return {"feedback": "", "save": True}
        else:
            return {"feedback": user_input.strip(), "save": False}

    elif isinstance(user_input, dict):
        # Already valid JSON from Studio UI
        return {
            "feedback": user_input.get("feedback", ""),
            "save": bool(user_input.get("save", False)),
        }

    else:
        # Fallback
        return {"feedback": "", "save": False}



def summarizer_rewriter(state: SummaryState):
    prompt = (
        f"Revise the following summary based on feedback:\n\n"
        f"Summary:\n{state['summary']}\n\nFeedback:\n{state['feedback']}"
    )
    result = llm.invoke(prompt)
    return {"revised_summary": result.content, "summary": result.content}


# ---- Build Graph ---- #
graph = StateGraph(SummaryState)
graph.add_node("video_loader", video_loader)
graph.add_node("main_point_summarizer", main_point_summarizer)
graph.add_node("summarizer_writer", summarizer_writer)
graph.add_node("user_feedback", user_feedback)
graph.add_node("summarizer_rewriter", summarizer_rewriter)

graph.add_edge(START, "video_loader")
graph.add_edge("video_loader", "main_point_summarizer")
graph.add_edge("main_point_summarizer", "summarizer_writer")
graph.add_edge("summarizer_writer", "user_feedback")



def feedback_router(state):
    print("--- ROUTER STATE:", state)
    save_flag = state.get("save", False)
    feedback = str(state.get("feedback", "")).strip().lower()

    if save_flag or feedback == "save":
        print("--- SAVE detected — ending graph.")
        return END  # must match the key below
    else:
        print("--- Continuing to rewriter with feedback...")
        return "summarizer_rewriter"

# Conditional edges must match the *string keys* returned above
graph.add_conditional_edges(
    "user_feedback",
    feedback_router,
    {
        "summarizer_rewriter": "summarizer_rewriter",
        END: END,   #  The key "END" matches what the router returns
    },
)

# Add the normal feedback loop
graph.add_edge("summarizer_rewriter", "user_feedback")

# Enable checkpointing for resuming after interrupts
config = {"configurable": {"thread_id": "test-thread"}}

checkpointer = MemorySaver()
summarizer_agent = graph.compile(checkpointer) # add checkpint here for dev.(checkpointer=checkpointer) for langGraph deploy remove it

# from IPython.display import display, Image
# display(Image(summarizer_agent.get_graph().draw_mermaid_png()))


# ---- Main Execution ---- #
# if __name__ == "__main__":
        
    # Visualize the graph
    # from langchain_core.runnables.graph import MermaidDrawMethod

    # # Render graph to PNG (bytes)
    # img_bytes = summarizer_agent.get_graph().draw_mermaid_png(
    #     draw_method=MermaidDrawMethod.PYPPETEER
    # )
    # # Save it locally
    # with open("summarizer_agent.png", "wb") as f:
    #     f.write(img_bytes)

    # print("Graph saved as graph.png ")


    # while True:
    #     choice = input("Enter 'url' for YouTube URL or 'file' for local video file: ").strip().lower()
    #     if choice == "url":
    #         video_source = input("Enter YouTube video URL: ").strip()
    #         initial_state = {"video_url": video_source}
    #         break
    #     elif choice == "file":
    #         video_source = input("Enter path to local video file: ").strip()
    #         if not os.path.exists(video_source):
    #             print(f"Error: File not found at '{video_source}'. Please try again.")
    #             continue
    #         initial_state = {"video_path": video_source}
    #         break
    #     else:
    #         print("Invalid choice. Please enter 'url' or 'file'.")

    # print(f"Starting summarization process for: {video_source}\n")

    # thread_id = "session_1"
    # try:
    #     final_state = summarizer_agent.invoke(
    #         initial_state, config={"configurable": {"thread_id": thread_id}}
    #     )
    # except Exception as e:
    #     # Handle interrupt manually if running in CLI
    #     from langgraph.errors import GraphInterrupt
    #     if isinstance(e, GraphInterrupt):
    #         print("\n--- Summary ---\n")
    #         print(e.payload.get("summary", "No summary yet."))
    #         feedback = input(e.payload.get("message", "Enter feedback or 'save': ")).strip()
    #         summarizer_agent.update_state(thread_id, {"feedback": feedback})
    #         summarizer_agent.resume(thread_id)
    #     else:
    #         raise

    
