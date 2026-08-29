package com.moodify.music.player

import org.json.JSONObject

/**
 * W01-P06 delivery client: resolves READY track -> authorized playback metadata.
 *
 * Pure logic (org.json only) so it is JVM-testable without a device.
 * The client never receives cloud credentials; it only holds a short-TTL signed URI
 * that can be refreshed via [refresh] without reprocessing (DLV-INV-02/06).
 */
data class PlaybackMetadata(
    val trackId: String,
    val renderObjectId: String,
    val title: String,
    val durationMs: Long,
    val container: String,
    val codec: String,
    val sampleRate: Int,
    val channels: Int,
    val contentLength: Long,
    val playbackUri: String,
    val uriExpiresAt: Long,
    val supportsRange: Boolean,
    val etag: String,
) {
    companion object {
        fun from(json: JSONObject): PlaybackMetadata = PlaybackMetadata(
            trackId = json.optString("track_id"),
            renderObjectId = json.optString("render_object_id"),
            title = json.optString("title"),
            durationMs = json.optLong("duration_ms", 0L),
            container = json.optString("container"),
            codec = json.optString("codec"),
            sampleRate = json.optInt("sample_rate", 0),
            channels = json.optInt("channels", 0),
            contentLength = json.optLong("content_length", 0L),
            playbackUri = json.optString("playback_uri"),
            uriExpiresAt = json.optLong("uri_expires_at", 0L),
            supportsRange = json.optBoolean("supports_range", true),
            etag = json.optString("etag"),
        )
    }
}

enum class DeliveryFailure(val code: String) {
    TRACK_NOT_READY("TRACK_NOT_READY"),
    TRACK_NOT_FOUND("TRACK_NOT_FOUND"),
    ACCESS_DENIED("ACCESS_DENIED"),
    DELIVERY_URI_EXPIRED("DELIVERY_URI_EXPIRED"),
    DELIVERY_URI_INVALID("DELIVERY_URI_INVALID"),
    NETWORK_UNAVAILABLE("NETWORK_UNAVAILABLE"),
    NETWORK_TIMEOUT("NETWORK_TIMEOUT"),
    RANGE_NOT_SUPPORTED("RANGE_NOT_SUPPORTED"),
    OBJECT_NOT_FOUND("OBJECT_NOT_FOUND"),
    UNSUPPORTED_MEDIA("UNSUPPORTED_MEDIA"),
    DECODER_ERROR("DECODER_ERROR"),
    AUDIO_FOCUS_LOST("AUDIO_FOCUS_LOST"),
    PLAYER_INTERNAL_ERROR("PLAYER_INTERNAL_ERROR"),
    UNKNOWN_PLAYBACK_ERROR("UNKNOWN_PLAYBACK_ERROR"),
}

/**
 * Resolves READY tracks to playable URIs and refreshes expired URIs.
 * `fetcher` is injected so tests can simulate success/expiry/network failures.
 */
class PlaybackDeliveryClient(
    private val fetcher: (String) -> JSONObject,
    private val nowMillis: () -> Long = System::currentTimeMillis,
) {
    fun resolve(trackId: String): PlaybackMetadata =
        try {
            PlaybackMetadata.from(fetcher(trackId))
        } catch (e: DeliveryException) {
            // Already a structured delivery failure: preserve its code (DLV failure isolation),
            // do not re-derive it from message text.
            throw e
        } catch (e: Exception) {
            throw DeliveryException.fromJson(e)
        }

    fun isExpired(meta: PlaybackMetadata): Boolean = nowMillis() > meta.uriExpiresAt

    fun refresh(trackId: String): PlaybackMetadata = resolve(trackId)

    fun playbackError(code: String): DeliveryFailure =
        DeliveryFailure.entries.firstOrNull { it.code == code } ?: DeliveryFailure.UNKNOWN_PLAYBACK_ERROR
}

class DeliveryException(val failure: DeliveryFailure, message: String) : Exception(message) {
    companion object {
        fun fromJson(e: Exception): DeliveryException {
            // JSONObject has no structured code; map by message where possible.
            val message = e.message ?: ""
            return when {
                "TRACK_NOT_READY" in message -> DeliveryException(DeliveryFailure.TRACK_NOT_READY, message)
                "TRACK_NOT_FOUND" in message -> DeliveryException(DeliveryFailure.TRACK_NOT_FOUND, message)
                "ACCESS_DENIED" in message -> DeliveryException(DeliveryFailure.ACCESS_DENIED, message)
                else -> DeliveryException(DeliveryFailure.UNKNOWN_PLAYBACK_ERROR, message)
            }
        }
    }
}
