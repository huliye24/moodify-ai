# Plugin Development Guide

## Overview

Moodify Plugin Architecture enables developers to extend Moodify AI audio intelligence into any audio workflow.

## Plugin Types

| Type | Description | Example |
|------|-------------|---------|
| `audio-processing` | Real-time audio processing | VST/AU plugins |
| `analysis` | Audio analysis tools | Quality checker |
| `integration` | Third-party integrations | GitHub Action |
| `visualization` | Audio visualization | Waveform display |
| `automation` | Workflow automation | Batch processor |

## Plugin Architecture

```
┌─────────────────────────────────────────┐
│           Host Application              │
│     (DAW / Audio Editor / etc.)       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Moodify Plugin Layer          │
│         (VST3 / AU / Standalone)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Moodify Plugin SDK            │
│    (C++ / Python / JavaScript)        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Moodify AI Audio Engine          │
│   (Analysis / Processing / MRS)       │
└─────────────────────────────────────────┘
```

## Quick Start

### 1. Create Plugin Manifest

```json
{
  "name": "my-moodify-plugin",
  "version": "1.0.0",
  "type": "audio-processing",
  "engine": {
    "name": "moodify-core",
    "version": ">=1.0.0"
  },
  "permissions": ["audio:read", "mrs:evaluate"]
}
```

### 2. Implement Plugin Interface

**C++ (VST3)**:
```cpp
#include <moodify/plugin.h>

class MyPlugin : public MoodifyAudioProcessor {
public:
    void processBlock(AudioBuffer& buffer) override {
        // Get MRS score
        auto score = moodify_->evaluate(buffer);
        
        // Process based on score
        if (score.overall < threshold_) {
            enhance(buffer);
        }
    }
};
```

**Python**:
```python
from moodify import Plugin

class MyPlugin(Plugin):
    def process(self, audio):
        score = self.moodify.evaluate(audio)
        if score.overall < 70:
            return self.enhance(audio)
        return audio
```

### 3. Build and Package

```bash
# C++ / JUCE
mkdir build && cd build
cmake ..
make

# Package
moodify-plugin package --output MyPlugin.vst3
```

### 4. Publish to Marketplace

```bash
moodify-plugin publish \
  --plugin plugin.json \
  --binary MyPlugin.vst3 \
  --docs docs/
```

## Plugin Manifest

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Plugin identifier |
| `version` | string | Semantic version |
| `type` | string | Plugin type |
| `engine` | object | Moodify engine requirements |
| `permissions` | array | Required permissions |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Plugin description |
| `author` | object | Author information |
| `license` | string | SPDX license identifier |
| `entry_points` | object | Binary locations |
| `parameters` | array | UI parameters |
| `presets` | object | Preset locations |
| `ui` | object | UI configuration |
| `pricing` | object | Pricing tiers |

## Permissions

| Permission | Description |
|------------|-------------|
| `audio:read` | Read audio data |
| `audio:write` | Write audio data |
| `mrs:evaluate` | Evaluate MRS score |
| `analysis:run` | Run analysis |
| `preset:load` | Load presets |
| `preset:save` | Save presets |
| `network:http` | HTTP requests |
| `filesystem:read` | Read files |
| `filesystem:write` | Write files |

## SDKs

### C++ SDK

**Installation**:
```bash
# Clone SDK
git clone https://github.com/huliye24/moodify-plugin-sdk-cpp.git

# Build
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
```

**Usage**:
```cpp
#include <moodify/plugin.h>

class MyPlugin : public MoodifyAudioProcessor {
public:
    void prepareToPlay(double sampleRate, int samplesPerBlock) override {
        moodify_->initialize(sampleRate, samplesPerBlock);
    }
    
    void processBlock(AudioBuffer& buffer) override {
        auto result = moodify_->analyze(buffer);
        // Use result.features, result.mrs_score
    }
};
```

### Python SDK

**Installation**:
```bash
pip install moodify-plugin-sdk
```

**Usage**:
```python
from moodify.plugin import AudioProcessor

class MyPlugin(AudioProcessor):
    def prepare(self, sample_rate, buffer_size):
        self.moodify.initialize(sample_rate, buffer_size)
    
    def process(self, audio_buffer):
        result = self.moodify.analyze(audio_buffer)
        return self.apply_processing(audio_buffer, result)
```

### JavaScript SDK

**Installation**:
```bash
npm install @moodify/plugin-sdk
```

**Usage**:
```javascript
import { MoodifyPlugin } from '@moodify/plugin-sdk';

class MyPlugin extends MoodifyPlugin {
  async process(audioBuffer) {
    const result = await this.moodify.analyze(audioBuffer);
    return this.applyProcessing(audioBuffer, result);
  }
}
```

## VST3 Plugin Development

### Project Structure

```
MyVSTPlugin/
├── CMakeLists.txt
├── plugin.json
├── src/
│   ├── PluginProcessor.cpp
│   ├── PluginProcessor.h
│   ├── PluginEditor.cpp
│   └── PluginEditor.h
├── resources/
│   └── icon.png
└── docs/
    └── README.md
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyVSTPlugin VERSION 1.0.0)

# Find Moodify SDK
find_package(MoodifyPluginSDK REQUIRED)

# JUCE
add_subdirectory(JUCE)

# Plugin
juce_add_plugin(MyVSTPlugin
    VERSION 1.0.0
    FORMATS VST3 AU Standalone
    PLUGIN_MANIFEST plugin.json
)

target_sources(MyVSTPlugin PRIVATE
    src/PluginProcessor.cpp
    src/PluginEditor.cpp
)

target_link_libraries(MyVSTPlugin PRIVATE
    Moodify::PluginSDK
    juce::juce_audio_utils
)
```

### PluginProcessor.h

```cpp
#pragma once
#include <JuceHeader.h>
#include <moodify/plugin.h>

class MyVSTPluginProcessor : public juce::AudioProcessor,
                             public MoodifyAudioProcessor {
public:
    MyVSTPluginProcessor();
    ~MyVSTPluginProcessor() override;
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    const juce::String getName() const override { return "MyVSTPlugin"; }
    
    // ... other required overrides
    
private:
    std::unique_ptr<MoodifyPlugin> moodify_;
    float mrsThreshold_ = 70.0f;
};
```

## Marketplace Publishing

### Submission Requirements

1. **Plugin Package**:
   - `plugin.json` (manifest)
   - Binaries (VST3, AU, etc.)
   - Documentation
   - Screenshots
   - License file

2. **Metadata**:
   - Name and description
   - Author information
   - Pricing
   - Support URL
   - Category and tags

3. **Quality**:
   - Pass automated tests
   - Security scan
   - Code review (for open source)

### Review Process

1. **Automated Checks**:
   - Manifest validation
   - Binary scanning
   - License verification

2. **Manual Review**:
   - Functionality test
   - UI/UX review
   - Documentation review

3. **Approval**:
   - Published to marketplace
   - Notification sent
   - Analytics enabled

## Pricing Models

### Free

```json
{
  "pricing": {
    "type": "free"
  }
}
```

### One-time Purchase

```json
{
  "pricing": {
    "type": "purchase",
    "price": 29.99,
    "currency": "USD"
  }
}
```

### Subscription

```json
{
  "pricing": {
    "type": "subscription",
    "tiers": [
      {
        "name": "basic",
        "price": 9.99,
        "interval": "monthly"
      },
      {
        "name": "pro",
        "price": 29.99,
        "interval": "monthly"
      }
    ]
  }
}
```

### Freemium

```json
{
  "pricing": {
    "type": "freemium",
    "tiers": [
      {
        "name": "free",
        "price": 0,
        "features": ["basic"]
      },
      {
        "name": "pro",
        "price": 19.99,
        "features": ["advanced", "unlimited"]
      }
    ]
  }
}
```

## Revenue Sharing

### Standard Split

| Party | Percentage |
|-------|-----------|
| Developer | 70% |
| Moodify | 20% |
| Payment Processing | 10% |

### Enterprise Split

| Party | Percentage |
|-------|-----------|
| Developer | 80% |
| Moodify | 15% |
| Payment Processing | 5% |

### Payout Schedule

- Monthly payouts
- Minimum threshold: $50
- Payment methods: PayPal, Bank Transfer

## Best Practices

### Performance

- Use async processing where possible
- Cache analysis results
- Minimize UI thread blocking
- Optimize memory usage

### User Experience

- Clear parameter labels
- Responsive UI
- Progress indicators
- Helpful error messages

### Security

- Validate all inputs
- Use HTTPS for API calls
- Sanitize file paths
- No hardcoded credentials

### Documentation

- Clear README
- API documentation
- Usage examples
- Troubleshooting guide

## Support

### Developer Resources

- Documentation: https://docs.moodify.ai/plugins
- Forum: https://forum.moodify.ai
- Discord: https://discord.gg/moodify
- GitHub: https://github.com/huliye24/moodify-plugin-sdk

### Contact

- Developer Support: developers@moodify.ai
- Partnerships: partners@moodify.ai
- Security: security@moodify.ai

## License

Copyright © 2024-2026 荣景文川
SPDX-License-Identifier: GPL-3.0-only
