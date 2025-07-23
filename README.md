# 🧠 PDF Question Extractor with OCR & GUI

This Python tool extracts **multiple questions** per page from PDFs using **OCR** and generates a clean JSON output with text, questions, and associated images. Includes a **Tkinter-based GUI** for user-friendly file selection.

---

## 📦 Features

- 🖼️ Converts PDF pages to images using `pdf2image`
- 🔍 Uses `pytesseract` OCR to detect question text (e.g., Q1, Q2, etc.)
- 🧠 Groups questions with associated images (main + options)
- 📂 Outputs structured `questions.json` with paths and data
- 💻 GUI-based batch extractor using Tkinter
- ✅ Works on multi-question-per-page exams, mock tests, etc.

---

## ⚙️ Setup Instructions

### 

```bash
git clone https://github.com/Sriramdayal/Pdf_extractor.git
cd Pdf_extractor
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
pip install pdf2image pytesseract opencv-python pillow
python3 extract.py  