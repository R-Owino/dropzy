from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session
                   )
from v1.cognito import register_user

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
            - 409 Conflict: email entered is already registered
    """
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        result = register_user(email, username, password)
        if result["Success"]:
            session["verification_email"] = email
            return redirect(url_for("api.confirm.confirm"))
        elif "UsernameExistsException" in result.get("message", ""):
            return render_template("register.html"), 409

    return render_template("register.html")
