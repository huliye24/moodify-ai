package com.moodify.music.data

import android.content.Context
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.os.Build

/**
 * P09 Device Observation Seed — reads NON-SENSITIVE device output capabilities.
 *
 * This is intentionally minimal.  P09 does NOT:
 *   - run automatic EQ
 *   - build a Hardware Graph
 *   - profile the user's device
 *
 * It only records what Android APIs safely expose so that future layers
 * (P10+) can make device-aware rendering decisions.
 */
data class DeviceObservation(
    /** e.g. TYPE_WIRED_HEADSET, TYPE_BLUETOOTH_A2DP, TYPE_BUILTIN_SPEAKER. */
    val outputRouteType: Int = AudioDeviceInfo.TYPE_UNKNOWN,
    /** Human-readable label for the route type. */
    val outputRouteLabel: String = "unknown",
    /** true if the output is wired (headphones/line). */
    val isWired: Boolean = false,
    /** true if the output is Bluetooth. */
    val isBluetooth: Boolean = false,
    /** Sample rate reported by the primary output (0 = unknown). */
    val sampleRateHz: Int = 0,
    /** Channel count reported by the primary output (0 = unknown). */
    val channelCount: Int = 0,
)

/**
 * Snapshot the current device audio output configuration.
 *
 * Must be called on a thread that can query AudioManager (main thread preferred).
 */
fun observeDevice(context: Context): DeviceObservation {
    val am = context.getSystemService(Context.AUDIO_SERVICE) as? AudioManager
        ?: return DeviceObservation()

    // API 23+: getDevices for comm/output
    val devices: Array<AudioDeviceInfo>? = runCatching {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            @Suppress("DEPRECATION")
            am.getDevices(AudioManager.GET_DEVICES_OUTPUTS)
        } else null
    }.getOrNull()

    // Android does not expose a reliable general-purpose "currently selected"
    // output flag here. Keep this observation explicitly best-effort and use
    // the first reported output rather than inventing route authority.
    val active = devices?.firstOrNull()

    return DeviceObservation(
        outputRouteType = active?.type ?: AudioDeviceInfo.TYPE_UNKNOWN,
        outputRouteLabel = active?.productName?.toString() ?: "unknown",
        isWired = active?.type in WIRED_TYPES,
        isBluetooth = active?.type in BT_TYPES,
        sampleRateHz = runCatching {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
                @Suppress("DEPRECATION")
                am.getProperty(AudioManager.PROPERTY_OUTPUT_SAMPLE_RATE)?.toInt() ?: 0
            } else 0
        }.getOrDefault(0),
        channelCount = active?.channelCounts?.maxOrNull() ?: 0,
    )
}

private val WIRED_TYPES = setOf(
    AudioDeviceInfo.TYPE_WIRED_HEADSET,
    AudioDeviceInfo.TYPE_WIRED_HEADPHONES,
    AudioDeviceInfo.TYPE_USB_DEVICE,
    AudioDeviceInfo.TYPE_USB_ACCESSORY,
    AudioDeviceInfo.TYPE_LINE_ANALOG,
)

private val BT_TYPES = setOf(
    AudioDeviceInfo.TYPE_BLUETOOTH_A2DP,
    AudioDeviceInfo.TYPE_BLE_HEADSET,
    AudioDeviceInfo.TYPE_BLE_SPEAKER,
)
