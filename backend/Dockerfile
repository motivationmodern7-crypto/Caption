FROM python:3.10-slim

# System dependencies (FFMPEG zaroori hai)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Requirements copy karo
COPY ./requirements.txt /code/requirements.txt

# Yahan --verbose add karo taaki Railway ke Logs mein dikhe ki kya install ho raha hai
RUN pip install --verbose --no-cache-dir -r /code/requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
