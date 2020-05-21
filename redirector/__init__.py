import sys

from flask import Flask

from .non_database import FlaskNonDatabase

# global non-database instance
# note for self: import everything that uses the non-database _after_ this line
non_db_ext = FlaskNonDatabase()


# load views
from .views import bp


def create_app(config: dict = None) -> Flask:
    """
    Idiomatic Flask way allowing to create different applications. This allows for creating more app objects, e.g.,
    for unit testing or some special deployments.

    Please note that it is not safe to run multiple instances in parallel, as the non-database extension has a global
    state.

    :return: app
    """

    app = Flask("redirector")

    if config is not None:
        app.config.update(config)

    # initialize extensions like the db
    try:
        non_db_ext.init_app(app)
    except Warning as w:
        print("Warning:", w, file=sys.stderr)

    # register routes
    app.register_blueprint(bp)

    return app
