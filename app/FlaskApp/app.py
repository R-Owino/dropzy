from flask import Flask, render_template
from config import Config
from routes.landing import landing_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.confirm import confirm_bp
from routes.main import main_bp
from routes.logout import logout_bp

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

app.register_blueprint(landing_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(confirm_bp)
app.register_blueprint(main_bp)
app.register_blueprint(logout_bp)

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
