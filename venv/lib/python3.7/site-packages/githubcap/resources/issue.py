import attr
from githubcap.base import GitHubHandlerBase
from githubcap.base import GitHubBase
from githubcap.enums import State
from githubcap.schemas import validate_response
from githubcap.schemas import ISSUE_SCHEMA


@attr.s
class Issue(GitHubBase):
    pass


@attr.s
class IssueHandler(GitHubHandlerBase):
    title = attr.ib(type=str)
    body = attr.ib(type=str)
    milestone = attr.ib(type=int, default=None)
    labels = attr.ib(type=list, default=attr.Factory(list))
    assignees = attr.ib(type=list, default=attr.Factory(list))
    state = attr.ib(default=State.get_default(), type=State)

    @staticmethod
    def _check_and_instantiate(response):
        validate_response(ISSUE_SCHEMA, response)
        # TODO: report not-changed values
        # TODO: return instance
        return response

    @classmethod
    def by_id(cls, organization, project, number):
        uri = 'repos/{org!s}/{project!s}/issues/{number:d}'.format(org=organization, project=project, number=number)
        response, _ = cls.get(uri)
        return cls._check_and_instantiate(response)

    def create(self, organization, project):
        uri = 'repos/{org!s}/{project!s}/issues'.format(org=organization, project=project)
        payload = {key: value for key, value in attr.asdict(self).items() if value is not None}
        response, _ = self.post(uri, payload=payload)
        return self._check_and_instantiate(response)

    def modify(self, organization, project, number):
        uri = 'repos/{org!s}/{project!s}/issues/{number:d}'.format(org=organization, project=project, number=number)
        payload = {key: value for key, value in attr.asdict(self).items() if value is not None}
        response, _ = self.patch(uri, payload=payload)
        # TODO: report not-changed values
        return self._check_and_instantiate(response)
