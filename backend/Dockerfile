# Python ka official image
FROM python:3.10-slim

# Working directory set karo
WORKDIR /code

# Requirements copy aur install karo
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Baaki code copy karo
COPY . .

# IMPORTANT: Railway ke liye $PORT ka use karo
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
