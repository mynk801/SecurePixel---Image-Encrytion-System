# SecurePixel

**Layered Chaos Theory & Steganography Engine**

SecurePixel is a production-ready, full-stack image cryptography application. It utilizes a two-layer security approach: scrambling target images using the mathematically chaotic Henon Map, and then seamlessly concealing the scrambled data within a carrier image using high-fidelity 2-bit Least Significant Bit (LSB) steganography.

---

## 🚀 Features

* **Chaos Engine Cryptography:** Utilizes the Henon Map for mathematically deterministic, vectorized image scrambling with float-overflow protection.
* **Dynamic High-Fidelity Steganography:** Implements 2-bit LSB embedding with 32-bit dynamic file headers, preserving 100% of the target image's quality without forced resizing.
* **Brutalist "Editorial" Interface:** A stark, minimalist, split-screen UI built with vanilla JS and asynchronous fetch operations.
* **Enterprise Security Hardening:** * AES Symmetric Encryption (`cryptography.fernet`) for securing mathematical vectors at rest.
  * CSRF Protection (`Flask-WTF`) to prevent cross-site request forgery.
  * Rate Limiting (`Flask-Limiter`) to prevent brute-force and DDoS attacks.
* **Secure Ledger (MongoDB):** A fully authenticated history dashboard tracking user sessions, target files, and encrypted initialization vectors.
* **Automated Janitor Daemon:** A background threading process that automatically wipes temporary image files from the server every 15 minutes to prevent disk bloat.
* **Production-Ready Server:** Runs on the multi-threaded `Waitress` WSGI server for concurrent user handling.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, Flask, Waitress
* **Image Processing:** OpenCV (`cv2`), NumPy
* **Database:** MongoDB, Flask-PyMongo
* **Security & Auth:** Flask-Login, Flask-Bcrypt, Flask-WTF, Flask-Limiter, Cryptography (Fernet), python-dotenv
* **Frontend:** HTML5, CSS3 (Inter & Space Grotesk fonts), Vanilla JavaScript

---

## 📂 Project Structure

```text
SecurePixel/
│
├── chaos_engine/
│   ├── __init__.py
│   └── henon.py             # Vectorized Henon Map logic
│
├── steganography/
│   ├── __init__.py
│   └── lsb.py               # 2-bit LSB dynamic hiding logic
│
├── static/
│   └── uploads/             # Temporary processing directory
│
├── templates/
│   ├── index.html           # Main Workspace & Ledger UI
│   └── login.html           # Authentication UI
│
├── .env                     # Environment variables (Secrets)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── main.py                  # Core application, auth, routing & server
```

---

## ⚙️ Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/mynk801/SecurePixel---Image-Encrytion-System.git
cd SecurePixel
```

**2. Set up a Virtual Environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
Create a `.env` file in the root directory and add the following keys. Ensure you generate a secure Fernet key (e.g., via `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).
```env
SECRET_KEY=your-secure-flask-session-key
MONGO_URI=mongodb://localhost:27017/securepixel_db
FERNET_KEY=your-generated-fernet-key=
```

**5. Start the Database**
Ensure your local MongoDB server is running on `localhost:27017`.

---

## 💻 Running the Application

Start the production Waitress server by running:
```bash
python main.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## 🔐 Usage Guide

1. **Authenticate:** Register a new user clearance and establish a session.
2. **Encrypt:** * Drop a large carrier image (Base) and a smaller secret image (Target).
   * Specify Henon Map keys (`x0` and `y0`).
   * Process and download the Stego-Image.
3. **Decrypt:** * Switch to Decrypt mode.
   * Drop the previously generated Stego-Image.
   * Input the *exact* Henon Map keys used during encryption.
   * Recover the original secret image.
4. **Ledger:** Review your past encryption operations and securely retrieve your Henon vectors.

---
*Disclaimer: This project was built for educational and theoretical cryptography purposes.*
