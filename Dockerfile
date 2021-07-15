FROM python:3.8
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY sense_energy_prometheus_exporter /tmp/exporter
COPY VERSION.txt /tmp/exporter/
RUN pip install --no-cache-dir /tmp/exporter
COPY ./main.py ./

ENTRYPOINT ["python", "./main.py"]
