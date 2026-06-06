# Python ka official image use karte hain
FROM python:3.10-slim

# Working directory set karo
WORKDIR /code

# Pehle requirements copy karo (taaki caching fast ho)
COPY ./requirements.txt /code/requirements.txt

# Dependencies install karo
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Baaki sara code copy karo
COPY . .

# Server start karne ka command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
