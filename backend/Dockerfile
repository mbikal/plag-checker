FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY plag_system /app/plag_system
RUN mkdir -p /app/ca /app/certs /app/uploads
COPY users.json /app/users.json

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "backend/auth.py"]
