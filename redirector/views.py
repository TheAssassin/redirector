from flask import Blueprint, redirect, make_response, current_app
from werkzeug.exceptions import NotFound

from . import non_db_ext

bp = Blueprint("redirector", __name__)

# TODO: JSON API for redirections


@bp.route("/")
def index():
    text = "\n".join(
        ("{}: {}".format(k, v) for k, v in non_db_ext.non_db.urls_to_names.items())
    )

    response = make_response(text, 200)
    response.mimetype = "text/plain"

    return response


# TODO: once / are allowed for names, change this to /<name:path>
@bp.route("/<name>")
def shortener(name: str):
    """
    The main redirection handling view. It does not permit ``/`` values in names as of yet.
    """

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
