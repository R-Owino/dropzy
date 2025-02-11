FROM python:3.11-slim

WORKDIR /app
COPY api/v1 /app/
COPY api/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "python", "app.py" ]
