cmake_minimum_required(VERSION 3.15)
project(MoodifyVSTTemplate VERSION 1.0.0)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find JUCE
if(NOT DEFINED JUCE_DIR)
    set(JUCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../JUCE")
endif()

add_subdirectory(${JUCE_DIR} JUCE)

# Find Moodify SDK
if(NOT DEFINED MOODIFY_SDK_DIR)
    set(MOODIFY_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../sdk")
endif()

# Plugin configuration
set(PLUGIN_NAME "MoodifyVSTTemplate")
set(PLUGIN_VERSION "1.0.0")
set(PLUGIN_MANUFACTURER "Moodify")
set(PLUGIN_MANUFACTURER_CODE "Mood")
set(PLUGIN_CODE "Mood")

# Create plugin
juce_add_plugin(${PLUGIN_NAME}
    VERSION ${PLUGIN_VERSION}
    COMPANY_NAME ${PLUGIN_MANUFACTURER}
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD TRUE
    PLUGIN_MANUFACTURER_CODE ${PLUGIN_MANUFACTURER_CODE}
    PLUGIN_CODE ${PLUGIN_CODE}
    FORMATS VST3 AU Standalone
    PRODUCT_NAME "Moodify VST Template"
)

# Source files
target_sources(${PLUGIN_NAME} PRIVATE
    src/PluginProcessor.cpp
    src/PluginProcessor.h
    src/PluginEditor.cpp
    src/PluginEditor.h
)

# Include directories
target_include_directories(${PLUGIN_NAME} PRIVATE
    ${MOODIFY_SDK_DIR}/cpp/include
    src
)

# Compile definitions
target_compile_definitions(${PLUGIN_NAME} PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
)

# Link libraries
target_link_libraries(${PLUGIN_NAME} PRIVATE
    juce::juce_audio_utils
    juce::juce_audio_processors
    juce::juce_gui_extra
    juce::juce_dsp
)

# Moodify SDK (future)
# target_link_libraries(${PLUGIN_NAME} PRIVATE
#     Moodify::PluginSDK
# )

# macOS specific
if(APPLE)
    set_target_properties(${PLUGIN_NAME} PROPERTIES
        XCODE_ATTRIBUTE_CLANG_LINK_OBJC_RUNTIME NO
    )
endif()

# Windows specific
if(WIN32)
    set_target_properties(${PLUGIN_NAME} PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
    )
endif()

# Install targets
install(TARGETS ${PLUGIN_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Package
set(CPACK_PACKAGE_NAME ${PLUGIN_NAME})
set(CPACK_PACKAGE_VERSION ${PLUGIN_VERSION})
set(CPACK_PACKAGE_VENDOR ${PLUGIN_MANUFACTURER})
include(CPack)
