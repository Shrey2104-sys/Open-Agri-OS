import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import agri_data
import ai_vision

# --- Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'open-agri-os-secret-key-change-in-prod' # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# --- Login Manager ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes: Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', mode='signup')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Routes: Main App ---
@app.route('/')
@login_required
def dashboard():
    return render_template('index.html', user=current_user)

# --- API Endpoints ---

@app.route('/api/scout_info', methods=['POST'])
@login_required
def scout_info():
    data = request.json
    place_name = data.get('place_name')
    
    if not place_name:
        return jsonify({'error': 'Place name required'}), 400
        
    coords = agri_data.get_coordinates(place_name)
    if not coords:
        return jsonify({'error': 'Location not found'}), 404
        
    lat, lon = coords
    rec = agri_data.get_crop_recommendation(lat, lon)
    weather = agri_data.get_weather(lat, lon)
    ndvi = agri_data.get_sentinel_ndvi(coords)
    
    return jsonify({
        'coords': coords,
        'recommendation': rec,
        'weather': weather,
        'ndvi': ndvi
    })

@app.route('/api/predict_disease', methods=['POST'])
@login_required
def predict_disease():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        image = Image.open(filepath)
        result = ai_vision.analyze_image(image)
        
        return jsonify(result)

@app.route('/api/get_advice', methods=['POST'])
@login_required
def get_advice():
    data = request.json
    disease = data.get('disease')
    ndvi_status = data.get('ndvi', 'Unknown')
    
    advice = agri_data.get_gemini_advice(disease, ndvi_status)
    return jsonify(advice)

# --- Main ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create tables if not exist
    app.run(debug=True, port=5000)
