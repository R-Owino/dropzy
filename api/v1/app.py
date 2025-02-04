from flask import Flask, render_template, session
from config import Config
from flask_session import Session
from datetime import timedelta
import logging

from routes.landing import landing_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.confirm import confirm_bp
from routes.resend_code import resend_bp
from routes.main import main_bp
from routes import upload_bp
from routes.download import download_bp
from routes import file_metadata_bp
from routes.delete import delete_bp
from routes.logout import logout_bp

import routes.upload
import routes.check_file
import routes.file_metadata
import routes.search_file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

Session(app)

app.register_blueprint(landing_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(confirm_bp)
app.register_blueprint(resend_bp)
app.register_blueprint(main_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(download_bp)
app.register_blueprint(file_metadata_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(logout_bp)


# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.before_request
def log_session_info():
    logger.debug(f"Session before request: {dict(session)}")


@app.after_request
def log_session_after_request(response):
    logger.debug(f"Session after request: {dict(session)}")
    return response


if __name__ == "__main__":
    app.run(debug=True)
