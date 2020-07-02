from flask import Blueprint

from . import cache as _cache

dynamic_redirects_bp = Blueprint("dynamic_redirects", __name__)


# we store all registered dynamic blueprints in order to be able to render the index page and provide them via the API
dynamic_routes = []


def dynamic_redirect(route, timeout=300):
    def actual_decorator(f):
        print(route, f)

        # this syntax might be awkward, but it works
        cached_f = _cache.cached(timeout=timeout)(f)
        dynamic_redirects_bp.route(route)(cached_f)

        # remember route for later
        dynamic_routes.append(route)

        return f

    return actual_decorator
