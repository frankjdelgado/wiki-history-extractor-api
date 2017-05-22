from flask import Blueprint

api = Blueprint('api', __name__)

from .docs import auto
from . import docs, errors, views, status, revisions, extract, queries, articles

