FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "sleep 10 && flask run --host=0.0.0.0 --port=8080"]