from flask import Flask, render_template, request, redirect, session
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename
import os
import sqlite3
from utils.database import create_user, verify_user, log_result
from utils.preprocess import preprocess_image

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Load the machine learning model
model = load_model('model/autism_model.h5.h5')  # Ensure this path is correct


# Database connection function
def connect_db():
    return sqlite3.connect('users.db')  # Ensure the path to your database is correct


# Routes for web app functionality
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in
    return render_template('index.html')  # Render home page after login


@app.route('/detect', methods=['POST'])
def detect():
    if 'user' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    file = request.files['image']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('static/uploads', filename)
        file.save(filepath)

        # Preprocess and predict
        img_array = preprocess_image(filepath)
        prediction = model.predict(img_array)[0][0]
        result = 'Non Autistic' if prediction > 0.015 else 'Autistic'

        # Log result to database
        log_result(session['user_id'], filename, result)

        return render_template('index.html', img_path=filepath, result=result)  # Display the result
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Create the user in the database
        if create_user(name, email, password):
            return redirect('/login')  # Redirect to the login page if the user is created
        else:
            return 'User already exists!'  # If user already exists (unique email constraint)

    return render_template('signup.html')  # Render the signup page if GET request


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verify user credentials
        user = verify_user(email, password)
        if user:
            session['user'] = user[1]  # Store user name in session
            session['user_id'] = user[0]  # Store user id in session
            return redirect('/')  # Redirect to the homepage after successful login
        else:
            return 'Invalid credentials!'  # If user not found or incorrect password

    return render_template('login.html')  # Render the login page if GET request


@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    session.pop('user_id', None)  # Remove user ID from session
    return redirect('/')  # Redirect to the homepage after logout


@app.route('/home')
def home():
    # This route can be for displaying the main page of your app
    if session.get('user'):  # Check if user is logged in
        user_id = session.get('user_id')
        filename = "example.jpg"  # Example filename, update this with actual logic
        result = "Non Autistic"  # Example result, update this with actual logic
        log_result(user_id, filename, result)  # Log the result to the database
        return render_template('index.html', result=result, filename=filename)  # Display result page
    return render_template('home.html')  # Render the home page if not logged in


if __name__ == '__main__':
    app.run(debug=True)
