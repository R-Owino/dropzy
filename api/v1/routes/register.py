from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session,
                   jsonify
                   )
from v1.cognito import register_user, email_exists
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Define Blueprint for register user route
register_bp = Blueprint("register", __name__)


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration

    GET:
        - Render the registration page
    POST:
        - Retrieve email, username and password from form data
        - Call Amazon Cognito to register the user
        - If successful, store the email in session and
            redirect to confirmation page
        - If unsuccessful, re-render the registration page

    Returns:
        JSON response:
            - 200 OK: render the registration page
            - 302 Redirect: confirmation page upon successful registration
            - 400 Bad Request: registration failed due to invalid inputs
            - 409 Conflict: email entered is already registered
            - 500 Internal Server Error: server error during registration
    """
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            if email_exists(email):
                return jsonify({
                    "message": "User with email already exists."
                }), 409

            result = register_user(email, username, password)
            if result["Success"]:
                session["verification_email"] = email
                return redirect(url_for("api.confirm.confirm"))
            else:
                return jsonify({
                    "message": (
                        "Registration failed. Please check your inputs."
                    )
                }), 400
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return jsonify({
                "message": "An error occured. Please try again."
            }), 500

    return render_template("register.html")
