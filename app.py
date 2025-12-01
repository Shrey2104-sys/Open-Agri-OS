import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from backend import ai_engine, data_engine

# --- Configuration ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'open-agri-os-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Enable CORS
CORS(app)

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
    return db.session.get(User, int(user_id))

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

# --- API Endpoints (Refactored) ---

@app.route('/api/scout', methods=['POST'])
@login_required
def scout():
    data = request.json
    location = data.get('place_name')
    result = data_engine.get_satellite_map(location)
    return jsonify(result)

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
        
        # Call Vision Engine
        result = ai_engine.predict_disease(filepath)
        return jsonify(result)

@app.route('/api/advice', methods=['POST'])
@login_required
def advice():
    data = request.json
    disease = data.get('disease')
    ndvi = data.get('ndvi', 'Unknown')
    
    # Call Data Engine
    result = data_engine.get_advice(disease, ndvi)
    return jsonify(result)

@app.route('/api/scout_info', methods=['POST'])
@login_required
def scout_info():
    data = request.json
    place_name = data.get('place_name')
    
    from geopy.geocoders import Nominatim
    
    try:
        geolocator = Nominatim(user_agent="open_agri_os_v5")
        location = geolocator.geocode(place_name)
        if location:
            coords = (location.latitude, location.longitude)
            
            # Mock Weather (Simulated for now, could be API later)
            weather = {
                "temp": 28,
                "condition": "Sunny",
                "humidity": 60,
                "forecast": "Good day."
            }
            
            # Dynamic AI Recommendation
            rec = data_engine.get_crop_recommendation(place_name, weather)
            
            # Map
            map_data = data_engine.get_satellite_map(place_name)
            
            return jsonify({
                'coords': coords,
                'recommendation': rec,
                'weather': weather,
                'ndvi': {'status': 'success', 'image_path': map_data.get('image_url')} 
            })
        return jsonify({'error': 'Location not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Geocoding error'}), 500

# --- Main ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')
