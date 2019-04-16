import attr
from datetime import datetime

from githubcap.base import GitHubHandlerBase
from githubcap.enums import Filtering
from githubcap.enums import Sorting
from githubcap.enums import SortingDirection
from githubcap.enums import State
from githubcap.schemas import validate_response
from githubcap.schemas import ISSUE_SCHEMA


@attr.s
class IssuesHandler(GitHubHandlerBase):
    page = attr.ib(default=1, type=int)
    per_page = attr.ib(default=GitHubHandlerBase.DEFAULT_PER_PAGE, type=int)
    filter = attr.ib(default=Filtering.get_default(), type=Filtering)
    state = attr.ib(default=State.get_default(), type=State)
    labels = attr.ib(default=attr.Factory(list), type=list)
    sort = attr.ib(default=Sorting.get_default(), type=Sorting)
    direction = attr.ib(default=SortingDirection.get_default(), type=SortingDirection)
    since = attr.ib(default=None, type=datetime)
    milestone = attr.ib(default=attr.Factory(lambda: '*'), type=str)

    assignee = attr.ib(default=attr.Factory(lambda: '*'), type=str)
    creator = attr.ib(default=None, type=str)
    mentioned = attr.ib(default=None, type=str)

    @milestone.validator
    def milestone_validator(self, _, value):
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Integer representation of a milestone has to be non-negative integer")
        elif not isinstance(value, str) and value is not None:
            raise ValueError("Unknown milestone representation supplied {!r} of type {!s}".format(value, type(value)))

    def _get_query_string(self):
        ret = ''
        for key, value in attr.asdict(self).items():
            if key == 'since' and value is None:
                continue

            if key in ('assignee', 'creator', 'mentioned') and value is None:
                continue

            if key == 'labels':
                if not value:
                    continue
                value = ",".join(value)

            if ret:
                ret += '&'

            ret += '{!s}={!s}'.format(key, str(value) if value is not None else 'none')
        return ret

    def list_assigned_issues(self, organization=None):
        if organization:
            base_uri = 'orgs/{!s}/issues'.format(organization)
        else:
            base_uri = 'issues'

        for item in self._do_listing(base_uri):
            validate_response(ISSUE_SCHEMA, item)
            # TODO: yield instances
            yield item

    def list_issues(self, organization, project):
        base_uri = 'repos/{!s}/{!s}/issues'.format(organization, project)
        for item in self._do_listing(base_uri):
            validate_response(ISSUE_SCHEMA, item)
            # TODO: yield instances
            yield item
