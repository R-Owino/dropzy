from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session
                   )
from v1.cognito import login_user
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define Blueprint for login route
login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login

    GET:
        - Render the login page

    POST:
        - Retrieve email and password from form data
        - Call Cognito to authenticate the user
        - If authentication is successful:
            - store user session details including tokens
            - redirect to the main page
        - If authentication fails:
            - re-render the login page

    Returns:
        JSON response:
            - 200 OK: login page is rendered
            - 302 Redirect: main page upon successful login
    """

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        logger.debug(f"Login attempt for email: {email}")

        result = login_user(email, password)
        # logger.info(f"Login result: {result}")

        if result["Success"]:
            session.permanent = True
            session["email"] = email
            session["access_token"] = result["tokens"]["AccessToken"]
            session["id_token"] = result["tokens"]["IdToken"]
            session["logged_in"] = True
            session.modified = True

            return redirect(url_for("api.main.main"))
        else:
            logger.warning(f"Login failed: {result['message']}")
            return render_template("login.html")

    return render_template("login.html")
