FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN flask db init || true
RUN flask db migrate -m "initial migration" || true
RUN flask db upgrade || true

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app('production')"]