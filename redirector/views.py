from flask import Blueprint, redirect, make_response

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
        return "not found", 404

    # return 301 with a small cache timeout value like many other shorteners
    response = redirect(url, 301)
    response.headers["Cache-Control"] = "max-age=120"
    return response
