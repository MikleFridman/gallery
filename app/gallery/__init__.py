from flask import Blueprint

bp = Blueprint('gallery', __name__)

from app.gallery import views, models, forms
