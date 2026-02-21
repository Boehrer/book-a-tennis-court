ARG TARGET_PLATFORM=linux/amd64
FROM --platform=${TARGET_PLATFORM} selenium/standalone-chrome:latest

USER root

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

COPY main.py secrets.py ./

CMD ["python3", "main.py"]
