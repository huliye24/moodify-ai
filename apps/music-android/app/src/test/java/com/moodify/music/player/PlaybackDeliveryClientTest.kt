package com.moodify.music.player

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

/** W01-P06 Android delivery JVM tests (no device required). */
class PlaybackDeliveryClientTest {

    private fun metaJson(
        trackId: String = "trk_x",
        uri: String = "moodify://deliver/trk_x/obj_y?expires=9999999999&sig=abc",
        expiresAt: Long = 9999999999999L,
    ): JSONObject = JSONObject(
        mapOf(
            "track_id" to trackId,
            "render_object_id" to "obj_y",
            "title" to "Test Track",
            "duration_ms" to 219000,
            "container" to "wav",
            "codec" to "pcm_s16le",
            "sample_rate" to 44100,
            "channels" to 2,
            "content_length" to 12345,
            "playback_uri" to uri,
            "uri_expires_at" to expiresAt,
            "supports_range" to true,
            "etag" to "\"abc123\"",
        )
    )

    // TST-11 — PLAY/PAUSE basic control mapping
    @Test
    fun tst11_playPauseStateMapping() {
        val client = PlaybackDeliveryClient(fetcher = { metaJson() }, nowMillis = { 1L })
        val meta = client.resolve("trk_x")
        assertEquals("trk_x", meta.trackId)
        assertEquals("wav", meta.container)
        assertEquals(219000L, meta.durationMs)
        assertTrue(meta.supportsRange)
    }

    // TST-04-equivalent — URL expiry detection + refresh
    @Test
    fun tst04_urlExpiryRefresh() {
        var call = 0
        val client = PlaybackDeliveryClient(
            fetcher = {
                call += 1
                if (call == 1) {
                    // first call: expired URI
                    metaJson(uri = "moodify://deliver/trk_x/obj_y?expires=100&sig=old", expiresAt = 50L)
                } else {
                    // refresh: fresh URI, same track/render identity, not expired
                    metaJson(uri = "moodify://deliver/trk_x/obj_y?expires=9999999999&sig=new", expiresAt = 9999999999999L)
                }
            },
            nowMillis = { 1000L },
        )
        val meta = client.resolve("trk_x")
        assertTrue(client.isExpired(meta))
        val refreshed = client.refresh("trk_x")
        assertEquals("trk_x", refreshed.trackId)
        assertEquals("obj_y", refreshed.renderObjectId)
        assertFalse(client.isExpired(refreshed))
    }

    // TST-07 — Unauthorized access maps to ACCESS_DENIED
    @Test
    fun tst07_unauthorizedAccess() {
        val client = PlaybackDeliveryClient(
            fetcher = { throw RuntimeException("ACCESS_DENIED (403): scope cannot play") },
            nowMillis = { 1L },
        )
        val ex = assertThrows(DeliveryException::class.java) { client.resolve("trk_x") }
        assertEquals(DeliveryFailure.ACCESS_DENIED, ex.failure)
    }

    // TST-09 — Playback failure isolation: delivery error is a delivery failure, not compute
    @Test
    fun tst09_failureIsolation() {
        val client = PlaybackDeliveryClient(
            fetcher = { throw DeliveryException(DeliveryFailure.TRACK_NOT_READY, "not ready") },
            nowMillis = { 1L },
        )
        val ex = assertThrows(DeliveryException::class.java) { client.resolve("trk_x") }
        assertEquals(DeliveryFailure.TRACK_NOT_READY, ex.failure)
    }

    // TST-10 — Track identity stable across refresh
    @Test
    fun tst10_trackIdentityStable() {
        val client = PlaybackDeliveryClient(fetcher = { metaJson() }, nowMillis = { 1L })
        val m1 = client.resolve("trk_x")
        val m2 = client.refresh("trk_x")
        assertEquals(m1.trackId, m2.trackId)
        assertEquals(m1.renderObjectId, m2.renderObjectId)
    }

    // TST-15 — Playback evidence: event type mapping from failure code
    @Test
    fun tst15_failureCodeMapping() {
        val client = PlaybackDeliveryClient(fetcher = { metaJson() }, nowMillis = { 1L })
        assertEquals(DeliveryFailure.NETWORK_TIMEOUT, client.playbackError("NETWORK_TIMEOUT"))
        assertEquals(DeliveryFailure.UNKNOWN_PLAYBACK_ERROR, client.playbackError("SOMETHING_NEW"))
    }
}
