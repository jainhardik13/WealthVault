"""
WealthVault - Personal Portfolio & Stock Tracking Application
=============================================================
Main Flask application file that initializes the web server and routes.

This application allows users to:
- Track Indian stocks (NSE & BSE)
- Manage stock portfolio (Add, Edit, Delete)
- View real-time stock prices and profit/loss
- Get AI-powered stock predictions using Google Gemini
- View interactive price charts
- Search stocks with live prices

Tech Stack:
- Backend: Flask (Python)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Charts: Chart.js
- AI: Google Gemini API
- Stock Data: NSEPython, BSE Web Scraping
"""

from flask import Flask, render_template
from dotenv import load_dotenv
from models.portfolio_models import init_db
from routes.portfolio_routes import portfolio_bp
from routes.search_routes import search_bp
from routes.graph_routes import graph_bp
from routes.ai_routes import ai_bp
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Secret key for session management

# Initialize SQLite database (creates tables if they don't exist)
init_db()

# Register all blueprints (modular route handlers)
app.register_blueprint(portfolio_bp)  # Portfolio CRUD operations
app.register_blueprint(search_bp)     # Stock search functionality
app.register_blueprint(graph_bp)      # Historical price charts
app.register_blueprint(ai_bp)         # AI predictions and insights

# =====================
# MAIN ROUTES
# =====================

@app.route("/")
def home():
    """
    Home page route - Displays personal portfolio website
    Shows: About, Skills, Projects, Contact information
    """
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    """
    Dashboard route - Redirects to portfolio blueprint
    The actual dashboard logic is in portfolio_routes.py
    """
    return render_template("dashboard.html")

# =====================
# RUN APPLICATION
# =====================

if __name__ == "__main__":
    # Run Flask development server
    # debug=True enables auto-reload and detailed error messages
    app.run(debug=True)