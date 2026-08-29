# System Metadata Policy

Metadata comes from current `LibraryTrack` or existing catalogue Track: title, artist and local album. Empty values use `未知歌曲 / 未知艺术家 / 未知专辑`. Unicode is preserved. Duration/position are projected only when finite and positive; seek returns through W04.

No local path, source URL, Ear/Evidence/stem state, cloud internal workflow state, token or secret is exposed. Artwork is omitted because no reliable canonical artwork seam exists. Track/state change updates Media Session; cleanup sets metadata null and playback state none.
