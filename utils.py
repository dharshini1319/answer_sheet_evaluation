import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    text = ""
    if extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif extension == '.pdf':
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    return text.strip()

def evaluate_similarity(student_text, correct_text):
    if not student_text or not correct_text:
        return 0, "Error: One of the files is empty."
    
    documents = [student_text, correct_text]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    score = round(similarity * 10, 2)
    
    if score > 8:
        feedback = "Excellent"
    elif score > 5:
        feedback = "Good"
    else:
        feedback = "Needs Improvement"
        
    return score, feedback
