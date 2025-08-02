import gradio as gr
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from fpdf import FPDF
from PyPDF2 import PdfReader

nltk.download("stopwords")
nltk.download("punkt")

def clean_text(text):
    return re.sub(r"[^\x00-\x7F]+", "", text)

def extract_sections_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    sections = {
        "Name": "",
        "Position": "",
        "Email": "",
        "Contact": "",
        "Education": "",
        "Skills": "",
        "Experience": "",
        "Projects": "",
        "Achievements": "",
        "Coding Profile": "",
    }
    current_section = None
    for line in text.splitlines():
        l = line.strip()
        for section in sections:
            if l.lower().startswith(section.lower()):
                current_section = section
                break
        else:
            if current_section:
                sections[current_section] += l + "\\n"
    return sections

def extract_keywords(job_description):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(job_description.lower())
    keywords = [w for w in words if w.isalpha() and w not in stop_words]
    relevant_skills = ["html","css","javascript","react","python","machine learning","data analysis"]
    return [s for s in relevant_skills if s in keywords]

def create_resume_pdf(sections, name, position, contact, email, job_keywords):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resume", ln=True, align="C")
    pdf.set_font("Arial", "B", 8)
    pdf.cell(0, 5, f"Name: {clean_text(name)}", ln=True)
    pdf.cell(0, 5, f"Position: {clean_text(position)}", ln=True)
    pdf.cell(0, 5, f"Contact: {clean_text(contact)}", ln=True)
    pdf.cell(0, 5, f"Email: {clean_text(email)}", ln=True)
    pdf.ln(3)
    for sec in ["Education","Skills","Experience","Projects","Achievements","Coding Profile"]:
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0,5,f"{sec}:", ln=True)
        pdf.set_font("Arial","",7)
        content = clean_text(sections.get(sec,""))
        if sec=="Skills" and job_keywords:
            content += "\\nRelevant Skills: " + ", ".join(job_keywords)
        if content.strip():
            pdf.multi_cell(0,4,content)
            pdf.ln(1)
    out = "generated_resume.pdf"
    pdf.output(out)
    return out

def process(uploaded_pdf, job_description, name, position, contact, email):
    if uploaded_pdf is not None:
        sections = extract_sections_from_pdf(uploaded_pdf.name)
    else:
        sections = {}
    job_keywords = extract_keywords(job_description or "")
    pdf_path = create_resume_pdf(sections, name or "N/A", position or "N/A", contact or "N/A", email or "N/A", job_keywords)
    return pdf_path

iface = gr.Interface(
    fn=process,
    inputs=[
        gr.File(label="Upload Existing Resume (PDF)"),
        gr.Textbox(lines=2, label="Job Description"),
        gr.Textbox(label="Name"),
        gr.Textbox(label="Position"),
        gr.Textbox(label="Contact"),
        gr.Textbox(label="Email"),
    ],
    outputs=gr.File(label="Generated Resume PDF"),
    title="Auto Resume Generator",
    description="Upload your resume and job description, get a tailored PDF resume."
)

if __name__ == "__main__":
    iface.launch()