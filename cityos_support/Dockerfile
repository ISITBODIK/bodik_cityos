FROM python:3.12.11


WORKDIR /app

COPY requirements.txt .

RUN apt-get update

# gdal, unzip, tippecanoe依存
RUN apt-get update && \
    apt-get install -y gdal-bin unzip build-essential git libsqlite3-dev zlib1g-dev && \
    git clone https://github.com/felt/tippecanoe.git /tmp/tippecanoe && \
    cd /tmp/tippecanoe && make -j && make install && \
    rm -rf /var/lib/apt/lists/* /tmp/tippecanoe

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt 

EXPOSE 8080
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*", "--port", "8080", "--ssl-keyfile", "./ssl/bodik.key", "--ssl-certfile", "./ssl/bodik.jp.pem"]
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*", "--port", "8080"]