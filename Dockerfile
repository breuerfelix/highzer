FROM python:3-slim

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "cli.py", "test"]
