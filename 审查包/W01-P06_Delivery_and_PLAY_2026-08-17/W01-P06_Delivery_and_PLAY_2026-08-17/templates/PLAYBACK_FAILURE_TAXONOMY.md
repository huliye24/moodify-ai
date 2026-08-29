# Playback Failure Taxonomy

| Code | Meaning | Retry | Server/Client | Notes |
|---|---|---:|---|---|
| TRACK_NOT_READY | Track not production-ready | false/manual | server | |
| TRACK_NOT_FOUND | Unknown Track | false | server | |
| ACCESS_DENIED | Actor cannot play | false | server | |
| DELIVERY_URI_EXPIRED | Temporary credential expired | true | client/server | refresh |
| DELIVERY_URI_INVALID | Delivery entry invalid | policy | client/server | |
| NETWORK_UNAVAILABLE | no network | true | client | |
| NETWORK_TIMEOUT | timeout | true | client | |
| RANGE_NOT_SUPPORTED | seek delivery problem | policy | client/server | |
| OBJECT_NOT_FOUND | final object missing | false/reconcile | server | |
| UNSUPPORTED_MEDIA | player cannot decode | false | client | |
| DECODER_ERROR | decode runtime error | policy | client | |
| AUDIO_FOCUS_LOST | interrupted | true/resume | client | |
| PLAYER_INTERNAL_ERROR | player engine error | policy | client | |
| UNKNOWN_PLAYBACK_ERROR | unclassified | policy | client | |

## Rule

This taxonomy is delivery/playback-specific and does not replace P04 compute failures.
