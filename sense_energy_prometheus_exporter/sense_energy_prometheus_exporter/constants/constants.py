import logging


class EnvironmentVariableKeys():
    # Prometheus sense_energy_prometheus_exporter configs
    EXPORTER_PORT_KEY = "EXPORTER_PORT"
    EXPORTER_LOG_LEVEL_KEY = "EXPORTER_LOG_LEVEL"
    EXPORTER_BIND_HOST_KEY = "EXPORTER_BIND_HOST"
    EXPORTER_NAMESPACE_KEY = "EXPORTER_NAMESPACE"

    # application env configs
    APP_CONFIG_FILE_KEY = "CONFIG_FILE"
    SENSE_ACCOUNT_USERNAME_KEY = "SENSE_ACCOUNT_USERNAME_"
    SENSE_ACCOUNT_PASSWORD_KEY = "SENSE_ACCOUNT_PASSWORD_"
    SENSE_ACCOUNT_NAME = "SENSE_ACCOUNT_NAME_"

    # Collector config values.
    TIMELINE_NUM_ITEMS = "TIMELINE_NUM_ITEMS"


class LogLevelOptions():
    # Logging Options
    log_level_options = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARN,
        "ERROR": logging.ERROR
    }


class TimeConstants():
    # reauthenticate every 15 min
    authentication_duration_min = 15
