import os

from flask import Flask

from .non_database import FlaskNonDatabase

# global non-database instance
# note for self: import everything that uses the non-database _after_ this line
non_db_ext = FlaskNonDatabase()


# load views
from .views import bp  # noqa: E402


def create_app(config: dict = None) -> Flask:
    """
    Idiomatic Flask way allowing to create different applications. This allows for creating more app objects, e.g.,
    for unit testing or some special deployments.

    Please note that it is not safe to run multiple instances in parallel, as the non-database extension has a global
    state.

    :return: app
    """

    app = Flask("redirector")

    # default value
    app.config.setdefault("STATIC_REDIRECTIONS_MAX_AGE", "120")

    if config is not None:
        app.config.update(config)

    # environment variables support
    for env_var in ["REDIRECTIONS_MAP_PATH", "STATIC_REDIRECTIONS_MAX_AGE"]:
        if env_var in os.environ:
            app.config[env_var] = os.environ[env_var]

    # initialize extensions like the non-db
    non_db_ext.init_app(app)

    # register routes
    app.register_blueprint(bp)

    return app
