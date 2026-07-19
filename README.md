<p align="center">
  <h1 align="center">🎬 RAG-Based AI Video Assistant</h1>
  <p align="center">
    <strong>Transcribe · Summarize · Chat with your meetings — powered by RAG</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#usage">Usage</a> •
    <a href="#project-structure">Project Structure</a> •
    <a href="#ui-highlights">UI Highlights</a>
  </p>
</p>

---

An AI-powered meeting intelligence tool that extracts actionable insights from video and audio content. Drop in a **YouTube URL**, **upload a file**, or enter a **local file path**, and the assistant will transcribe, summarize, extract action items, key decisions, and open questions — then let you **chat with the transcript** using a Retrieval-Augmented Generation (RAG) pipeline.

## Features

| Feature | Description |
|---|---|
| 🔊 **Audio Extraction** | Download audio from YouTube URLs, upload files directly, or load local audio/video files. Automatically converts to WAV and chunks long recordings for efficient processing. |
| 📝 **Dual Transcription Engines** | **Whisper** (local, OpenAI) for English • **Sarvam AI** (cloud API) for Hinglish → English translation |
| 🏷️ **Auto Title Generation** | Generates a concise, professional meeting title from the transcript |
| 📋 **Smart Summarization** | Map-reduce summarization pipeline — splits long transcripts into chunks, summarizes each, then combines into a final bullet-point summary |
| ✅ **Action Item Extraction** | Identifies tasks, owners, and deadlines from the conversation |
| 🔑 **Key Decision Extraction** | Pulls out all decisions agreed upon during the meeting |
| ❓ **Open Question Detection** | Highlights unresolved questions and topics needing follow-up |
| 💬 **RAG-Powered Chat** | Ask natural-language questions about your meeting with suggested question chips — answers are grounded in the transcript via a LangChain LCEL + ChromaDB retrieval chain |
| 📥 **Export & Download** | Download meeting summary, full transcript, and all insights as `.txt` files |
| 📊 **Metrics Dashboard** | Real-time stats — processing time, word count, audio chunks, and action item count |
| 📚 **Session History** | Switch between previously analyzed meetings within the same session |
| 🎨 **Premium Interactive UI** | Custom dark-mode Streamlit interface with animated floating orbs, glassmorphism cards, tabbed dashboard, fade-in animations, typing indicators, and micro-interactions |

## Architecture

```
              ┌──────────────────────────┐
              │  YouTube URL / Upload /  │
              │  Local File Path         │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │     Audio Processor      │  yt-dlp + pydub + FFmpeg
              │  (download / save,       │  Convert → WAV (16kHz mono)
              │   convert, chunk)        │  Chunk → 10-min segments
              └────────────┬─────────────┘
                           │
            ┌──────────────┼──────────────┐
            │ English      │              │ Hinglish
   ┌────────▼────────┐           ┌────────▼────────┐
   │  OpenAI Whisper  │           │   Sarvam AI     │
   │  (local model)   │           │ (STT + Translate)│
   └────────┬────────┘           └────────┬────────┘
            └──────────────┬──────────────┘
                           │
              ┌────────────▼─────────────┐
              │     Full Transcript      │
              └────────────┬─────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐   ┌───────▼───────┐   ┌───────▼───────┐
│ Summarizer  │   │  Extractor    │   │  RAG Engine   │
│ (Map-Reduce)│   │  (Actions,    │   │  (ChromaDB +  │
│             │   │   Decisions,  │   │   LangChain   │
│ Mistral LLM │   │   Questions)  │   │   LCEL Chain) │
└──────┬──────┘   └───────┬───────┘   └───────┬───────┘
       │                  │                   │
       └──────────────────┼───────────────────┘
                          │
              ┌───────────▼────────────┐
              │   Streamlit UI         │
              │   ┌──────────────────┐ │
              │   │ Tabbed Dashboard │ │
              │   │ 📋 Summary      │ │
              │   │ 📝 Transcript   │ │
              │   │ ✅ Insights     │ │
              │   │ 💬 RAG Chat     │ │
              │   └──────────────────┘ │
              └────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit with custom CSS (dark mode, animated orbs, glassmorphism, tabs) |
| **Speech-to-Text** | OpenAI Whisper (local) · Sarvam AI (cloud, Hinglish) |
| **LLM** | Mistral AI (`mistral-small-latest`) via LangChain |
| **RAG Pipeline** | LangChain LCEL · ChromaDB · HuggingFace Embeddings (`all-MiniLM-L6-v2`) |
| **Audio Processing** | yt-dlp · pydub · FFmpeg |
| **Language** | Python 3.10+ |

## Getting Started

### Prerequisites

- **Python** ≥ 3.10
- **FFmpeg** installed and available on your system PATH ([download](https://ffmpeg.org/download.html))
- API keys for:
  - [Mistral AI](https://console.mistral.ai/) — required for summarization, extraction, and RAG chat
  - [Sarvam AI](https://www.sarvam.ai/) — optional, only needed for Hinglish transcription

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/RAG-based-AI-Video-Assistant.git
   cd RAG-based-AI-Video-Assistant
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r Requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   MISTRAL_API_KEY=your_mistral_api_key_here
   SARVAM_API_KEY=your_sarvam_api_key_here   # optional — only for Hinglish
   WHISPER_MODEL=small                        # optional — tiny, base, small, medium, large
   ```

### Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Usage

1. **Choose input method** — Toggle between two modes in the sidebar:
   - 🔗 **YouTube URL / Path** — Paste a YouTube URL or type a local file path
   - 📁 **Upload File** — Drag-and-drop or browse for audio/video files (`.mp4`, `.mp3`, `.wav`, `.m4a`, `.webm`, `.ogg`, `.flac`, `.mkv`, `.avi`)
2. **Select language** — Choose `english` (uses Whisper locally) or `hinglish` (uses Sarvam AI cloud API).
3. **Click ⚡ Analyse** — The pipeline runs through 6 stages with animated progress tracking in the sidebar:
   - 🔊 Audio Processing
   - 📝 Transcription
   - 🏷️ Title Generation
   - 📋 Summarization
   - 🔍 Extraction (action items, decisions, questions)
   - 🧠 RAG Engine setup
4. **Review results** — Browse the tabbed dashboard:
   - **📋 Summary** — Auto-generated meeting summary with download button
   - **📝 Transcript** — Full transcript with word count and download button
   - **✅ Insights** — Action items, key decisions, and open questions with combined download
   - **💬 Chat** — Ask questions about the meeting with suggested starter questions
5. **Check metrics** — View processing time, word count, audio chunks, and action item count in the metrics ribbon.
6. **Switch sessions** — Use the session history in the sidebar to revisit previous analyses.

## Project Structure

```
RAG-based-AI-Video-Assistant/
│
├── app.py                     # Streamlit UI — main entry point
├── main.py                    # CLI / alternative entry point
├── test.py                    # Test script
├── Requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
│
├── core/                      # Core AI pipeline modules
│   ├── transcriber.py         # Whisper + Sarvam AI transcription
│   ├── summarizer.py          # Map-reduce summarization (Mistral)
│   ├── extractor.py           # Action items, decisions, questions
│   ├── rag_engine.py          # LangChain LCEL RAG chain
│   └── vector_store.py        # ChromaDB vector store management
│
├── utils/                     # Utility modules
│   └── audio_processor.py     # YouTube download, WAV conversion, chunking
│
├── downloades/                # Downloaded & uploaded audio files (auto-created)
└── vector_db/                 # ChromaDB persistent storage (auto-created)
```

## UI Highlights

| Element | Details |
|---|---|
| 🌀 **Animated Background** | Floating gradient orbs (purple, cyan, pink) with CSS keyframe drift animations |
| 📑 **Tabbed Dashboard** | 4-tab layout — Summary, Transcript, Insights, Chat — with gradient active-tab styling |
| ⚡ **Pipeline Progress** | Step-by-step animated cards with elapsed time per step, pulsing glow on active step |
| 💬 **Smart Chat** | Fade-in messages with timestamps, 6 clickable suggested question chips, styled user/bot bubbles |
| 📊 **Metrics Ribbon** | 4 animated stat cards with hover lift effects |
| 📥 **Export** | Download summary, transcript, and insights as `.txt` directly from tabs |
| 📚 **Session History** | Sidebar list of past analyses with one-click switching |
| ✨ **Micro-interactions** | Card hover lifts, button press scales, toast notifications, floating empty-state animation |

## How It Works

### Transcription

- **English**: Uses [OpenAI Whisper](https://github.com/openai/whisper) running locally. The model size is configurable via the `WHISPER_MODEL` env variable (`tiny`, `base`, `small`, `medium`, `large`).
- **Hinglish**: Uses [Sarvam AI](https://www.sarvam.ai/) STT-Translate API which simultaneously transcribes Hindi/Hinglish audio and translates to English. Audio is split into ≤25-second segments to comply with the API's 30-second limit.

### Summarization

Uses a **map-reduce** approach with Mistral AI:
1. **Map** — The transcript is split into 3000-character chunks, and each chunk is summarized independently.
2. **Reduce** — All partial summaries are combined into one final, cohesive bullet-point summary.

### RAG Chat

1. The transcript is split into 500-character chunks with 50-character overlap.
2. Each chunk is embedded using `all-MiniLM-L6-v2` (via HuggingFace / Sentence Transformers).
3. Embeddings are stored in a **ChromaDB** vector store.
4. At query time, the top-4 most similar chunks are retrieved and passed as context to **Mistral AI** through a LangChain LCEL pipeline.

## License

This project is open source. Feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using Streamlit, LangChain, Whisper, Mistral AI, and ChromaDB
</p>
