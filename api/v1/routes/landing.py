from flask import Blueprint, render_template

# Define Blueprint for the landing page route
landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def landing():
    """
    Handle requests to the landing page

    GET:
        - Render index.html template as the landing page

    Returns:
        JSON response:
            - 200 OK: landing page content
    """
    return render_template("index.html")
