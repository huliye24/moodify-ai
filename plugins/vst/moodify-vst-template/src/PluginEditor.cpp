#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
MoodifyVSTTemplateAudioProcessorEditor::MoodifyVSTTemplateAudioProcessorEditor(
    MoodifyVSTTemplateAudioProcessor& p
) : AudioProcessorEditor(&p), processor(p)
{
    // Title
    titleLabel.setText("Moodify VST Template", juce::dontSendNotification);
    titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    titleLabel.setColour(juce::Label::textColourId, textColour);
    addAndMakeVisible(titleLabel);

    // Version
    versionLabel.setText("v1.0.0", juce::dontSendNotification);
    versionLabel.setFont(juce::Font(12.0f));
    versionLabel.setColour(juce::Label::textColourId, textColour.withAlpha(0.7f));
    addAndMakeVisible(versionLabel);

    // MRS Threshold Slider
    mrsThresholdSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    mrsThresholdSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    mrsThresholdSlider.setRange(0.0, 100.0, 0.1);
    mrsThresholdSlider.setValue(70.0);
    mrsThresholdSlider.setColour(juce::Slider::thumbColourId, accentColour);
    mrsThresholdSlider.setColour(juce::Slider::rotarySliderFillColourId, accentColour);
    addAndMakeVisible(mrsThresholdSlider);

    mrsThresholdLabel.setText("MRS Threshold", juce::dontSendNotification);
    mrsThresholdLabel.setFont(juce::Font(14.0f));
    mrsThresholdLabel.setColour(juce::Label::textColourId, textColour);
    addAndMakeVisible(mrsThresholdLabel);

    mrsThresholdValueLabel.setText("70.0", juce::dontSendNotification);
    mrsThresholdValueLabel.setFont(juce::Font(12.0f));
    mrsThresholdValueLabel.setColour(juce::Label::textColourId, textColour);
    mrsThresholdValueLabel.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(mrsThresholdValueLabel);

    // Auto Process Toggle
    autoProcessButton.setButtonText("Auto Process");
    autoProcessButton.setColour(juce::ToggleButton::tickColourId, accentColour);
    autoProcessButton.setColour(juce::ToggleButton::textColourId, textColour);
    addAndMakeVisible(autoProcessButton);

    // Analysis Mode
    analysisModeLabel.setText("Analysis Mode", juce::dontSendNotification);
    analysisModeLabel.setFont(juce::Font(14.0f));
    analysisModeLabel.setColour(juce::Label::textColourId, textColour);
    addAndMakeVisible(analysisModeLabel);

    analysisModeBox.addItem("Quick", 1);
    analysisModeBox.addItem("Standard", 2);
    analysisModeBox.addItem("Detailed", 3);
    analysisModeBox.setSelectedId(2);
    analysisModeBox.setColour(juce::ComboBox::backgroundColourId, foregroundColour);
    analysisModeBox.setColour(juce::ComboBox::textColourId, textColour);
    addAndMakeVisible(analysisModeBox);

    // MRS Score Display
    mrsScoreLabel.setText("MRS Score", juce::dontSendNotification);
    mrsScoreLabel.setFont(juce::Font(16.0f, juce::Font::bold));
    mrsScoreLabel.setColour(juce::Label::textColourId, textColour);
    addAndMakeVisible(mrsScoreLabel);

    mrsScoreValue.setText("--", juce::dontSendNotification);
    mrsScoreValue.setFont(juce::Font(48.0f, juce::Font::bold));
    mrsScoreValue.setColour(juce::Label::textColourId, accentColour);
    mrsScoreValue.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(mrsScoreValue);

    // Features Display
    featuresLabel.setText("Features", juce::dontSendNotification);
    featuresLabel.setFont(juce::Font(14.0f));
    featuresLabel.setColour(juce::Label::textColourId, textColour);
    addAndMakeVisible(featuresLabel);

    featuresText.setMultiLine(true);
    featuresText.setReadOnly(true);
    featuresText.setColour(juce::TextEditor::backgroundColourId, foregroundColour);
    featuresText.setColour(juce::TextEditor::textColourId, textColour);
    featuresText.setText("No analysis yet...");
    addAndMakeVisible(featuresText);

    // Set window size
    setSize(600, 500);

    // Start timer to update display
    startTimerHz(30);
}

MoodifyVSTTemplateAudioProcessorEditor::~MoodifyVSTTemplateAudioProcessorEditor()
{
    stopTimer();
}

//==============================================================================
void MoodifyVSTTemplateAudioProcessorEditor::paint(juce::Graphics& g)
{
    // Background gradient
    juce::ColourGradient gradient(
        backgroundColour, 0, 0,
        backgroundColour.darker(0.3f), 0, (float)getHeight(),
        false
    );
    g.setGradientFill(gradient);
    g.fillAll();

    // Draw accent line
    g.setColour(accentColour);
    g.fillRect(0, 0, getWidth(), 2);
}

void MoodifyVSTTemplateAudioProcessorEditor::resized()
{
    auto area = getLocalBounds().reduced(20);

    // Title area
    auto titleArea = area.removeFromTop(50);
    titleLabel.setBounds(titleArea.removeFromLeft(300));
    versionLabel.setBounds(titleArea.removeFromRight(100));

    area.removeFromTop(20);

    // Left column (controls)
    auto leftColumn = area.removeFromLeft(280);

    // MRS Threshold
    auto thresholdArea = leftColumn.removeFromTop(180);
    mrsThresholdLabel.setBounds(thresholdArea.removeFromTop(25));
    mrsThresholdSlider.setBounds(thresholdArea.removeFromTop(120));
    mrsThresholdValueLabel.setBounds(thresholdArea);

    leftColumn.removeFromTop(20);

    // Auto Process
    auto autoArea = leftColumn.removeFromTop(40);
    autoProcessButton.setBounds(autoArea);

    leftColumn.removeFromTop(20);

    // Analysis Mode
    auto modeArea = leftColumn.removeFromTop(60);
    analysisModeLabel.setBounds(modeArea.removeFromTop(25));
    analysisModeBox.setBounds(modeArea);

    area.removeFromLeft(20);

    // Right column (display)
    auto rightColumn = area;

    // MRS Score
    auto scoreArea = rightColumn.removeFromTop(150);
    mrsScoreLabel.setBounds(scoreArea.removeFromTop(30));
    mrsScoreValue.setBounds(scoreArea);

    rightColumn.removeFromTop(20);

    // Features
    featuresLabel.setBounds(rightColumn.removeFromTop(25));
    featuresText.setBounds(rightColumn);
}

//==============================================================================
void MoodifyVSTTemplateAudioProcessorEditor::updateMRS(float score)
{
    mrsScoreValue.setText(juce::String(score, 1), juce::dontSendNotification);

    // Update color based on score
    if (score >= 80.0f)
        mrsScoreValue.setColour(juce::Label::textColourId, juce::Colours::green);
    else if (score >= 60.0f)
        mrsScoreValue.setColour(juce::Label::textColourId, juce::Colours::orange);
    else
        mrsScoreValue.setColour(juce::Label::textColourId, juce::Colours::red);
}

void MoodifyVSTTemplateAudioProcessorEditor::updateFeatures(
    const std::map<std::string, float>& features
)
{
    juce::String text;
    for (const auto& [name, value] : features)
    {
        text += name + ": " + juce::String(value, 4) + "\n";
    }
    featuresText.setText(text);
}

//==============================================================================
void MoodifyVSTTemplateAudioProcessorEditor::timerCallback()
{
    // Update MRS display from processor
    float mrs = processor.getLastMRSResult();
    if (mrs > 0.0f)
    {
        updateMRS(mrs);
    }

    // Update features
    auto features = processor.getFeatures();
    if (!features.empty())
    {
        updateFeatures(features);
    }
}
