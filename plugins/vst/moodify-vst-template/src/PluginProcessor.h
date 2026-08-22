#pragma once

#include <JuceHeader.h>

// Forward declarations for Moodify SDK (future)
namespace moodify {
    class Plugin;
    struct MRSResult;
    struct AnalysisResult;
}

//==============================================================================
/**
 * Moodify VST Template Audio Processor
 *
 * Main audio processing class that integrates with Moodify AI engine.
 */
class MoodifyVSTTemplateAudioProcessor : public juce::AudioProcessor
{
public:
    //==============================================================================
    MoodifyVSTTemplateAudioProcessor();
    ~MoodifyVSTTemplateAudioProcessor() override;

    //==============================================================================
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

    #ifndef JucePlugin_PreferredChannelConfigurations
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    #endif

    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    //==============================================================================
    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    //==============================================================================
    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram(int index) override;
    const juce::String getProgramName(int index) override;
    void changeProgramName(int index, const juce::String& newName) override;

    //==============================================================================
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    //==============================================================================
    // Moodify-specific methods

    /**
     * Evaluate MRS score for current audio buffer.
     * @return MRS score (0-100)
     */
    float evaluateMRS();

    /**
     * Get last MRS evaluation result.
     */
    float getLastMRSResult() const { return lastMRSResult_; }

    /**
     * Set MRS threshold for auto-processing.
     */
    void setMRSThreshold(float threshold);
    float getMRSThreshold() const { return mrsThreshold_; }

    /**
     * Enable/disable auto-processing.
     */
    void setAutoProcess(bool enabled) { autoProcess_ = enabled; }
    bool getAutoProcess() const { return autoProcess_; }

    /**
     * Get analysis features.
     */
    std::map<std::string, float> getFeatures() const { return features_; }

    //==============================================================================
    // Parameters
    juce::AudioParameterFloat* mrsThresholdParam;
    juce::AudioParameterBool* autoProcessParam;
    juce::AudioParameterChoice* analysisModeParam;

private:
    //==============================================================================
    // Moodify integration (future)
    // std::unique_ptr<moodify::Plugin> moodifyPlugin_;

    // State
    double currentSampleRate_ = 44100.0;
    int currentBlockSize_ = 512;
    float lastMRSResult_ = 0.0f;
    float mrsThreshold_ = 70.0f;
    bool autoProcess_ = false;
    std::map<std::string, float> features_;

    // Analysis buffer
    juce::AudioBuffer<float> analysisBuffer_;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MoodifyVSTTemplateAudioProcessor)
};
