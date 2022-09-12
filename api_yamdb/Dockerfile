FROM python:3.7-slim
ENV USER=django

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip3 install -r /app/requirements.txt --no-cache-dir

RUN useradd ${USER} \
    && mkdir -p static media \
    && chown -R ${USER}:${USER} .

COPY --chown=${USER}:${USER} . .

USER ${USER}
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api_yamdb.wsgi:application"] 