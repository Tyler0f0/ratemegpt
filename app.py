import openai
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
import docx

app = Flask(__name__)
openai.api_key = "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"


def rate_writing(text):
    prompt = f"Please rate the following text out of 100 and provide a thorough evaluation:\n\nText: {text}\n\nRating:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip() # type: ignore

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rate', methods=['POST'])
def rate():
    if 'text' in request.form:
        text = request.form['text']
    elif 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename) # type: ignore
        file_ext = filename.split('.')[-1]

        if file_ext == 'txt':
            text = file.read().decode('utf-8')
        elif file_ext == 'pdf':
            text = read_pdf(file)
        elif file_ext == 'docx':
            text = read_docx(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
    else:
        return jsonify({'error': 'No text or file provided'}), 400

    rating = rate_writing(text)
    return jsonify({'rating': rating})

def read_pdf(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page_num in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page_num).extractText()
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

if __name__ == '__main__':
    app.run(debug=True)
