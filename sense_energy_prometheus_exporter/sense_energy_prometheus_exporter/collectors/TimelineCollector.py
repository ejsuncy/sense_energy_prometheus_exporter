import time
import logging
import datetime
from .CustomCollector import CustomCollector
from ..client.sense import SenseClient
from prometheus_client.core import CounterMetricFamily, Counter, Gauge


class TimelineCollector(CustomCollector):
    eventMetric: Counter
    scrapesTotalMetric: Counter
    scrapeErrorsTotalMetric: Counter
    lastScrapeErrorMetric: Gauge
    lastScrapeTimestampMetric: Gauge
    lastScrapeDurationSecondsMetric: Gauge

    # the subsystem prefix is a name for the item type you are scraping
    subsystemPrefix: str = "timeline"

    # the set of labels that describe each of your items that you are scraping
    eventLabels: list[str] = ["account", "name", "type"]

    # This is the client that calls external apis for the items you want to scrape
    sense_client: SenseClient

    # Timestamp of last event processed.
    lastTimestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

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
        self.eventMetric = Counter("total", f"Total {self.subsystemPrefix} events",
                                   subsystem=f"{self.subsystemPrefix}_events",
                                   namespace=self.namespace,
                                   labelnames=self.eventLabels)

    def collect(self):
        time_start = time.time()

        logging.debug(f"Collecting {self.subsystemPrefix} stats")

        logging.debug("Resetting per-call metrics")

        error_status = 0

        new_timestamp = self.lastTimestamp
        try:
            # this is where the api-scraping logic goes
            logging.debug("Collecting data for timeline")
            events = self.sense_client.timeline

            for event in events:
                labels = [event[label] for label in self.eventLabels]
                if event.timestamp <= self.lastTimestamp:
                    # Initialize labels from past events, but do not increment.
                    self.eventMetric.labels(*labels).inc(0)
                    continue
                self.eventMetric.labels(*labels).inc()
                if event.timestamp > new_timestamp:
                    new_timestamp = event.timestamp

        except Exception as e:
            logging.error(
                "Error while getting %s stats via client: %s", self.subsystemPrefix, e
            )
            error_status = 1
            self.scrapeErrorsTotalMetric.inc()

        self.lastTimestamp = new_timestamp

        self.scrapesTotalMetric.inc()
        self.lastScrapeErrorMetric.set(error_status)
        time_end = time.time()
        self.lastScrapeTimestampMetric.set(time_end)
        self.lastScrapeDurationSecondsMetric.set(time_end - time_start)

        # Empty because this uses a static Counter for persistence of values.
        return []
