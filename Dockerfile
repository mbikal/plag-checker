FROM node:20-alpine AS frontend-builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json /app/
RUN npm ci
COPY frontend /app
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY plag_system /app/plag_system
COPY users.json /app/users.json
RUN mkdir -p /app/ca /app/certs /app/uploads
COPY --from=frontend-builder /app/dist /app/frontend/dist

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "backend/auth.py"]
