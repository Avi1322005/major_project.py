# 🧠 AI Text Summarizer (Tkinter GUI)

A powerful desktop GUI application for automatic text summarization, built with Python, HuggingFace Transformers, and Tkinter. Supports voice input, text-to-speech, theme toggling, and PDF export.

---

## 🚀 Features

- ✅ Summarize any input text using `t5-small` model from HuggingFace
- 🎙️ Accepts **voice input** (speech-to-text)
- 🔊 Read summaries aloud using **text-to-speech (TTS)**
- 🌓 Toggle between **Light** and **Dark** theme modes
- 📄 Export summarized content as **PDF**
- 🧹 Clear button to reset input/output
- 🔒 Error-handling with user-friendly alerts

---

## 🖥️ GUI Preview

| Light Mode                           | Dark Mode                            |
|-------------------------------------|--------------------------------------|
| ![Light Mode](assets/light_mode.png) | ![Dark Mode](assets/dark_mode.png)   |

> *Screenshots coming soon!*

---

## 📦 Requirements

Install dependencies using `pip`:

```bash
pip install transformers
pip install torch
pip install pyttsx3
pip install SpeechRecognition
pip install pyaudio
pip install fpdf
