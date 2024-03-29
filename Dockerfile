FROM python:3.11 as build

WORKDIR /sense

COPY ./main.py ./requirements.txt ./
COPY sense_energy_prometheus_exporter ./sense/exporter
COPY VERSION.txt ./sense/exporter/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir ./sense/exporter

FROM gcr.io/distroless/python3-debian12

ENV PYTHONPATH /sense_exporter
COPY --from=build /usr/local/lib/python3.11/site-packages /
COPY --from=build /sense/main.py /

ENTRYPOINT ["python", "main.py"]
