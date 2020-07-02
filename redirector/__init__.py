import importlib
import os
import sys

from flask import Flask
from flask_caching import Cache

from .non_database import FlaskNonDatabase

# global non-database instance
# note for self: import everything that uses the non-database _after_ this line
non_db_ext = FlaskNonDatabase()

# some responses should be cached for performance reasons
# we use the simple but extensible Flask-Caching extension for this
cache = Cache()

# make decorators easy to import
from .dynamic import dynamic_redirect


def create_app(config: dict = None) -> Flask:
    """
    Idiomatic Flask way allowing to create different applications. This allows for creating more app objects, e.g.,
    for unit testing or some special deployments.

    Please note that it is not safe to run multiple instances in parallel, as the non-database extension has a global
    state.

    :return: app
    """

    app = Flask("redirector")

    app.config.setdefault("STATIC_REDIRECTIONS_MAX_AGE", "120")

    app.config.setdefault("CACHE_TYPE", "simple")

    # optional: load config.py from current working directory
    try:
        app.config.from_pyfile("config.py")
    except FileNotFoundError:
        print("config.py not found, skipping", file=sys.stderr)

    if config is not None:
        app.config.update(config)

    # environment variables support
    for env_var in ["REDIRECTIONS_MAP_PATH", "STATIC_REDIRECTIONS_MAX_AGE", "DYNAMIC_REDIRECTS_MODULES"]:
        if env_var in os.environ:
            app.config[env_var] = os.environ[env_var]

    try:
        for module_name in app.config["DYNAMIC_REDIRECTS_MODULES"].split(":"):
            importlib.import_module(module_name)

    except KeyError:
        pass

    # initialize extensions like the non-db
    non_db_ext.init_app(app)
    cache.init_app(app)

    # importing here to avoid annoying cyclic imports
    from .views import bp  # noqa: E402
    from .dynamic import dynamic_redirects_bp

    # register routes
    app.register_blueprint(bp)
    app.register_blueprint(dynamic_redirects_bp)

    return app
