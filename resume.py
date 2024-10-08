import re
import spacy
import pdfplumber
import pandas as pd
from fuzzywuzzy import process

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def extract_skills_fuzzy(resume_text, skill_words):
    # Convert the resume text to lowercase for case-insensitive matching
    resume_text_lower = resume_text.lower()

    # Initialize a list to store extracted skills
    extracted_skills = []

    # Iterate over each skill word
    for skill_word in skill_words:
        # Use fuzzy matching to find approximate matches
        match, score = process.extractOne(skill_word.lower(), resume_text_lower)
        
        # If the score is above a certain threshold, consider it a match
        if score >= 80:
            extracted_skills.append(match)

    return extracted_skills

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load the dataset containing various skills
skills_dataset = pd.read_csv('skills.csv')

# Verify the contents of the skills dataset
print("Contents of skills dataset:")
print(skills_dataset)

# Extract skill words from the dataset
skill_words = skills_dataset['Example'].tolist()

print("Skill words extracted from the dataset:", skill_words)

# Path to the PDF resume
pdf_path = 'Myresume.pdf'

# Extract resume text from the PDF
resume_text = extract_text_from_pdf(pdf_path)
print("Resume text extracted from PDF:", resume_text)

# Extract skills using fuzzy matching
fuzzy_skills = extract_skills_fuzzy(resume_text, skill_words)
print("Skills extracted using fuzzy matching:", fuzzy_skills)
