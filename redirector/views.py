import os

from flask import Blueprint, redirect, current_app, jsonify, render_template
from werkzeug.exceptions import NotFound

from . import non_db_ext

this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
static_folder = os.path.join(this_dir, "static")
template_folder = os.path.join(this_dir, "templates")

bp = Blueprint("redirector", __name__, static_folder=static_folder, template_folder=template_folder)

# TODO: JSON API for redirections


@bp.route("/")
def index():
    return render_template("index.html", non_db=non_db_ext.non_db)


@bp.route("/api/urls.json")
def api_urls():
    return jsonify(non_db_ext.non_db.urls_to_names)


# TODO: once / are allowed for names, change this to /<name:path>
@bp.route("/<name>")
def shortener(name: str):
    """
    The main redirection handling view. It does not permit ``/`` values in names as of yet.
    """

    # The /api prefix is reserved, so if no other view handles a request like this,
    # we need to reply here accordingly
    # TODO: decide whether to decline all "/api.*" requests or only "/api"
    if name.startswith("api"):
        raise NotFound

    try:
        url = non_db_ext.non_db.lookup_url_for_name(name)

    except KeyError:
        raise NotFound

    # depending on the configuration, we either return a "permanent" redirect with a small cache timeout, or a
    # "temporary" one
    max_age = current_app.config["STATIC_REDIRECTIONS_MAX_AGE"]

    if not max_age:
        max_age = 0

    # make sure it's an int
    max_age = int(max_age)

    response = redirect(url, 302)

    if max_age > 0:
        response.status_code = 301
        response.headers["Cache-Control"] = "max-age={}".format(max_age)

    return response
