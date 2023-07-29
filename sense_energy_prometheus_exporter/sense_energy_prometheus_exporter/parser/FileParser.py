import logging
import os

from ..constants import EnvironmentVariableKeys as envkey, defaults as appDefaults

import yaml


class FileParser():

    @classmethod
    def parse_app_configs(cls, app):
        app_config_file_env = os.getenv(envkey.APP_CONFIG_FILE_KEY)
        if app_config_file_env:
            logging.debug("Env var %s was set to %s", envkey.APP_CONFIG_FILE_KEY, app_config_file_env)
            app.app_config_file = app_config_file_env
        else:
            app.app_config_file = appDefaults.app_config_file

        logging.info("App config file: %s", app.app_config_file)

        # parse yaml file
        try:
            with open(app.app_config_file, 'r') as config_file:
                try:
                    app_configs = yaml.load(config_file, Loader=yaml.FullLoader)
                    app.app_configs = app_configs
                except Exception as e:
                    logging.warning("Unable to parse app config file %s: %s.", app.app_config_file, e)
                    raise e
        except Exception as e:
            logging.warning("Unable to process app config file %s: %s. Skipping.", app.app_config_file, e)
