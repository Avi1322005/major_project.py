import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import pipeline
from fpdf import FPDF
import pyttsx3
import threading
import speech_recognition as sr

# Initialize summarizer
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Text-to-Speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Global recognizer
recognizer = sr.Recognizer()

class TextSummarizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("🧠 AI Text Summarizer")
        self.master.geometry("850x720")

        self.theme = "light"
        self.speaking = False
        self.listening_thread = None
        self.stop_listening_function = None

        self._define_themes()
        self._create_widgets()
        self._apply_theme()

    def _define_themes(self):
        self.light_theme = {
            "bg": "#e3f2fd",
            "text_bg": "#ffffff",
            "text_fg": "#000000",
            "btn_bg": "#2196F3",
            "btn_fg": "#ffffff",
            "btn_active": "#1976D2",
            "label_fg": "#0D47A1"
        }

        self.dark_theme = {
            "bg": "#1e1e1e",
            "text_bg": "#2e2e2e",
            "text_fg": "#ffffff",
            "btn_bg": "#424242",
            "btn_fg": "#ffffff",
            "btn_active": "#616161",
            "label_fg": "#90caf9"
        }

    def _create_widgets(self):
        self.title_label = tk.Label(self.master, text="AI Text Summarizer", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        # Input
        self.input_label = tk.Label(self.master, text="Enter text to summarize:", font=("Helvetica", 13))
        self.input_label.pack(pady=5)
        self.input_text = tk.Text(self.master, height=10, width=95, wrap=tk.WORD, font=("Helvetica", 11))
        self.input_text.pack(padx=20, pady=5)

        # Buttons: Row 1 (Main actions)
        btn_frame1 = tk.Frame(self.master)
        btn_frame1.pack(pady=6)

        self.buttons = []
        self._add_button(btn_frame1, "🔍 Summarize", self.summarize_text)
        self._add_button(btn_frame1, "🔊 Listen Summary", self.toggle_speech)
        self._add_button(btn_frame1, "📄 Export as PDF", self.export_as_pdf)
        self._add_button(btn_frame1, "🧹 Clear", self.clear_text)

        # Buttons: Row 2 (Voice + Theme)
        btn_frame2 = tk.Frame(self.master)
        btn_frame2.pack(pady=6)

        self._add_button(btn_frame2, "🎙 Start Voice Input", self.start_listening)
        self._add_button(btn_frame2, "🛑 Stop Voice Input", self.stop_listening)
        self._add_button(btn_frame2, "🌓 Toggle Theme", self.toggle_theme)

        # Output
        self.output_label = tk.Label(self.master, text="Summary:", font=("Helvetica", 13))
        self.output_label.pack(pady=5)
        self.output_text = tk.Text(self.master, height=10, width=95, wrap=tk.WORD, font=("Helvetica", 11))
        self.output_text.pack(padx=20, pady=5)

    def _add_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, font=("Helvetica", 11), padx=10, pady=6, relief="raised")
        btn.pack(side=tk.LEFT, padx=8, pady=4)
        self.buttons.append(btn)

    def _apply_theme(self):
        theme = self.dark_theme if self.theme == "dark" else self.light_theme

        self.master.configure(bg=theme["bg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["label_fg"])
        self.input_label.configure(bg=theme["bg"], fg=theme["label_fg"])
        self.output_label.configure(bg=theme["bg"], fg=theme["label_fg"])

        self.input_text.configure(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])
        self.output_text.configure(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])

        for btn in self.buttons:
            btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_active"])

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()

    def summarize_text(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("No Input", "Please enter or speak some text.")
            return
        try:
            self.output_text.delete("1.0", tk.END)
            result = summarizer("summarize: " + input_text, max_length=130, min_length=30, do_sample=False)
            summary = result[0]['summary_text']
            self.output_text.insert(tk.END, summary)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}")

    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

    def toggle_speech(self):
        if self.speaking:
            engine.stop()
            self.speaking = False
            return

        summary = self.output_text.get("1.0", tk.END).strip()
        if not summary:
            return

        self.speaking = True

        def speak():
            try:
                engine.say(summary)
                engine.runAndWait()
            except Exception as e:
                print("TTS Error:", e)
            finally:
                self.speaking = False

        threading.Thread(target=speak, daemon=True).start()

    def export_as_pdf(self):
        summary = self.output_text.get("1.0", tk.END).strip()
        if not summary:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, summary)
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf.output(file_path)

    def start_listening(self):
        if self.listening_thread and self.listening_thread.is_alive():
            messagebox.showinfo("Already Listening", "Speech recognition is already running.")
            return

        def listen_continuously():
            messagebox.showinfo("Voice Input", "🎙 Listening started... Speak now")
            try:
                mic = sr.Microphone()
                self.stop_listening_function = recognizer.listen_in_background(mic, self.callback)
            except Exception as e:
                messagebox.showerror("Microphone Error", f"Could not start microphone: {e}")

        self.listening_thread = threading.Thread(target=listen_continuously, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):
        if self.stop_listening_function:
            self.stop_listening_function(wait_for_stop=False)
            self.stop_listening_function = None
            messagebox.showinfo("Voice Input", "🛑 Listening stopped.")
        else:
            messagebox.showinfo("Not Listening", "Speech recognition is not running.")

    def callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            self.input_text.insert(tk.END, text + " ")
        except sr.UnknownValueError:
            self.input_text.insert(tk.END, "\n[Could not understand]\n")
        except sr.RequestError:
            self.input_text.insert(tk.END, "\n[Recognition Error]\n")


# ---------------- Run App ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TextSummarizerApp(root)
    root.mainloop()
