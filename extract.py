import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import io
import os
import json
import re

def parse_questions(text):
    """
    Extracts all questions using numbered format like '1.', '2.', etc.
    Returns list of (question_number, question_text) tuples.
    """
    pattern = r'(\d{1,2}\.\s.*?)(?=\n\d{1,2}\.\s|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    return [q.strip() for q in matches]

def extract_images_from_page(page, page_number, output_dir):
    """
    Extracts and saves images from a PDF page.
    Returns a list of image file paths.
    """
    image_paths = []
    image_list = page.get_images(full=True)
    
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = page.parent.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image = Image.open(io.BytesIO(image_bytes))
        
        image_filename = f"page_{page_number + 1}_img_{img_index + 1}.{image_ext}"
        image_path = os.path.join(output_dir, image_filename)
        image.save(image_path)
        image_paths.append(image_path.replace("\\", "/"))

    return image_paths

def extract_from_pdf(pdf_path, output_folder):
    """
    Full PDF parsing logic: extracts all questions and nearby images.
    Saves results as JSON.
    """
    doc = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_path = os.path.join(output_folder, pdf_name)
    os.makedirs(pdf_output_path, exist_ok=True)

    all_questions = []
    all_images = []

    # Step 1: Extract all text and images
    for page_number, page in enumerate(doc):
        page_text = page.get_text()
        page_questions = parse_questions(page_text)
        image_paths = extract_images_from_page(page, page_number, pdf_output_path)

        for q in page_questions:
            all_questions.append({
                "question": q,
                "images": None,          # Will assign below
                "option_images": []
            })
        all_images.extend(image_paths)

    # Step 2: Associate images to questions (1 main + rest as options)
    q_count = len(all_questions)
    for i in range(min(q_count, len(all_images))):
        all_questions[i]["images"] = all_images[i]
    
    # Step 3: Save as JSON
    json_path = os.path.join(pdf_output_path, "questions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=4)

    print(f"Extracted {len(all_questions)} questions from {pdf_path}")
    print(f"→ Saved to: {json_path}")

def select_and_extract():
    """
    GUI handler: lets user pick PDFs and output folder.
    """
    files = filedialog.askopenfilenames(
        title="Select PDF Files", filetypes=[("PDF files", "*.pdf")]
    )
    if not files:
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    for file in files:
        try:
            extract_from_pdf(file, output_folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract from {file}:\n{str(e)}")

    messagebox.showinfo("Done", " All questions and images extracted successfully!")

# ----------------- GUI Layout ----------------- #

root = tk.Tk()
root.title("PDF Question Extractor with JSON")
root.geometry("460x250")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(pady=50)

label = tk.Label(
    frame,
    text=" Extract all questions and images from PDFs",
    font=("Arial", 12)
)
label.pack(pady=10)

button = tk.Button(
    frame,
    text="📂 Select PDFs & Extract",
    command=select_and_extract,
    font=("Arial", 12),
    bg="blue",
    fg="white",
    padx=20,
    pady=6
)
button.pack(pady=10)

root.mainloop()
