# Moodify Cloud Capabilities

These runners expose third-party engines as isolated Moodify cloud
capabilities. They do not introduce another job queue or product state machine.
The canonical Moodify worker remains responsible for cases, retries, evidence,
verification, and human escalation.

## Basic Pitch

`basic_pitch_runner.sh INPUT_AUDIO OUTPUT_DIRECTORY` writes MIDI and note-event
CSV artifacts. The runtime is isolated at
`/opt/moodify/capabilities/basic-pitch/venv` because its TFLite build requires
NumPy 1.x while the canonical Moodify environment uses NumPy 2.x.

## MuseScore

`musescore_export_runner.sh INPUT_SCORE OUTPUT_FILE` converts MIDI, MusicXML, or
MuseScore input using a headless Qt platform. It runs without an audio device or
interactive display and has a bounded five-minute execution timeout.
