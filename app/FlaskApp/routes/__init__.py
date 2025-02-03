from flask import Blueprint

# define blueprints that are used across multiple routes
upload_bp = Blueprint("upload", __name__)
file_metadata_bp = Blueprint("file_metadata", __name__)

# export the blueprints
__all__ = ['upload_bp', 'file_metadata_bp']
