# 1. Python ka official image
FROM python:3.10-slim

# 2. System dependencies install karo (FFMPEG yahan add kiya hai)
# && rm -rf... se image ka size chota rahega
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Working directory set karo
WORKDIR /code

# 4. Requirements copy aur install karo
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Baaki code copy karo
COPY . .

# 6. Server start command
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
