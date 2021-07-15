import time
import logging
from .CustomCollector import CustomCollector
from ..client.sense import SenseClient, SensePower
from prometheus_client.core import GaugeMetricFamily, Counter, Gauge


class PowerCollector(CustomCollector):
    powerMetric: GaugeMetricFamily
    scrapesTotalMetric: Counter
    scrapeErrorsTotalMetric: Counter
    lastScrapeErrorMetric: Gauge
    lastScrapeTimestampMetric: Gauge
    lastScrapeDurationSecondsMetric: Gauge

    # the subsystem prefix is a name for the item type you are scraping
    subsystemPrefix: str = "power"

    # the set of labels that describe each of your items that you are scraping
    powerLabels: [str] = ["account", "name"]

    # This is the client that calls external apis for the items you want to scrape
    sense_client: SenseClient

    def __init__(self, sense_client: SenseClient, namespace: str):
        super().__init__(namespace)
        self.sense_client = sense_client

        self.scrapesTotalMetric = Counter("total", f"Total number of scrapes for {self.subsystemPrefix} stats",
                                          subsystem=f"{self.subsystemPrefix}_scrapes",
                                          namespace=self.namespace)
        self.scrapeErrorsTotalMetric = Counter("total",
                                               f"Total number of scrape errors for {self.subsystemPrefix} stats",
                                               subsystem=f"{self.subsystemPrefix}_scrape_errors",
                                               namespace=self.namespace)
        self.lastScrapeErrorMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_error",
                                           f"Status of last scrape for {self.subsystemPrefix} stats (1=error, 0=success)",
                                           subsystem="", namespace=self.namespace)
        self.lastScrapeTimestampMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_timestamp",
                                               f"Number of seconds between 1970 and last scrape for {self.subsystemPrefix} stats",
                                               subsystem="", namespace=self.namespace)
        self.lastScrapeDurationSecondsMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_duration_seconds",
                                                     f"Duration of last scrape for {self.subsystemPrefix} stats",
                                                     subsystem="", namespace=self.namespace)

    '''
    This function resets the stats that are scraped from external apis
    '''

    def reset(self):
        self.powerMetric = GaugeMetricFamily(self.build_name("watts", self.subsystemPrefix),
                                              f"{self.subsystemPrefix} measurement in watts",
                                              labels=self.powerLabels)

    def collect(self):
        time_start = time.time()

        logging.debug(f"Collecting {self.subsystemPrefix} stats")

        logging.debug("Resetting per-call metrics")
        self.reset()

        error_status = 0

        try:
            # this is where the api-scraping logic goes
            logging.debug("Collecting data for power")
            powers: [SensePower] = self.sense_client.powers

            for power in powers:
                labels = [power[label] for label in self.powerLabels]
                self.powerMetric.add_metric(
                    labels=labels, value=power.watts)

        except Exception as e:
            logging.error("Error while getting %s stats via client: %s", self.subsystemPrefix, e)
            error_status = 1
            self.scrapeErrorsTotalMetric.inc()

        self.scrapesTotalMetric.inc()
        self.lastScrapeErrorMetric.set(error_status)
        time_end = time.time()
        self.lastScrapeTimestampMetric.set(time_end)
        self.lastScrapeDurationSecondsMetric.set(time_end - time_start)

        return [self.powerMetric]
