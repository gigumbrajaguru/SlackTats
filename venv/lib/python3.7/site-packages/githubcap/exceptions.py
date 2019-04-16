
class GithubcapException(Exception):
    """Base class for githubcap exception tree."""


class ConfigNotFound(GithubcapException):
    """Raised on non-existing configuration file."""


class ConfigurationError(GithubcapException):
    """Raised on invalid configuration."""


class MissingPassword(GithubcapException):
    """Raised when a user name is set but no password provided."""


class HTTPError(GithubcapException):
    """Raised on unrecoverable HTTP errors."""

    def __init__(self, message, status_code):
        super().__init__(message['message'])

        self.status_code = status_code
        self.raw_response = message
