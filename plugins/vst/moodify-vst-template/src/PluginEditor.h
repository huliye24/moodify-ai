#pragma once

#include <JuceHeader.h>

//==============================================================================
/**
 * Moodify VST Template UI Editor
 *
 * Provides user interface for the Moodify VST plugin.
 */
class MoodifyVSTTemplateAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    MoodifyVSTTemplateAudioProcessorEditor(class MoodifyVSTTemplateAudioProcessor&);
    ~MoodifyVSTTemplateAudioProcessorEditor() override;

    //==============================================================================
    void paint(juce::Graphics&) override;
    void resized() override;

    //==============================================================================
    // Update MRS display
    void updateMRS(float score);

    //==============================================================================
    // Update features display
    void updateFeatures(const std::map<std::string, float>& features);

private:
    //==============================================================================
    // Reference to processor
    class MoodifyVSTTemplateAudioProcessor& processor;

    //==============================================================================
    // UI Components
    juce::Slider mrsThresholdSlider;
    juce::Label mrsThresholdLabel;
    juce::Label mrsThresholdValueLabel;

    juce::ToggleButton autoProcessButton;
    juce::Label autoProcessLabel;

    juce::ComboBox analysisModeBox;
    juce::Label analysisModeLabel;

    juce::Label mrsScoreLabel;
    juce::Label mrsScoreValue;

    juce::Label featuresLabel;
    juce::TextEditor featuresText;

    juce::Label titleLabel;
    juce::Label versionLabel;

    //==============================================================================
    // Colors
    juce::Colour backgroundColour{ juce::Colour(0xFF1a1a2e) };
    juce::Colour foregroundColour{ juce::Colour(0xFF16213e) };
    juce::Colour accentColour{ juce::Colour(0xFFe94560) };
    juce::Colour textColour{ juce::Colour(0xFFeaeaea) };

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MoodifyVSTTemplateAudioProcessorEditor)
};
