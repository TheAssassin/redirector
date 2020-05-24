# redirector

![Traivs status](https://travis-ci.org/TheAssassin/redirector.svg?branch=master&status=passed)
[![Coverage Status](https://opencov.assassinate-you.net/projects/4/badge.svg)](https://opencov.assassinate-you.net/projects/4)

This project provides a simple redirection web service app, with self-hosting in mind. It is built
using the awesome [Flask micro-framework](https://flask.palletsprojects.com/).

It can be used to set up a
URL shortener providing persistent links to URLs which might change over time. It is especially
useful in the following scenarios (non-exhaustive list):

- Linking to third-party-provided services from a self-operated instance (looking at you, "cloud" and "SAAS" stuff!)
- Online documentation (docs are never, content might be moved over time, static links are difficult to realize)
- Static links to release files with non-fixed names (useful if links are included in scripts and other static documents)
- etc.


## Features

In this application, there are two kinds of redirection types: static and dynamic ones. The former
are typically specified in a JSON file by the user, the latter in Python code. The two types are
described in this section.


### Static redirections

The user needs to provide a mapping of URLs to short names they want the redirector to trigger on.
Naturally, one could be tempted to do it the other way round, providing a short-name-to-URL mapping.
This, however, has significant usage drawbacks. Technically speaking, URLs have a one-to-many
relation to the short names. In simple words, this means that every URL can be assigned multiple
short names. In a name-to-URL mapping, one would have to specify the same URL for every name that
should be assigned to it. This is really annoying, as then the same URL would be repeated over and
over again.

The data format chosen has one significant drawback its reverse counterpart does not have: it is
prone to name collisions. The names need to be unique for obvious reasons, there can be at most one
URL with the same short name. What might not be a problem in a properly made relational database
(i.e., a ER model with at least 2NF properly implemented and a unique constraint in the names table)
becomes one in this scenario. As we don't have a real database system to perform these checks, the
application performs a duplicates check when loading the data during startup. You will be presented
a useful error message if there are duplicate entries.

The term "static" refers to the property that the mapping between short name and URL is fixed. The
URL used in the redirection is not changed unless explicitly requested by the user.

This is an example for a JSON file containing static redirections:

```json
{
    "https://appimage.org/": [
        "appimage",
        "ai"
    ],

    "https://docs.appimage.org": [
        "ai-docs",
        "aidocs",
        "appimage-docs"
    ]
}
```

In a simple deployment, one has to restart the application server to apply changes to the file.

The default JSON file path is `redirections.json`, relative to the working directory of the server
process.


### Dynamic redirections

There are plans to implement dynamic redirections by letting users register callbacks for certain
names. This way, the redirector can provide a static frontend for URLs which might change over time.


## HTTP interface

Being a web service, the redirector provides some HTTP endpoints. These are described in this
section.

### Redirections list ("index page")

The redirector provides an overview of all registered URLs on its index URL `/`. This is done
for transparency reasons, allowing users to look up links before being redirected to a random
page.


### Redirection endpoints

Every other URL path is as of now considered to be treated by this handler, there are no reserved
other names as of yet. The URLs follow the pattern `/<name>`.

Please note that names are explicitly not allowed to contain `/` characters. This might be changed at
a later point. 

A `404 Not Found` status is returned if a short name is not known.

A `301 Moved Permanently` status with `Cache-Control: max-age=X` is sent for static redirections.
According to several online sources, this is similar to many public URL shorteners' behavior
(e.g., bit.ly uses a value of `90`).
The advantage is that it allows the client to cache a URL for at most `X` seconds before they have
to make another request. Of course, it means that updates will be seen `X` seconds after the first
request in the worst case (given the client implements caching at all), however for static URLs this
should be an acceptable trade-off.
The timeout value is configurable. Please refer to the [Configuration](#configuration) section.
The feature can be disabled as well. In that case, a `302 Found` header is used.

A `302 Found` status is returned for dynamic redirections. Here, the URL is likely to change more
regularly, therefore a new request should be made by the client every time the value is used.

### HTTP API

`/api/urls.json` returns a JSON representation of all URLs and the short names assigned to them.
The format is equivalent to the static routes file.
For dynamic routes, the currently cached value is shown (if available), otherwise `null` is returned.


## Configuration

This application is, as of yet, only configurable through environment variables. This is an easy
and widely known approach that is also very compatible with modern deployment systems like Docker.

- `REDIRECTIONS_MAP_PATH` (optional): path to the JSON file used to configure the static
   redirections. The file must exist and contain valid JSON following the data format described
   above. By default, the application tries to use a file called `redirects.json` in the current
   working directory. If it does not exist, no static mappings will be available and a warning is
   displayed.
- `STATIC_REDIRECTIONS_MAX_AGE` (optional): The value of the `Cache-Control: max-age=` header sent
   when handling static redirections. The unit is seconds. The default value is `120`. Set to a
   value `<= 0` to disable client-side caching.
   
   
## How to run

There are two scenarios in which this application can be run: development and production.


### Development server

Nowadays, the [Flask framework](https://flask.palletsprojects.com/) provides the `flask` command,
which can be used to run a development server. For example:

```
> export FLASK_APP=redirector:create_app
> export FLASK_ENV = development
> flask run
 * Serving Flask app "redirector:create_app" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:10000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-yyy-zzz
```

For more information, please see the
[Flask docs](https://flask.palletsprojects.com/en/1.1.x/server/).


### Production

For real deployments, a WSGI application server should be used. A simple-to-use one is
[Gunicorn](https://gunicorn.org/). The following example illustrates how to run the application
through `gunicorn`:

```
> export FLASK_APP=redirector:create_app
# run a server with 4 threads on port 8000 on all interfaces
> gunicorn -w 4 $FLASK_APP -b :8000
```

You can use pretty much any WSGI server you want to use.


### Docker

The project comes with a `Dockerfile`, which makes deployment really easy. It is recommended to use
[`docker-compose`](https://docs.docker.com/compose/) to set up and operate the service.

The project includes a `docker-compose.yml.example` file which shows how to run the service.
