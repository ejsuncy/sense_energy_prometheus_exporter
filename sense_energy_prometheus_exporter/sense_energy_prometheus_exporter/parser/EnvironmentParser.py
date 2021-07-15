import os
import logging
import re

from ..client.sense import SenseAccount
from ..constants import LogLevelOptions as loglevel, EnvironmentVariableKeys as envkey, defaults as appDefaults


class EnvironmentParser():

    @classmethod
    def parse_logging_config(cls, app):
        exporter_log_level_env = os.getenv(envkey.EXPORTER_LOG_LEVEL_KEY)
        if exporter_log_level_env:
            app.exporter_log_level = exporter_log_level_env
        else:
            app.exporter_log_level = appDefaults.exporter_log_level
        logging.basicConfig(level=loglevel.log_level_options.get(app.exporter_log_level),
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        logging.info("Log level set to: %s", app.exporter_log_level)

    @classmethod
    def parse_server_config(cls, app):
        exporter_port_env = os.getenv(envkey.EXPORTER_PORT_KEY)
        if exporter_port_env:
            logging.debug("Env var %s was set to %s", envkey.EXPORTER_PORT_KEY, exporter_port_env)
            app.exporter_port = exporter_port_env
        else:
            app.exporter_port = appDefaults.exporter_port

        exporter_bind_host_env = os.getenv(envkey.EXPORTER_BIND_HOST_KEY)
        if exporter_bind_host_env:
            logging.debug("Env var %s was set to %s", envkey.EXPORTER_BIND_HOST_KEY, exporter_bind_host_env)
            app.exporter_bind_host = exporter_bind_host_env
        else:
            app.exporter_bind_host = appDefaults.exporter_bind_host

        exporter_namespace_env = os.getenv(envkey.EXPORTER_NAMESPACE_KEY)
        if exporter_namespace_env:
            logging.debug("Env var %s was set to %s", envkey.EXPORTER_NAMESPACE_KEY, exporter_namespace_env)
            app.exporter_namespace = exporter_namespace_env
        else:
            app.exporter_namespace = appDefaults.exporter_namespace

    @classmethod
    def parse_sense_accounts(cls, app):
        accounts: [SenseAccount] = []

        sense_account_env_pattern = re.compile(f"{envkey.SENSE_ACCOUNT_NAME}(?P<index>\\d+)$")
        for key, value in os.environ.items():
            match = sense_account_env_pattern.match(key)

            if not match:
                continue

            index = str(match.group("index"))
            name = value
            username = os.getenv(f"{envkey.SENSE_ACCOUNT_USERNAME_KEY}{index}")
            password = os.getenv(f"{envkey.SENSE_ACCOUNT_PASSWORD_KEY}{index}")

            if not name:
                logging.warning(f"Found {key} but the value was blank. Skipping this account.")
                continue

            if not username:
                logging.warning(f"Found {key} but no valid username found in corresponding {envkey.SENSE_ACCOUNT_USERNAME_KEY}{index} var. Skipping this account.")
                continue

            if not password:
                logging.warning(f"Found {key} and associated username, but no valid password found in corresponding {envkey.SENSE_ACCOUNT_PASSWORD_KEY}{index} var. Skipping this account.")
                continue

            account = SenseAccount(
                name=value,
                username=username,
                password=password
            )

            accounts.append(account)

        app.sense_accounts = accounts
