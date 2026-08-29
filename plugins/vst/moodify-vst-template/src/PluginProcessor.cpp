#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
MoodifyVSTTemplateAudioProcessor::MoodifyVSTTemplateAudioProcessor()
    : AudioProcessor(BusesProperties()
                       #if !JucePlugin_IsMidiEffect
                        #if !JucePlugin_IsSynth
                         .withInput("Input", juce::AudioChannelSet::stereo(), true)
                        #endif
                         .withOutput("Output", juce::AudioChannelSet::stereo(), true)
                       #endif
                       )
{
    // Initialize parameters
    addParameter(mrsThresholdParam = new juce::AudioParameterFloat(
        "mrsThreshold",
        "MRS Threshold",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        70.0f,
        juce::AudioParameterFloatAttributes()
            .withLabel("score")
    ));

    addParameter(autoProcessParam = new juce::AudioParameterBool(
        "autoProcess",
        "Auto Process",
        false
    ));

    addParameter(analysisModeParam = new juce::AudioParameterChoice(
        "analysisMode",
        "Analysis Mode",
        juce::StringArray({"Quick", "Standard", "Detailed"}),
        1
    ));

    // Initialize Moodify SDK (future)
    // moodifyPlugin_ = std::make_unique<moodify::Plugin>();
}

MoodifyVSTTemplateAudioProcessor::~MoodifyVSTTemplateAudioProcessor()
{
}

//==============================================================================
void MoodifyVSTTemplateAudioProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    currentSampleRate_ = sampleRate;
    currentBlockSize_ = samplesPerBlock;

    // Prepare analysis buffer
    analysisBuffer_.setSize(getTotalNumInputChannels(), samplesPerBlock);

    // Initialize Moodify SDK (future)
    // if (moodifyPlugin_) {
    //     moodifyPlugin_->initialize(sampleRate, samplesPerBlock);
    // }
}

void MoodifyVSTTemplateAudioProcessor::releaseResources()
{
    // Release resources
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool MoodifyVSTTemplateAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    #if JucePlugin_IsMidiEffect
        juce::ignoreUnused(layouts);
        return true;
    #else
        if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
            && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
            return false;

        #if !JucePlugin_IsSynth
        if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
            return false;
        #endif

        return true;
    #endif
}
#endif

void MoodifyVSTTemplateAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ignoreUnused(midiMessages);

    const int totalNumInputChannels = getTotalNumInputChannels();
    const int totalNumOutputChannels = getTotalNumOutputChannels();

    // Copy input to analysis buffer
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        analysisBuffer_.copyFrom(channel, 0, buffer, channel, 0, buffer.getNumSamples());
    }

    // Get current parameters
    mrsThreshold_ = mrsThresholdParam->get();
    autoProcess_ = autoProcessParam->get();

    // Evaluate MRS (placeholder implementation)
    if (autoProcess_)
    {
        lastMRSResult_ = evaluateMRS();

        // Auto-process if below threshold
        if (lastMRSResult_ < mrsThreshold_)
        {
            // Future: Apply Moodify enhancement
            // moodifyPlugin_->enhance(buffer);

            // Placeholder: Simple gain boost
            for (int channel = 0; channel < totalNumOutputChannels; ++channel)
            {
                buffer.applyGain(channel, 0, buffer.getNumSamples(), 1.1f);
            }
        }
    }

    // Clear unused output channels
    for (int i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear(i, 0, buffer.getNumSamples());
}

//==============================================================================
float MoodifyVSTTemplateAudioProcessor::evaluateMRS()
{
    // Future: Call Moodify SDK
    // if (moodifyPlugin_) {
    //     auto result = moodifyPlugin_->evaluate(analysisBuffer_);
    //     features_ = result.features;
    //     return result.overall;
    // }

    // Placeholder: Calculate simple metric
    float rms = 0.0f;
    for (int channel = 0; channel < analysisBuffer_.getNumChannels(); ++channel)
    {
        rms += analysisBuffer_.getRMSLevel(channel, 0, analysisBuffer_.getNumSamples());
    }
    rms /= analysisBuffer_.getNumChannels();

    // Convert to pseudo-MRS score (0-100)
    float score = juce::jlimit(0.0f, 100.0f, rms * 1000.0f);

    features_["rms"] = rms;
    features_["score"] = score;

    return score;
}

void MoodifyVSTTemplateAudioProcessor::setMRSThreshold(float threshold)
{
    mrsThreshold_ = juce::jlimit(0.0f, 100.0f, threshold);
    mrsThresholdParam->storeValue(mrsThreshold_, juce::dontSendNotification);
}

//==============================================================================
juce::AudioProcessorEditor* MoodifyVSTTemplateAudioProcessor::createEditor()
{
    return new MoodifyVSTTemplateAudioProcessorEditor(*this);
}

bool MoodifyVSTTemplateAudioProcessor::hasEditor() const
{
    return true;
}

//==============================================================================
const juce::String MoodifyVSTTemplateAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool MoodifyVSTTemplateAudioProcessor::acceptsMidi() const
{
    #if JucePlugin_WantsMidiInput
        return true;
    #else
        return false;
    #endif
}

bool MoodifyVSTTemplateAudioProcessor::producesMidi() const
{
    #if JucePlugin_ProducesMidiOutput
        return true;
    #else
        return false;
    #endif
}

bool MoodifyVSTTemplateAudioProcessor::isMidiEffect() const
{
    #if JucePlugin_IsMidiEffect
        return true;
    #else
        return false;
    #endif
}

double MoodifyVSTTemplateAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

//==============================================================================
int MoodifyVSTTemplateAudioProcessor::getNumPrograms()
{
    return 1;
}

int MoodifyVSTTemplateAudioProcessor::getCurrentProgram()
{
    return 0;
}

void MoodifyVSTTemplateAudioProcessor::setCurrentProgram(int index)
{
    juce::ignoreUnused(index);
}

const juce::String MoodifyVSTTemplateAudioProcessor::getProgramName(int index)
{
    juce::ignoreUnused(index);
    return {};
}

void MoodifyVSTTemplateAudioProcessor::changeProgramName(int index, const juce::String& newName)
{
    juce::ignoreUnused(index, newName);
}

//==============================================================================
void MoodifyVSTTemplateAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    // Save state
    auto state = std::make_unique<juce::XmlElement>("MoodifyVSTTemplate");
    state->setAttribute("mrsThreshold", mrsThreshold_);
    state->setAttribute("autoProcess", autoProcess_);

    copyXmlToBinary(*state, destData);
}

void MoodifyVSTTemplateAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    // Restore state
    auto state = getXmlFromBinary(data, sizeInBytes);

    if (state != nullptr)
    {
        if (state->hasTagName("MoodifyVSTTemplate"))
        {
            mrsThreshold_ = (float)state->getDoubleAttribute("mrsThreshold", 70.0);
            autoProcess_ = state->getBoolAttribute("autoProcess", false);
        }
    }
}

//==============================================================================
// This creates new instances of the plugin
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new MoodifyVSTTemplateAudioProcessor();
}
