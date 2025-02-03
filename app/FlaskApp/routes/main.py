import logging
from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   session)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

@main_bp.route("/main", methods=["GET", "POST"])
def main():
    """defines the main page route"""
    logger.debug("Current session contents: %s", dict(session))

    logger.debug("Session logged_in: %s", session.get("logged_in"))
    logger.debug("Session username: %s", session.get("username"))
    logger.debug("id_token: %s", session.get("id_token"))

    if not session.get("logged_in"):
        logger.warning("Unauthorized access attempt to main page")
        return redirect(url_for("login.login"))
    
    return render_template("main.html",
                           username=session["username"])
