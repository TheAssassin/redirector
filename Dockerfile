FROM python:3-alpine

MAINTAINER "TheAssassin <theassassin@user.noreply.github.com>"
LABEL org.opencontainers.image.source="https://github.com/TheAssassin/blueflare"

COPY redirector/ /app/redirector/
COPY setup.py /app/
COPY pyproject.toml /app/

WORKDIR /app

# log all commands
SHELL ["sh", "-x", "-c"]

# installing in development mode avoids duplicate files in the image
RUN apk add --no-cache libxml2-dev libxslt-dev gcc musl-dev && \
    python -m ensurepip && \
    pip install -e . && \
    pip install gunicorn

# run gunicorn by default
# the service will listen on port 8080, and print access logs to stdout/stderr
CMD gunicorn -w "$(nproc)" "redirector:create_app()" -b :8080 --access-logfile -
