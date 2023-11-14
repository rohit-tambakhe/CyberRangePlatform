FROM python:3.11-slim-bullseye

RUN pip install kubernetes slack-sdk

RUN mkdir /app

COPY alerts.py /app/alerts.py

WORKDIR /app

# Run the script
CMD ["python3", "alerts.py"]
