# Moodify VST3 Plugin Template

Official template for creating Moodify VST3/AU plugins.

## Features

- JUCE 7 framework
- Moodify SDK integration
- MRS evaluation
- Audio analysis
- Preset system
- Cross-platform (Windows, macOS, Linux)

## Requirements

- CMake 3.15+
- C++17 compiler
- JUCE 7.0.0+
- Moodify Plugin SDK

## Quick Start

### 1. Clone Template

```bash
git clone https://github.com/huliye24/moodify-vst-template.git my-plugin
cd my-plugin
```

### 2. Configure

Edit `plugin.json`:
```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "author": "Your Name"
}
```

### 3. Build

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
```

### 4. Install

```bash
# macOS
cp -r MyPlugin.vst3 ~/Library/Audio/Plug-Ins/VST3/

# Windows
copy MyPlugin.vst3 "C:\Program Files\Common Files\VST3\"

# Linux
cp -r MyPlugin.vst3 ~/.vst3/
```

## Project Structure

```
my-plugin/
├── CMakeLists.txt          # Build configuration
├── plugin.json             # Plugin manifest
├── src/
│   ├── PluginProcessor.cpp  # Audio processing
│   ├── PluginProcessor.h
│   ├── PluginEditor.cpp     # UI
│   └── PluginEditor.h
├── resources/
│   └── icon.png
├── presets/
│   └── default.json
└── docs/
    └── README.md
```

## Customization

### Add Parameters

In `PluginProcessor.h`:
```cpp
AudioParameterFloat* mrsThresholdParam;
```

In constructor:
```cpp
addParameter(mrsThresholdParam = new AudioParameterFloat(
    "mrsThreshold",
    "MRS Threshold",
    0.0f, 100.0f, 70.0f
));
```

### Process Audio

```cpp
void MyPluginAudioProcessor::processBlock(
    AudioBuffer<float>& buffer,
    MidiBuffer& midiMessages
) {
    // Get MRS threshold
    float threshold = mrsThresholdParam->get();

    // Evaluate audio
    auto result = moodify_->evaluate(buffer);

    // Process if needed
    if (result.overall < threshold) {
        moodify_->enhance(buffer);
    }
}
```

### Create UI

In `PluginEditor.cpp`:
```cpp
MyPluginAudioProcessorEditor::MyPluginAudioProcessorEditor(
    MyPluginAudioProcessor& p
) : AudioProcessorEditor(&p), processor(p) {
    // Add threshold slider
    thresholdSlider.setSliderStyle(Slider::Rotary);
    thresholdSlider.setRange(0.0, 100.0);
    thresholdSlider.setValue(70.0);
    addAndMakeVisible(thresholdSlider);

    // Add MRS display
    mrsLabel.setText("MRS: --", dontSendNotification);
    addAndMakeVisible(mrsLabel);

    setSize(400, 300);
}
```

## Building

### Debug Build

```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
```

### Release Build

```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release
```

### Universal Binary (macOS)

```bash
cmake -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" ..
cmake --build .
```

## Testing

### Load in DAW

1. Build plugin
2. Install to VST3 directory
3. Open DAW (Ableton, Logic, etc.)
4. Scan for plugins
5. Load plugin on audio track

### Debug

```bash
# macOS
lldb /Applications/Ableton\ Live\ 11\ Suite.app
(lldb) run
```

## Distribution

### Package

```bash
# Create installer package
mkdir -p MyPlugin-1.0.0/{VST3,AU,Standalone}
cp -r build/MyPlugin.vst3 MyPlugin-1.0.0/VST3/
cp -r build/MyPlugin.component MyPlugin-1.0.0/AU/
zip -r MyPlugin-1.0.0.zip MyPlugin-1.0.0/
```

### Submit to Marketplace

```bash
moodify-plugin publish \
  --plugin plugin.json \
  --binaries build/ \
  --docs docs/
```

## API Reference

### MoodifyPlugin

```cpp
class MoodifyPlugin {
    // Initialize
    void initialize(double sampleRate, int samplesPerBlock);

    // Analysis
    AnalysisResult analyze(const AudioBuffer& buffer);

    // Evaluation
    MRSResult evaluate(const AudioBuffer& buffer);

    // Processing
    void enhance(AudioBuffer& buffer);
    void reconstruct(AudioBuffer& buffer);
};
```

### AnalysisResult

```cpp
struct AnalysisResult {
    float duration;
    int sampleRate;
    std::map<std::string, float> features;
    std::map<std::string, float> spectral;
    std::map<std::string, float> temporal;
};
```

### MRSResult

```cpp
struct MRSResult {
    float overall;    // 0-100
    float fidelity;   // 0-100
    float balance;    // 0-100
    float clarity;    // 0-100
    std::string version;
};
```

## Troubleshooting

### Plugin Not Showing

- Check VST3 path
- Rescan plugins in DAW
- Check plugin validation

### Build Errors

- Update CMake
- Update JUCE
- Check C++17 support

### Runtime Crashes

- Check sample rate
- Verify buffer sizes
- Enable debug logging

## Support

- Documentation: https://docs.moodify.ai/plugins/vst
- Forum: https://forum.moodify.ai
- Issues: https://github.com/huliye24/moodify-vst-template/issues

## License

Copyright © 2024-2026 荣景文川
SPDX-License-Identifier: GPL-3.0-only
