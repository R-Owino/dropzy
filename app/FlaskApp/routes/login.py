from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session
                )
from cognito import login_user
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """defines the login route"""
    logger.debug("Login route accessed")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        logger.debug(f"Login attempt for username: {username}")

        result = login_user(username, password)
        logger.debug(f"Login result: {result}")
        if result["Success"]:
            session.permanent = True

            session["username"] = username
            session["access_token"] = result["tokens"]["AccessToken"]
            session["logged_in"] = True

            session.modified = True

            logger.debug("Login successful, session created")

            flash("Login Successful!", "success")
            return redirect(url_for("main.main"))
        else:
            logger.warning(f"Login failed: {result['message']}")
            flash(result["message"], "danger")
    
    return render_template("login.html")
