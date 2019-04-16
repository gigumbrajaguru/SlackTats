from enum import Enum


class GitHubCapEnum(Enum):
    @classmethod
    def get_default(cls):
        raise NotImplementedError

    @classmethod
    def all_names(cls):
        return list(member_name for member_name in cls.__members__.keys())

    @classmethod
    def all_values(cls):
        return list(member.value for member in cls.__members__.values())

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, name):
        return cls.__members__[name]


class Filtering(GitHubCapEnum):
    ASSIGNED = 'assigned'
    CREATED = 'created'
    MENTIONED = 'mentioned'
    SUBSCRIBED = 'subscribed'
    ALL = 'all'

    @classmethod
    def get_default(cls):
        return cls.ALL


class State(GitHubCapEnum):
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'

    @classmethod
    def get_default(cls):
        return cls.ALL


class Sorting(GitHubCapEnum):
    CREATED = 'created'
    UPDATED = 'updated'
    COMMENTS = 'comments'

    @classmethod
    def get_default(cls):
        return cls.CREATED


class SortingDirection(GitHubCapEnum):
    ASC = 'asc'
    DESC = 'desc'

    @classmethod
    def get_default(cls):
        return cls.DESC
