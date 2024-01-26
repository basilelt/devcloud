FROM python:3.11.3-bullseye

ADD django/ /app

RUN set -ex \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app/G7

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "G7.asgi:application"]