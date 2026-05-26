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
