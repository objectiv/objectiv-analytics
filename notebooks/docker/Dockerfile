FROM python:3.9

ENV DEBIAN_FRONTEND=non-interactive

ENV APP=/services/notebooks/

RUN mkdir -p $APP && \
    apt -q update && \
    apt -qy upgrade && \
    apt -qy install postgresql-client && \
    apt clean && \
    python3 -m venv /services/venv && \
    . /services/venv/bin/activate && \
    python -m pip install --upgrade pip && \
    useradd --user-group --system --create-home --no-log-init notebook

COPY docker/*.sql  /services/

COPY requirements.txt /services

RUN . /services/venv/bin/activate && \
    cd /services && \
    pip install --no-use-pep517  sklearn && \
    pip install -r requirements.txt


COPY docker/entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY *.ipynb $APP

USER notebook
ENV OBJECTIV_VERSION_CHECK_DISABLE=true
ENTRYPOINT /entrypoint.sh
