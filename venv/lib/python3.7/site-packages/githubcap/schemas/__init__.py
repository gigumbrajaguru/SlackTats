from githubcap import Configuration
from .issue import ISSUE_SCHEMA
from .user import USER_SCHEMA
from .label import LABEL_SCHEMA
from .milestone import MILESTONE_SCHEMA


def validate_response(validator, response):
    if Configuration().validate_schemas:
        validator(response)

    return response
