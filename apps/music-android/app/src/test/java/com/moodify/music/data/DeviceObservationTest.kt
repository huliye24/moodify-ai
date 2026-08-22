package com.moodify.music.data

import android.media.AudioDeviceInfo
import org.junit.Assert.*
import org.junit.Test

/**
 * P09 DeviceObservation model tests.
 * Verifies the data class contract and default values.
 *
 * Note: observeDevice() requires a real Android Context (AudioManager).
 * Instrumented tests would be needed for full integration testing.
 */
class DeviceObservationTest {

    @Test
    fun `default observation is unknown`() {
        val obs = DeviceObservation()
        assertEquals(AudioDeviceInfo.TYPE_UNKNOWN, obs.outputRouteType)
        assertEquals("unknown", obs.outputRouteLabel)
        assertFalse(obs.isWired)
        assertFalse(obs.isBluetooth)
        assertEquals(0, obs.sampleRateHz)
        assertEquals(0, obs.channelCount)
    }

    @Test
    fun `wired headset observation`() {
        val obs = DeviceObservation(
            outputRouteType = AudioDeviceInfo.TYPE_WIRED_HEADSET,
            outputRouteLabel = "Wired Headset",
            isWired = true,
            isBluetooth = false,
            sampleRateHz = 44100,
            channelCount = 2,
        )
        assertEquals(AudioDeviceInfo.TYPE_WIRED_HEADSET, obs.outputRouteType)
        assertTrue(obs.isWired)
        assertFalse(obs.isBluetooth)
        assertEquals(44100, obs.sampleRateHz)
    }

    @Test
    fun `bluetooth A2DP observation`() {
        val obs = DeviceObservation(
            outputRouteType = AudioDeviceInfo.TYPE_BLUETOOTH_A2DP,
            outputRouteLabel = "BT Speaker",
            isWired = false,
            isBluetooth = true,
            sampleRateHz = 48000,
            channelCount = 2,
        )
        assertTrue(obs.isBluetooth)
        assertFalse(obs.isWired)
        assertEquals(48000, obs.sampleRateHz)
    }

    @Test
    fun `copy preserves unrelated fields`() {
        val original = DeviceObservation(
            outputRouteType = AudioDeviceInfo.TYPE_BUILTIN_SPEAKER,
            outputRouteLabel = "Speaker",
            isWired = false,
            isBluetooth = false,
            sampleRateHz = 44100,
            channelCount = 2,
        )
        val updated = original.copy(sampleRateHz = 48000)
        assertEquals(AudioDeviceInfo.TYPE_BUILTIN_SPEAKER, updated.outputRouteType) // preserved
        assertEquals(48000, updated.sampleRateHz) // changed
        assertEquals(44100, original.sampleRateHz) // unchanged
    }
}
