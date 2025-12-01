FROM python:3.12.11

WORKDIR /app

COPY requirements.txt .

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt 

EXPOSE 8080
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*", "--port", "8080", "--ssl-keyfile", "./ssl/bodik.key", "--ssl-certfile", "./ssl/bodik.jp.pem"]
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*", "--port", "8080"]
