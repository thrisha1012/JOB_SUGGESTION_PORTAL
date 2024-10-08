from flask import Flask, session, request, redirect, url_for, render_template, jsonify, send_from_directory ,abort
import smtplib
from email.message import EmailMessage
import pandas as pd
import re
import mysql.connector
import os
import time
import requests
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from werkzeug.utils import secure_filename
from email.mime.application import MIMEApplication



app = Flask(__name__)
app.secret_key = 'hack'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from email.mime.base import MIMEBase
from email import encoders

@app.route('/send_application_email', methods=['POST'])
def send_application_email():
    gmail_user = 'thrishas.22cse@kongu.edu'
    app_password = 'gaee wdpf nxgf qmec'

    # Retrieve email from session
    email = session.get('email')

    if not email:
        return jsonify({'error': 'Email not found in session.'}), 400

    # Initialize message variable
    message = MIMEMultipart()

    try:
        # Get user's data from the database
        user, user_jobs = get_user_by_email(email)

        if user is None:
            return jsonify({'error': 'User not found.'}), 404

        # Email content
        sender = gmail_user
        receiver = 'thrishla1012@gmail.com'
        subject = 'Test Email'
        body = f'''
        This is a test email sent from Python.

        User Details:
        Name: {user[1]}
        Email: {user[2]}
        Contact Number: {user[4]}
        Address: {user[5]}
        City: {user[6]}
        Zipcode: {user[7]}
        Job Title: {user[8]}
        Industry: {user[9]}
        Experience: {user[10]}
        Education: {user[11]}
        Skills: {user[12]}
        Employment Type: {user[13]}
        Salary Range: {user[14]}
        Resume: {user[15]}
        
        Saved Jobs:
        {user_jobs}
        '''
        
        # Set headers
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = subject

        # Attach the email body
        message.attach(MIMEText(body, 'plain'))

        # Attach resume file
        resume_path = user[15]  # Assuming the resume path is stored in the database
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(resume_path)}')
            message.attach(part)

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to your Gmail account using the app password
        server.login(gmail_user, app_password)

        # Send the email
        server.sendmail(sender, receiver, message.as_string())

        # Close the connection
        server.quit()
        return jsonify({'message': 'Email sent successfully!'}), 200
    except Exception as e:
        print(e)
        error_message = f"Failed to send email. Error: {e}"
        return jsonify({'error': error_message}), 500


def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='thrisha1012',
            database='hackbuzz'
        )
        print("Database connected successfully")
        return conn
    except Exception as e:
        print("Error connecting to database:", str(e))
        raise

# Load the dataset
try:
    data = pd.read_csv('naukri_com-job_sample.csv')  # Replace 'naukri_com-job_sample.csv' with the actual filename
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: Dataset file not found.")
    data = None

# Columns to exclude
columns_to_exclude = ['jobid', 'payrate', 'numberofpositions', 'site_name', 'postdate', 'uniq_id']

upload_folder = 'D:\\projects\\job_portal\\job_suggestions\\uploads'


@app.route('/view_resume/<filename>')
def view_resume(filename):
    try:
        # Check if the file exists in the uploads directory
        if os.path.exists(os.path.join(upload_folder, filename)):
            return send_from_directory(upload_folder, filename, as_attachment=True)
        else:
            abort(404)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        abort(500)

@app.route('/get_user_details')
def get_user_details():
    # Assuming you have the user's email stored in a variable
    email = session.get('email')
    user, user_jobs = get_user_by_email(email)
    return jsonify({'user': user, 'user_jobs': user_jobs})



def get_user_by_email(email):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.execute("SELECT * FROM job WHERE mail = %s", (email,))
        user_jobs = cur.fetchall()
        print("Fetched user:", user)  # Print fetched user data
        return user, user_jobs
    except Exception as e:
        print("Error fetching user:", e)
        return None, None
    finally:
        if conn is not None:
            conn.close()

# Function to remove specific lines from jobdescription column
def remove_specific_lines(description):
    if isinstance(description, str):
        description = re.sub(r'Download PPT Photo 1\s+View Contact Details', '', description)
        description = re.sub(r'Job Description\s+Send me Jobs like this', '', description)
    return description



def add_user(fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path))
        conn.commit()
        print("Data inserted successfully")
    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()
    finally:
        conn.close()


@app.route('/save_job_details', methods=['POST'])
def save_job_details():
    if request.method == 'POST':
        data = request.json
        job_title = data.get('jobTitle')
        company_name = data.get('companyName')
        email = session.get('email')
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO job (mail, company_name, job_title)
                VALUES (%s, %s, %s)
            """, (email, company_name, job_title))
            conn.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            print("Error inserting job details:", e)
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            conn.close()



@app.route("/success")
def success():
    # Retrieve user details from query parameters
    user_name = request.args.get("user_name")
    email = request.args.get("email")
    
    # Display a success message along with user details
    return f"<h1>Application submitted successfully</h1><p>Thank you, {user_name}, your application has been submitted. An email confirmation has been sent to {email}.</p>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        contact_number = request.form.get("contact_number")
        address = request.form.get("address")
        city = request.form.get("city")
        zipcode = request.form.get("zipcode")
        job_title = request.form.get("job_title")
        industry = request.form.get("industry")
        experience = request.form.get("experience")
        education = request.form.get("education")
        skills = request.form.get("skills")
        employment_type = request.form.get("employment_type")
        salary_range = request.form.get("salary_range")
        print("Received Files:", request.files)  # Debug print to check received files

        resume_file = request.files.get("resume")
        print("Received Resume File:", resume_file)  # Debug print to check the received resume file
        
        resume_path = save_resume(resume_file)
        print("Saved Resume Path:", resume_path)
        if None in [fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range] or not resume_path:
            error_message = "One or more required fields are missing."
            return render_template("register.html", error=error_message)

        add_user(fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path)
        return redirect(url_for("index")) 

    return render_template("register.html")

@app.route('/modify_profile', methods=['POST'])
def modify_profile():
    if request.method == 'POST':
        email = session.get('email')
        fullname = request.form['fullname']
        password = request.form['password']
        contact_number = request.form['contact_number']
        address = request.form['address']
        city = request.form['city']
        zipcode = request.form['zipcode']
        job_title = request.form['job_title']
        industry = request.form['industry']
        experience = request.form['experience']
        education = request.form['education']
        skills = request.form['skills']
        employment_type = request.form['employment_type']
        salary_range = request.form['salary_range']
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume.filename != '':
                filename = secure_filename(resume.filename)
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume.save(resume_path)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET fullname=%s, password=%s, contact_number=%s, address=%s, city=%s, zipcode=%s, 
                job_title=%s, industry=%s, experience=%s, education=%s, skills=%s, 
                employment_type=%s, salary_range=%s ,resume_path=%s
            WHERE email=%s
        """, (fullname, password, contact_number, address, city, zipcode, 
              job_title, industry, experience, education, skills, 
              employment_type, salary_range,filename, email))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reg")
def reg():
    return render_template("register.html")

@app.route("/modify")
def modify():
    email = session.get('email')
    user = get_user_by_email(email)
    if user:
        return render_template("modify.html", user=user)
    else:
        return redirect(url_for("index"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user, user_jobs = get_user_by_email(email)
        if user and user[3] == password:  # Check if the user exists and the password matches
            session["email"] = user[2]  # Store the email in the session
            session["password"] = user[3]  # Store the password in the session
            return redirect(url_for("user"))  # Redirect to the user page

        else:
            error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)



@app.route("/user")
def user():
    email = session.get('email')
    print("Session email:", email)  # Print session email

    user, user_jobs = get_user_by_email(email)
    print("Fetched user:", user)  # Print fetched user data

    if user:
        # Fetch user's skills from the database
        skills = user[12]  # Assuming skills are stored in the 13th column

        # Convert skills to a list of lowercase words
        skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []
        print("User's skills:", skills_list)

        company_details = []
        job_limit = 9  # Set the limit for job suggestions
        suggestion_count = 0  # Counter to keep track of the number of suggestions added

        for skill in skills_list:
            # Define a regular expression pattern to match the current skill
            skill_pattern = re.escape(skill)

            # Filter job postings based on the current skill
            filtered_data = data[data['jobtitle'].str.contains(skill_pattern, case=False, regex=True)]

            # Convert filtered data to a list of dictionaries for rendering in the template
            for index, row in filtered_data.iterrows():
                if suggestion_count < job_limit:
                    company_details.append({
                        "company": row["company"],
                        "jobtitle": row["jobtitle"],
                        "experience": row["experience"],
                        "joblocation_address": row["joblocation_address"],
                        "jobdescription": row["jobdescription"]
                    })
                    suggestion_count += 1
                else:
                    break  # Break out of the loop if the job limit is reached

        print("Recommendations based on user's skills:", company_details)

        return render_template("user.html", user=user, user_jobs=user_jobs, company_details=company_details)
    else:
        return redirect(url_for("index"))



@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        location = request.form.get("location")
        skills = request.form.get("skills")
        experience = request.form.get("experience")

        print(f"Search parameters: Location={location}, Skills={skills}, Experience={experience}")  # Debug print

        if not (location or skills or experience):
            print("No search parameters provided.")
            return render_template("index.html", error="No search parameters provided.")

        try:
            filtered_data = data.copy()

            if location:
                filtered_data = filtered_data[filtered_data["joblocation_address"].str.lower() == location.lower()]

            if experience:
                experience = experience.replace(" ", "").replace("yrs", "").replace("years", "")
                filtered_data = filtered_data[filtered_data["experience"].str.replace(" ", "").str.contains(experience)]

            if skills:
                skill_words = set(skills.lower().split())
                filtered_data = filtered_data[(filtered_data["jobtitle"].str.lower().str.contains(r"\b" + re.escape(skills.lower()) + r"\b")) |
                                              (filtered_data["jobdescription"].str.lower().str.contains(r"\b" + re.escape(skills.lower()) + r"\b"))]

            company_details = filtered_data[["company", "jobtitle", "experience", "joblocation_address", "jobdescription"]].to_dict(orient="records")

            print("Company details:", company_details)  # Debug print

            return render_template("search_results.html", search_results=company_details)

        except Exception as e:
            print(f"Error filtering dataset: {str(e)}")
            return render_template("index.html", error=f"Error filtering dataset: {str(e)}")

    else:
        return render_template("index.html", error="Invalid request method.")

@app.route("/get_company_url", methods=["POST"])

def get_company_url():
   
    company_name = request.json.get("company_name")

    company_url = scrape_company_url(company_name)

    return jsonify(company_url=company_url)


def scrape_company_url(company_name):

    driver = webdriver.Chrome()
    try:
        driver.get("https://www.google.com/")
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(company_name + Keys.RETURN)
        time.sleep(2)

        search_result = driver.find_element(By.CSS_SELECTOR, 'div.tF2Cxc a')
        company_url = search_result.get_attribute('href')
        print(f"Company: {company_name}, URL: {company_url}")

    except Exception as e:
        print(f"Error finding URL for {company_name}: {e}")
        company_url = None

    driver.quit()
    return company_url



if __name__ == "__main__":
    app.run(debug=True)
