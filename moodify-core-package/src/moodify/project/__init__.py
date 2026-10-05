"""Song Project — the persistent working object of a production.

Project Model 0.1 (``moodify.project/0.1``) is the minimum canonical
foundation: create a project from one source audio file, record the source as
a hashed asset, and reopen and re-verify it later. It coexists with the
existing :class:`moodify.contracts.ProductionCase` system and does not replace
it.
"""

from .errors import (
    ProjectError,
    ProjectExistsError,
    ProjectIntegrityError,
    ProjectValidationError,
)
from .models import (
    PROJECT_PROTOCOL,
    RESERVED_SECTIONS,
    AssetKind,
    ProjectAsset,
    ProjectManifest,
)
from .service import (
    MANIFEST_NAME,
    PROJECT_DIRECTORIES,
    create_project,
    load_project,
    project_root,
)

__all__ = [
    "AssetKind",
    "MANIFEST_NAME",
    "PROJECT_DIRECTORIES",
    "PROJECT_PROTOCOL",
    "RESERVED_SECTIONS",
    "ProjectAsset",
    "ProjectError",
    "ProjectExistsError",
    "ProjectIntegrityError",
    "ProjectManifest",
    "ProjectValidationError",
    "create_project",
    "load_project",
    "project_root",
]
