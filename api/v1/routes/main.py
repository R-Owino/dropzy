import logging
from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   session)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the Blueprint for the main route
main_bp = Blueprint("main", __name__)


@main_bp.route("/main", methods=["GET", "POST"])
def main():
    """
    Handles requests to the main page

    GET:
        - Check if the user is logged in
        - Display main page for authenticated users
        - Otherwise, redirects to the login page
    POST:
        - Retrieve authenticated user details from session
        - Handle form submissions from main page

    Returns:
        JSON response:
            - 200 OK: render main page content for authenticated users
            - 302 Redirect: login page if user is unauthenticated
    """

    if not session.get("logged_in"):
        logger.warning("Unauthorized access attempt to main page")
        return redirect(url_for("api.login.login"))

    return render_template("main.html",
                           username=session["email"])
