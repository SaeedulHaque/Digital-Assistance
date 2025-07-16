FROM python:3.10-slim

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir \
    beautifulsoup4 \
    python-dotenv

CMD ["python", "test_email_processor.py"]