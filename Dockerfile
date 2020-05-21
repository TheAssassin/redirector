FROM python:3.7-alpine

COPY redirector/ /app/redirector/
COPY setup.py /app/
COPY pyproject.toml /app/

WORKDIR /app

# log all commands
SHELL ["sh", "-x", "-c"]

# installing in development mode avoids duplicate files in the image
RUN pip install -U pip && \
    pip install -e . && \
    pip install gunicorn

# run gunicorn by default
# the service will listen on port 8080, and print access logs to stdout/stderr
CMD gunicorn -w "$(nproc)" "redirector:create_app()" -b :8080 --access-logfile -
