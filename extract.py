import fitz  # PyMuPDF for working with PDFs
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import io
import os
import json

def extract_from_pdf(pdf_path, output_folder):
    """
    Extracts text and images from a PDF file.
    Saves text as .txt and images as .png/.jpg.
    Creates a JSON mapping of questions and images.
    """
    doc = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_folder, pdf_name)

    os.makedirs(output_path, exist_ok=True)

    full_text = ""
    questions = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        page_text = page.get_text().strip()
        full_text += page_text + "\n"

        # Save raw text of each page
        text_filename = f"page_{page_number + 1}.txt"
        with open(os.path.join(output_path, text_filename), "w", encoding="utf-8") as f:
            f.write(page_text)

        # Extract and save images from the page
        images = []
        for index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            image_info = doc.extract_image(xref)
            image_data = image_info["image"]
            image_ext = image_info["ext"]
            image = Image.open(io.BytesIO(image_data))

            image_filename = f"page_{page_number + 1}_img_{index + 1}.{image_ext}"
            image_path = os.path.join(output_path, image_filename)
            image.save(image_path)
            images.append(image_path.replace("\\", "/"))  # Normalize path

        # Build question entry for JSON if images are found
        if images:
            question_entry = {
                "question": page_text.split("\n")[0] if page_text else "No question text found.",
                "images": images[0],               # First image = main question image
                "option_images": images[1:]        # Remaining images = options
            }
            questions.append(question_entry)

    # Save full document text
    with open(os.path.join(output_path, "full_text.txt"), "w", encoding="utf-8") as f:
        f.write(full_text)

    # Save all question data to a JSON file
    with open(os.path.join(output_path, "questions.json"), "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)

    print(f"Done extracting: {pdf_path}")
    print(f"→ Output saved in: {output_path}")

def select_and_extract():
    """
    Opens file dialog to select PDFs and destination folder,
    then runs extraction for each selected file.
    """
    files = filedialog.askopenfilenames(
        title="Select PDF Files",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not files:
        return  # User cancelled

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    for file in files:
        try:
            extract_from_pdf(file, output_folder)
        except Exception as e:
            messagebox.showerror("Extraction Failed", f"Error with {file}:\n{e}")
            continue

    messagebox.showinfo("Success", "✅ All PDFs processed and extracted.")

#  GUI Setup

# Create window
root = tk.Tk()
root.title("PDF Text & Image Extractor + JSON Generator")
root.geometry("460x250")
root.resizable(False, False)

# Create main frame and label
frame = tk.Frame(root)
frame.pack(pady=50)

label = tk.Label(
    frame,
    text=" Select PDFs to extract questions, text, and images",
    font=("Arial", 12)
)
label.pack(pady=10)

# Create button to launch file selection
button = tk.Button(
    frame,
    text="📂 Select PDFs & Start Extraction",
    command=select_and_extract,
    font=("Arial", 12),
    bg="blue",
    fg="white",
    padx=20,
    pady=6
)
button.pack(pady=10)

# Run the GUI loop
root.mainloop()
