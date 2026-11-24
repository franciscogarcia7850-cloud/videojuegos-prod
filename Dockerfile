FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=mysql+pymysql://user:pwd@db/videojuegos
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--threads", "4", "app:app"]
