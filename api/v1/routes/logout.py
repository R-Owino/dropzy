from flask import (Blueprint,
                   redirect,
                   url_for,
                   session)

# define Blueprint for logout route
logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Handle user logout

    - Clears all the session data
    - Redirects the user to the login page

    Returns:
        JSON response:
            - 302 Redirect: login page
    """
    session.clear()
    return redirect(url_for("api.login.login"))
