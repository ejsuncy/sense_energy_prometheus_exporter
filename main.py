import time
import logging
from typing import Dict

from sense_energy_prometheus_exporter import AccountCollector,DeviceCollector,CurrentCollector,FrequencyCollector,PowerCollector,VoltageCollector,TrendCollector,TimelineCollector
from sense_energy_prometheus_exporter import EnvironmentParser,FileParser
from sense_energy_prometheus_exporter import SenseClient,SenseAccount

from prometheus_client import start_http_server, REGISTRY



class ExporterApplication():
    def __init__(self):
        self.exporter_namespace: str = None
        self.exporter_port: str = None
        self.exporter_bind_host: str = None
        self.app_configs: Dict = None
        self.timeline_num_items: int = 30
        self.sense_accounts: [SenseAccount] = []

    def register_collectors(self):
        logging.debug("Initializing Sense Client")
        sense_client = SenseClient(self.sense_accounts, self.timeline_num_items)

        logging.debug("Initializing AccountCollector")
        account_collector = AccountCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering AccountCollector")
        REGISTRY.register(account_collector)

        logging.debug("Initializing DeviceCollector")
        device_collector = DeviceCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering DeviceCollector")
        REGISTRY.register(device_collector)

        logging.debug("Initializing CurrentCollector")
        current_collector = CurrentCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering CurrentCollector")
        REGISTRY.register(current_collector)

        logging.debug("Initializing FrequencyCollector")
        frequency_collector = FrequencyCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering FrequencyCollector")
        REGISTRY.register(frequency_collector)

        logging.debug("Initializing PowerCollector")
        power_collector = PowerCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering PowerCollector")
        REGISTRY.register(power_collector)

        logging.debug("Initializing VoltageCollector")
        voltage_collector = VoltageCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering VoltageCollector")
        REGISTRY.register(voltage_collector)

        logging.debug("Initializing TrendCollector")
        trend_collector = TrendCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering TrendCollector")
        REGISTRY.register(trend_collector)

        logging.debug("Initializing TimelineCollector")
        device_timeline_collector = TimelineCollector(sense_client, self.exporter_namespace)
        logging.debug("Registering TimelineCollector")
        REGISTRY.register(device_timeline_collector)

    def start_server(self):
        if app.app_configs:
            logging.info("App namespace from config file: %s", app.app_configs['namespace'])
        logging.info("Starting server on %s:%s", self.exporter_bind_host, self.exporter_port)
        start_http_server(port=int(self.exporter_port), addr=self.exporter_bind_host)

        # Keep the main thread active so the daemon threads can handle requests
        while True:
            time.sleep(1)


if __name__ == '__main__':
    app = ExporterApplication()
    EnvironmentParser.parse_logging_config(app)
    EnvironmentParser.parse_server_config(app)
    EnvironmentParser.parse_sense_accounts(app)
    EnvironmentParser.parse_collector_configs(app)
    FileParser.parse_app_configs(app)
    app.register_collectors()
    app.start_server()
