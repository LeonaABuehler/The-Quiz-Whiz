import time
import os
import uuid
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer
from fpdf import FPDF
import gradio as gr

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
openai.api_key = os.environ["OPENAI_API_KEY"]

# Load LLM
llm = OpenAI(model="gpt-4o")

# Global chat engine
chat_engine = None

class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

def upload_file(files):
    global chat_engine
    file_paths = [file.name for file in files]

    # Upload documents
    data = SimpleDirectoryReader(input_files=file_paths).load_data()
    index = VectorStoreIndex.from_documents(data)

    # Initialize memory and chat engine
    memory = ChatMemoryBuffer.from_defaults(token_limit=5000)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt=(
        "You are the Quiz Whiz, a document scanner that takes documents and turns them into quizzes based on the content. "
        "Generate different types of questions including multiple-choice, true/false, short answer, and essay. "
        "The answer key should be at the end of the quiz. No additional messages should be included in the output. "
        "Make sure the question types are completely random in the quiz. "
        "In the PDF, make sure to not have '?' instead of apostrophes!!!"
        "No additional messages should be included in the output."
        "The quiz will have the difficulty levels: Easy, Medium, Hard and whichever is selected by the user will be used"
        )
    )
    return f"{len(file_paths)} file(s) uploaded. Ready to generate quiz!"

def chat_with_ai(question_types, difficulty_levels, num_questions):
    if chat_engine is None:
        return "Please upload a document first."

    selected_types = ", ".join(question_types) if question_types else "any"
    difficulties = ", ".join(difficulty_levels) if difficulty_levels else "any"
    message = f"Generate a quiz with {num_questions} questions. Question types: {selected_types}. Difficulty levels: {difficulties}"

    response = chat_engine.chat(message)
    quiz_text = response.response

    questions, answers = [], []
    if "Answer Key:" in quiz_text:
        question_part, answer_part = quiz_text.split("Answer Key:", 1)
        questions = question_part.strip().split("\n")
        answers = answer_part.strip().split("\n")
    else:
        questions = quiz_text.strip().split("\n")

    return "\n".join(questions) + "\n\nAnswer Key:\n" + "\n".join(answers)

def generate_pdf(text, title):
    import re

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Handle optional pdf title and use it as filename 
    if title.strip():
        # Clean title to be safe as a filename
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title.strip())
        filename = f"{safe_title}.pdf"
        # Set title in the document
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(190, 10, safe_title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        pdf.ln(10)
    else:
        filename = "output.pdf"

    # Remove unwanted characters such as *, #, -, and _
    pdf.set_font("Arial", size=12)
    text = text.replace("*", "").replace("#", "").replace("-", "").replace("_", ""), 
    
    # Split into questions and answers
    parts = text.split("\n")
    questions, answers = [], []
    is_answer_section = False

    for line in parts:
        if line.strip().lower().startswith("answer key"):
            is_answer_section = True
            continue
        if is_answer_section:
            answers.append(line.strip())
        else:
            questions.append(line.strip())

    # Add questions
    for question in questions:
        if question:
            if pdf.get_y() + 20 > 270:
                pdf.add_page()
            pdf.multi_cell(0, 10, question.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(5)

    # Add answers
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(190, 10, "Answer Key:", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for answer in answers:
        if answer:
            if pdf.get_y() + 20 > 270:
                pdf.add_page()
            pdf.multi_cell(0, 10, answer.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(5)

    # Save the PDF with either title-based or fallback name
    pdf.output(filename, "F")
    return filename

# Gradio UI
with gr.Blocks(title="The Quiz Whiz", theme=gr.themes.Soft(primary_hue="amber", neutral_hue="gray")) as demo:
    gr.HTML("""
    <head>
        <title>The Quiz Whiz</title>
        <meta name="description" content="LeonaGPT - AI Chatbot for document analysis">
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            html, body, .gradio-container {
                background-color: #FAF3E0 !important;
                color: #4CAF50 !important;
                font-family: 'Nunito', sans-serif !important;
                min-height: 200vh!important;
                margin: 0;
                padding: 0;
            }
            h1 {
                color: #212121 !important;
                text-align: center !important;
                font-weight: bold !important;
                font-size: 36px !important;
            }
            .content{
                text-align: center;
                font-size: 24px;
                margin-top: 20px; 
            }
        </style>
    </head>
    <body>
        <h1>The Quiz Whiz</h1>
        <div class="content">Upload your PDF(s) and generate quizzes instantly!</div>
    </body>
    """)

    gr.Image("LOGO-Picsart-BackgroundRemover.jpg", interactive=False, show_label=False, height=80)

    file_input = gr.File(label="Upload PDF(s)", file_types=[".pdf"], file_count="multiple")
    file_output = gr.Textbox(label="Uploaded File Info")

    question_types = gr.CheckboxGroup(
        choices=["Multiple Choice", "True/False", "Short Answer"],
        label="Select Question Types"
    )
    difficulty_levels = gr.Radio(
        choices=["Easy", "Medium", "Hard"],
        label="Select Difficulty Level"
    )

    num_questions = gr.Slider(
        minimum=1, maximum=50, step=1, value=10,
        label="Number of Questions"
    )

    generate_button = gr.Button("Generate Quiz")
    chat_output = gr.Textbox(label="AI Generated Quiz with Answer Key", lines=15)
    pdf_title = gr.Textbox(label="Optional PDF Title")
    generate_pdf_button = gr.Button("Generate PDF")
    pdf_download = gr.File(label="Download Quiz as PDF")

    file_input.change(upload_file, file_input, file_output)
    generate_button.click(chat_with_ai, inputs=[question_types, difficulty_levels, num_questions], outputs=chat_output)
    generate_pdf_button.click(generate_pdf, inputs=[chat_output, pdf_title], outputs=pdf_download)

demo.launch(share=True, favicon_path="Light_processed.ico")
