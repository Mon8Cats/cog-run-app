
FROM python:3.11

COPY requirements.txt ./

# Install production dependencies.
RUN set -ex; \
    pip install -r requirements.txt; \
    pip install gunicorn

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
