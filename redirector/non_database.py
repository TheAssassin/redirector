import json
from typing import Union, List

from flask import Flask


class NonDatabase:
    """
    Reads a JSON file mapping URLs to short names which the redirector should know. Provides a fast and easy interface
    for looking up in both directions.
    """

    def __init__(self, filename_or_data: Union[str, dict, None] = None):
        """
        Hybrid constructor. Can either initialize an empty non-database into which one can later load the data, or
        alternatively the data (or a string to the data) can be passed directly, saving one call.

        For more information on the data structure, please refer to :meth:`load_data`.

        :param filename_or_data: Path of file or data
        """

        # we store the mapping twice
        # this adds memory overhead, however reduces runtime overhead significantly
        # given the amount of names this redirector typically has to handle, this is an acceptable trade-off

        # URLs-to-names mapping, can be used to lookup all names assigned to a URL
        self.urls_to_names: dict = {}

        # names-to-URLs mapping, can be used to lookup the URL assigned to a name
        self.names_to_urls: dict = {}

        if filename_or_data is not None:
            self.load_data(filename_or_data)

    def load_data(self, filename_or_data: Union[str, dict]):
        """
        This method loads the data into the internal storage. It can be used to initialize and later re-initialize the
        non-database instance.

        The expected data structure is a mapping of URLs to the short names the redirector shall react on. It's the
        reverse of the many-to-one names-to-URL mapping the system usually works with.

        :param filename_or_data: either a path to a JSON file which should be loaded, or the data directly
        """

        if isinstance(filename_or_data, dict):
            self.urls_to_names = filename_or_data

        else:
            with open(filename_or_data, "r") as f:
                self.urls_to_names = json.load(f)

        # this call also performs a validity check on all names (e.g., ensuring that no / is contained)
        self.names_to_urls = self._build_reverse_map(self.urls_to_names)

    @classmethod
    def _validate_name(cls, name):
        if "/" in name:
            raise ValueError("/ character is not allowed in names")

    @classmethod
    def _build_reverse_map(cls, forward_map: dict):
        reverse_map = {}

        for url, names in forward_map.items():
            for name in names:
                # due to the way the input data mapping is constructed (i.e., mapping URLs to names), names might be
                # specified more than once
                # this is however not in order, the names need to be unique
                # therefore, on load, we need to make sure there are no collisions
                if name in reverse_map:
                    raise ValueError("Name collision: {} is used for (at least) both URLs {} and {}".format(
                        name, reverse_map[name], url
                    ))

                # call name checker to make sure the names are valid
                cls._validate_name(name)

                reverse_map[name] = url

        return reverse_map

    def lookup_url_for_name(self, name: str) -> str:
        """
        Looks up a URL for a given short name.

        :param name: short name
        :return: URL
        :raises KeyError: if no URL can be found
        """

        return self.names_to_urls[name]

    def lookup_names_for_url(self, url: str) -> List[str]:
        """
        Returns the list of names assigned to a URL. Read-only.

        :param url: URL to look up in the data
        :return: copy of the list of names assigned to provided URL
        :raises KeyError: if no URL can be found
        """

        # the only way to make this really read-only is to copy the list
        return self.urls_to_names[url].copy()


class FlaskNonDatabase:
    """
    Flask extension for the NonDatabase.
    """

    def __init__(self, app: Flask = None):
        self.app: Union[Flask, None] = app

        # we make this available through a read-only property only to be able to make a sanity check and raise an
        # exception with a proper description if this is still None, meaning that the application has not been
        # initialized
        self._non_db: Union[NonDatabase, None] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self._non_db = NonDatabase()

        app.config.setdefault("REDIRECTIONS_MAP_PATH", None)

        path = app.config["REDIRECTIONS_MAP_PATH"]

        if path is None:
            try:
                self._non_db.load_data("redirects.json")

            except FileNotFoundError:
                raise RuntimeWarning("no redirections database path specified and redirects.json not found, "
                                     "no static redirections available")
        else:
            self._non_db.load_data(path)

    @property
    def non_db(self):
        if self._non_db is None:
            raise ValueError("extension has not been initialized yet")

        return self._non_db


