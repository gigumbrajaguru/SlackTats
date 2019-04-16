import os
import attr
import yaml
import logging
import contextlib

from .exceptions import ConfigNotFound
from .exceptions import ConfigurationError

_LOG = logging.getLogger(__name__)
_DEFAULT_CONFIG_DIR = '/etc'
_CONFIG_FILE_PATH = os.path.join(os.getenv('HOME', _DEFAULT_CONFIG_DIR), 'config.yaml')


@attr.s(slots=True)
class _ConfigurationSingleton(object):
    headers = attr.ib(default=attr.Factory(dict), type=dict)
    user = attr.ib(default=None, type=str)
    password = attr.ib(default=None, type=str)
    token = attr.ib(default=None, type=str)
    per_page_listing = attr.ib(default=100, type=int)
    github_api = attr.ib(default=os.getenv('GITHUB_API', 'https://api.github.com'), type=str)
    omit_rate_limiting = attr.ib(default=True, type=bool)
    pagination = attr.ib(default=True, type=bool)
    validate_schemas = attr.ib(default=True, type=bool)

    @per_page_listing.validator
    def per_page_listing_validator(self, _, value):
        if not 1 <= value <= 100:
            raise ConfigurationError("Page listing has to be between 1 and 100.")

    @contextlib.contextmanager
    def temporary_change(self, **adjusted_options):
        option_backup = {}
        config = Configuration()

        for option, value in adjusted_options.items():
            option_backup[option] = getattr(config, option)
            setattr(Configuration(), option, value)

        yield option_backup

        for option, value in option_backup.items():
            setattr(config, option, value)

    @classmethod
    def from_config_file(cls):
        try:
            with open(_CONFIG_FILE_PATH) as config_file:
                configuration = yaml.load(config_file)
        except FileNotFoundError as exc:
            raise ConfigNotFound("No configuration present in {!s}".format(_CONFIG_FILE_PATH)) from exc
        except Exception as exc:
            raise ConfigurationError("Unable to open configuration: {!s}".format(str(exc))) from exc

        try:
            return cls(**configuration)
        except Exception as exc:
            raise ConfigurationError("Failed to initialize configuration: {!s}".format(str(exc))) from exc

    @classmethod
    def get_configuration(cls):
        try:
            return cls.from_config_file()
        except ConfigNotFound as exc:
            _LOG.debug("Fallback to default configuration: {!s}".format(str(exc)))

        return cls()


class Configuration(object):
    _instance = None

    __slots__ = []

    def __init__(self, **kwargs):
        if Configuration._instance is None:
            Configuration._instance = _ConfigurationSingleton.get_configuration()

        for key, value in kwargs.items():
            setattr(Configuration._instance, key, value)

    def __str__(self):
        return str(Configuration._instance)

    def __repr__(self):
        return repr(Configuration._instance)

    def __getattr__(self, item):
        if item == 'instance':
            return self._instance

        try:
            return getattr(Configuration._instance, item)
        except AttributeError as exc:
            raise ConfigurationError("Unknown configuration option '{!s}'".format(item)) from exc

    def __setattr__(self, key, value):
        if key == '_instance':
            return super().__setattr__(key, value)
        try:
            return setattr(Configuration._instance, key, value)
        except AttributeError as exc:
            raise ConfigurationError("Unknown configuration option '{!s}'".format(key)) from exc
