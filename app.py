# from models.portfolio_models import init_db
#
# if __name__ == "__main__":
#     # Initialize the database
#     init_db()
#     print("Database initialized successfully!")
#     print("Database created at: database/portfolio.db")
#

from flask import Flask, render_template
from dotenv import load_dotenv
from models.portfolio_models import init_db
from routes.portfolio_routes import portfolio_bp
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Intialize the database
init_db()

app.register_blueprint(portfolio_bp)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)