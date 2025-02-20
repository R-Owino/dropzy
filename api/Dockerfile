FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt /app/
COPY api/tests /app/tests/
COPY api/v1/app.py /app/v1/
COPY api/v1/cognito.py /app/v1/
COPY api/v1/config.py /app/v1/
COPY api/v1/__init__.py /app/v1/
COPY api/v1/routes/ /app/v1/routes/
COPY api/v1/static/ /app/v1/static/
COPY api/v1/templates/ /app/v1/templates/

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /app/v1

ENV PYTHONPATH="/app"

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "v1.app:app" ]
