import os
import cv2
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from flask_wtf.csrf import CSRFProtect, generate_csrf
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import your custom engines
from chaos_engine.henon import encrypt_image, decrypt_image
from steganography.lsb import hide_image, extract_image

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Restrict uploads to 16MB

# --- SECURITY HARDENING ---
FERNET_KEY = os.environ.get('FERNET_KEY').encode('utf-8')
cipher_suite = Fernet(FERNET_KEY)
csrf = CSRFProtect(app) 

# Rate Limiter to prevent DDoS attacks
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']

@login_manager.user_loader
def load_user(user_id):
    users_collection = mongo.db.users
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users_collection = mongo.db.users
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({"username": username})
        
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user_obj = User(user_data)
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials. Access denied.")
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    users_collection = mongo.db.users
    username = request.form.get('username')
    password = request.form.get('password')
    
    if users_collection.find_one({"username": username}):
        return render_template('login.html', error="User already exists.")
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_collection.insert_one({"username": username, "password": hashed_password})
    return render_template('login.html', success="Registration complete. You may now authenticate.")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- MAIN APP ROUTES ---
@app.route('/')
@login_required
def index():
    # We pass a CSRF token to the frontend so JavaScript fetch requests are allowed
    return render_template('index.html', username=current_user.username, csrf_token=generate_csrf())

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Fetches and DECRYPTS the user's encryption history from MongoDB."""
    records = mongo.db.keys.find({"user_id": current_user.id}).sort("created_at", -1)
    history_list = []
    
    for r in records:
        try:
            # Decrypt the keys from the database before showing the user
            decrypted_x0 = cipher_suite.decrypt(r.get("x0")).decode('utf-8')
            decrypted_y0 = cipher_suite.decrypt(r.get("y0")).decode('utf-8')
        except Exception:
            # Fallback if old unencrypted data exists during testing
            decrypted_x0 = r.get("x0")
            decrypted_y0 = r.get("y0")

        history_list.append({
            "target_filename": r.get("target_filename", "Unknown File"),
            "x0": decrypted_x0,
            "y0": decrypted_y0,
            "date": r.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return jsonify(history_list)

@app.route('/api/encrypt', methods=['POST'])
@login_required
@limiter.limit("5 per minute") # Max 5 encryptions per minute per user
def api_encrypt():
    base_file = request.files.get('base_image')
    target_file = request.files.get('target_image')
    
    raw_x0 = request.form.get('x0', '0.1')
    raw_y0 = request.form.get('y0', '0.1')
    x0 = float(raw_x0)
    y0 = float(raw_y0)
    
    if not base_file or not target_file:
        return jsonify({'error': 'Missing images'}), 400

    base_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(base_file.filename))
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(target_file.filename))
    base_file.save(base_path)
    target_file.save(target_path)

    # ENCRYPT the keys before saving to MongoDB
    encrypted_x0 = cipher_suite.encrypt(raw_x0.encode('utf-8'))
    encrypted_y0 = cipher_suite.encrypt(raw_y0.encode('utf-8'))

    mongo.db.keys.insert_one({
        "user_id": current_user.id,
        "x0": encrypted_x0,
        "y0": encrypted_y0,
        "target_filename": target_file.filename,
        "created_at": datetime.utcnow()
    })

    # Process Images
    target_img = cv2.imread(target_path)
    encrypted_target = encrypt_image(target_img, x0, y0)
    
    try:
        stego_img = hide_image(base_path, encrypted_target)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    out_filename = f'stego_out_{current_user.id}_{int(datetime.utcnow().timestamp())}.png'
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
    cv2.imwrite(out_path, stego_img)
    
    return jsonify({'message': 'Success', 'output_url': url_for('static', filename='uploads/' + out_filename)})

@app.route('/api/decrypt', methods=['POST'])
@login_required
@limiter.limit("5 per minute") # Max 5 decryptions per minute per user
def api_decrypt():
    stego_file = request.files.get('stego_image')
    x0 = float(request.form.get('x0', 0.1))
    y0 = float(request.form.get('y0', 0.1))

    if not stego_file:
        return jsonify({'error': 'Missing image'}), 400

    stego_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(stego_file.filename))
    stego_file.save(stego_path)

    # Process Images
    try:
        extracted_enc_target = extract_image(stego_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    decrypted_img = decrypt_image(extracted_enc_target, x0, y0)
    
    out_filename = f'decrypted_out_{current_user.id}_{int(datetime.utcnow().timestamp())}.png'
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
    cv2.imwrite(out_path, decrypted_img)

    return jsonify({'message': 'Success', 'output_url': url_for('static', filename='uploads/' + out_filename)})

# --- FILE CLEANUP DAEMON ---
def cleanup_old_files():
    """Runs in the background and deletes images older than 15 minutes to save disk space."""
    while True:
        time.sleep(600)  # Check every 10 minutes
        now = time.time()
        folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                # If file is older than 15 minutes (900 seconds)
                if os.stat(filepath).st_mtime < now - 900:
                    try:
                        os.remove(filepath)
                        print(f"[CLEANUP] Deleted old file: {filename}")
                    except Exception as e:
                        pass

if __name__ == '__main__':
    from waitress import serve
    import logging
    
    # Start the background cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [SECURE-PIXEL] %(message)s')
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    print("==================================================")
    print(" ENGINE ONLINE: SecurePixel Production Server")
    print(" Listening on http://127.0.0.1:5000")
    print(" Press CTRL+C to terminate.")
    print("==================================================")
    
    serve(app, host='0.0.0.0', port=5000, threads=4)