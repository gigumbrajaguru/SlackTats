from voluptuous import Schema, Required, Optional, Any, Url, Range, All
from githubcap.enums import State

from .user import USER_SCHEMA
from .label import LABEL_SCHEMA
from .milestone import MILESTONE_SCHEMA


ISSUE_SCHEMA = Schema({
  Required("id"): All(Range(min=1)),
  Required("url"): Url(),
  Required("repository_url"): Url(),
  Required("labels_url"): Url(),
  Required("comments_url"): Url(),
  Required("events_url"): Url(),
  Required("html_url"): Url(),
  Required("number"): int,
  Required("state"): Schema(Any(*State.all_values())),
  Required("title"): str,
  Required("body"): Schema(Any(str, None)),
  Required("user"): USER_SCHEMA,
  Required("locked"): bool,
  Required("comments"): All(Range(min=0)),
  Required("labels"): [
    LABEL_SCHEMA
  ],
  Required("author_association"): Schema(Any('OWNER', 'CONTRIBUTOR', 'NONE')),
  Optional("assignee"): object,
  Required("assignees"): [
    USER_SCHEMA
  ],
  Optional("closed_by"): Schema(Any(USER_SCHEMA, None)),
  Required("milestone"): Schema(Any(MILESTONE_SCHEMA, None)),
  Optional("pull_request"): Schema({  # if this is present, it's a pull request, otherwise an issue
    Required("url"): Url(),
    Required("html_url"): Url(),
    Required("diff_url"): Url(),
    Required("patch_url"): Url()
  }),
  Required("closed_at"): Schema(Any(str, None)),
  Required("created_at"): str,
  Required("updated_at"): str,
})
