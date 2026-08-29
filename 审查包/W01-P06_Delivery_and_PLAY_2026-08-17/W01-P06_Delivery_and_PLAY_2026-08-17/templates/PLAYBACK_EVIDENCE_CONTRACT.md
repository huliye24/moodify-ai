# Playback Evidence Contract

## Events

- PLAY_REQUESTED
- PLAY_STARTED
- PLAY_PAUSED
- PLAY_RESUMED
- PLAY_ENDED
- PLAY_FAILED

## Safe Fields

- event_id
- playback_session_id
- track_id
- render_object_id/version
- timestamp
- safe playback position
- duration
- app version
- failure code
- correlation_id

## Do Not Collect By Default

- audio recording
- unnecessary hardware identifiers
- unrelated sensor data
- full signed URL
- cloud credentials
