# Batch Action Contract

Batch actions consume visible selected Track IDs and return `{ total, succeeded, already_exists, skipped, failed }`. Items run independently; successes remain if another item fails. Supported: add Playlist, append Queue, favorite, unfavorite and remove Library.

Favorite/Queue/Playlist operations preserve selection. Library removal asks once with explicit original-file wording and clears selection after completion.
