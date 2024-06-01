import logging
import pprint
from datetime import datetime
from enum import Enum

from sense_energy import Senseable

from ..constants import TimeConstants


class SenseAccount(object):
    def __init__(self, name: str, username: str, password: str):
        self._name: str = name
        self._username: str = username
        self._password: str = password
        self._senseable: Senseable = Senseable()
        self._last_auth_time: datetime = None

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def name(self) -> str:
        return self._name

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def senseable(self) -> Senseable:
        return self._senseable

    @property
    def last_auth_time(self) -> datetime:
        return self._last_auth_time

    def should_authenticate(self) -> bool:
        if not self.last_auth_time:
            return True

        elapsed = datetime.now() - self.last_auth_time
        return elapsed.total_seconds() > (TimeConstants.authentication_duration_min * 60)

    def authenticate(self) -> None:
        self.senseable.authenticate(
            self.username,
            self.password
        )

        self._last_auth_time = datetime.now()


class SenseDevice(object):
    def __init__(self, account=None, name=None, watts=0):
        self._account = account
        self._name = name
        self._watts = watts

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def watts(self):
        return self._watts

    @property
    def name(self):
        return self._name

    @property
    def account(self):
        return self._account

    @classmethod
    def from_api(cls, account, account_devices: [object]):
        logging.debug("Converting sense api devices: %s", pprint.pformat(account_devices))
        devices: [SenseDevice] = []

        for account_device in account_devices:
            devices.append(SenseDevice(account, account_device['name'], account_device['w']))

        return devices


class SenseCurrent(object):
    def __init__(self, account=None, name=None, amps=0.0):
        self._account = account
        self._name = name
        self._amps = amps

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def amps(self):
        return self._amps

    @property
    def name(self):
        return self._name

    @property
    def account(self):
        return self._account

    @classmethod
    def from_api(cls, account, name, account_current: float):
        logging.debug("Converting sense api current: %s", pprint.pformat(account_current))
        return SenseCurrent(account, name, account_current)


class SenseFrequency(object):
    def __init__(self, account=None, name=None, hertz=0.0):
        self._account = account
        self._name = name
        self._hertz = hertz

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def hertz(self):
        return self._hertz

    @property
    def name(self):
        return self._name

    @property
    def account(self):
        return self._account

    @classmethod
    def from_api(cls, account, name, account_frequency: float):
        logging.debug("Converting sense api frequency: %s", pprint.pformat(account_frequency))
        return SenseFrequency(account, name, account_frequency)


class SensePower(object):
    def __init__(self, account=None, name=None, watts=0.0):
        self._account = account
        self._name = name
        self._watts = watts

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def watts(self):
        return self._watts

    @property
    def name(self):
        return self._name

    @property
    def account(self):
        return self._account

    @classmethod
    def from_api(cls, account, name, account_power: float):
        logging.debug("Converting sense api power: %s", pprint.pformat(account_power))
        return SensePower(account, name, account_power)


class SenseVoltage(object):
    def __init__(self, account=None, name=None, phase=0, volts=0.0):
        self._account = account
        self._name = name
        self._phase = str(phase)
        self._volts = volts

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def phase(self):
        return self._phase

    @property
    def volts(self):
        return self._volts

    @property
    def name(self):
        return self._name

    @property
    def account(self):
        return self._account

    @classmethod
    def from_api(cls, account, name, account_voltage: [float]):
        logging.debug("Converting sense api voltage: %s", pprint.pformat(account_voltage))

        return [
            SenseVoltage(account, name, phase_index, phase_voltage)
            for phase_index, phase_voltage in enumerate(account_voltage, 1)
        ]


class SenseTrendPeriod:
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SenseTrendType:
    PRODUCTION = "production"
    CONSUMPTION = "consumption"


class SenseTrend(object):

    def __init__(self, account=None, period=None, type=None, kwh=0.0):
        self._account = account
        self._period = period
        self._type = type
        self._kwh = kwh

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def kwh(self):
        return self._kwh

    @property
    def account(self):
        return self._account

    @property
    def period(self) -> SenseTrendPeriod:
        return self._period

    @property
    def type(self) -> SenseTrendType:
        return self._type


class SenseClient(object):
    def __init__(self, accounts: [SenseAccount]):
        self._accounts: [SenseAccount] = accounts

    def add_accounts(self, accounts: [SenseAccount]) -> None:
        self._accounts.extend(accounts)

    @property
    def accounts(self) -> [SenseAccount]:
        return self._accounts

    @property
    def devices(self) -> [SenseDevice]:
        devices: [SenseDevice] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_realtime()
                account_devices = account.senseable.devices
            except Exception as e:
                logging.error("Unable to retrieve devices from Sense account name %s: %s", account.name, e)
                continue

            devices.extend(SenseDevice.from_api(account.name, account_devices))

        return devices

    @property
    def currents(self) -> [SenseCurrent]:
        currents: [SenseCurrent] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_realtime()
                realtime = account.senseable.get_realtime()
                account_current = realtime['c']
                account_current_solar = None
                if 'solar_c' in realtime.keys():
                    account_current_solar = realtime['solar_c']
            except Exception as e:
                logging.error("Unable to retrieve current info from Sense account name %s: %s", account.name, e)
                continue

            currents.append(SenseCurrent.from_api(account.name, "main", account_current))

            if account_current_solar:
                currents.append(SenseCurrent.from_api(account.name, "solar", account_current_solar))

        return currents

    @property
    def frequencies(self) -> [SenseFrequency]:
        frequencies: [SenseFrequency] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_realtime()
                account_frequency = account.senseable.active_frequency
                account_frequency_solar = None
                realtime = account.senseable.get_realtime()
                if 'solar_hz' in realtime.keys():
                    account_frequency_solar = realtime['solar_hz']
            except Exception as e:
                logging.error("Unable to retrieve frequency info from Sense account name %s: %s", account.name, e)
                continue

            frequencies.append(SenseFrequency.from_api(account.name, "main", account_frequency))

            if account_frequency_solar:
                frequencies.append(SenseFrequency.from_api(account.name, "solar", account_frequency_solar))

        return frequencies

    @property
    def powers(self) -> [SensePower]:
        powers: [SensePower] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_realtime()
                power = account.senseable.active_power
                solar_power = account.senseable.active_solar_power
                active_devices = account.senseable.get_realtime()['devices']
            except Exception as e:
                logging.error("Unable to retrieve power info from Sense account name %s: %s", account.name, e)
                continue

            powers.append(SensePower.from_api(account.name, "main", power))
            powers.append(SensePower.from_api(account.name, "solar", solar_power))

            for d in active_devices:
                powers.append(SensePower.from_api(account.name, d['name'], d['w']))

        return powers

    @property
    def voltages(self) -> [SenseVoltage]:
        voltages: [SenseVoltage] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_realtime()
                voltage = account.senseable.active_voltage
                voltage_solar = None
                realtime = account.senseable.get_realtime()
                if 'solar_voltage' in realtime.keys():
                    voltage_solar = realtime['solar_voltage']
            except Exception as e:
                logging.error("Unable to retrieve voltage info from Sense account name %s: %s", account.name, e)
                continue

            voltages.extend(SenseVoltage.from_api(account.name, "main", voltage))

            if voltage_solar:
                voltages.extend(SenseVoltage.from_api(account.name, "solar", voltage_solar))

        return voltages

    @property
    def trends(self) -> [SenseTrend]:
        trends: [SenseTrend] = []

        account: SenseAccount
        for account in self.accounts:
            if account.should_authenticate():
                account.authenticate()
            try:
                account.senseable.update_trend_data()
                daily_usage_trend = account.senseable.daily_usage
                daily_production_trend = account.senseable.daily_production
                weekly_usage_trend = account.senseable.weekly_usage
                weekly_production_trend = account.senseable.weekly_production
                monthly_usage_trend = account.senseable.monthly_usage
                monthly_production_trend = account.senseable.monthly_production
                yearly_usage_trend = account.senseable.yearly_usage
                yearly_production_trend = account.senseable.yearly_production

            except Exception as e:
                logging.error("Unable to retrieve trend info from Sense account name %s: %s", account.name, e)
                continue

            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.DAILY, SenseTrendType.CONSUMPTION, daily_usage_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.DAILY, SenseTrendType.PRODUCTION, daily_production_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.WEEKLY, SenseTrendType.CONSUMPTION, weekly_usage_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.WEEKLY, SenseTrendType.PRODUCTION, weekly_production_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.MONTHLY, SenseTrendType.CONSUMPTION, monthly_usage_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.MONTHLY, SenseTrendType.PRODUCTION, monthly_production_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.YEARLY, SenseTrendType.CONSUMPTION, yearly_usage_trend))
            trends.append(
                SenseTrend(account.name, SenseTrendPeriod.YEARLY, SenseTrendType.PRODUCTION, yearly_production_trend))

        return trends
