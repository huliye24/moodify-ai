"""Project-domain failures.

Kept deliberately small: callers need to distinguish "you gave me something
that is not a project" from "this project no longer matches what it recorded".
"""

from __future__ import annotations


class ProjectError(Exception):
    """Base class for every project-domain failure."""


class ProjectValidationError(ProjectError):
    """The source, manifest or project layout is not a valid project."""


class ProjectExistsError(ProjectError):
    """A project directory already exists at the target location."""


class ProjectIntegrityError(ProjectError):
    """Persisted project content no longer matches its recorded digest."""
