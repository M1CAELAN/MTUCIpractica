FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r req.txt


EXPOSE 8080


CMD ["python", "main.py", "runserver", "0.0.0.0:8080"]

