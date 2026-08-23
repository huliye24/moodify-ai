package com.moodify.music.data

import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * P09 LocalTrack model tests.
 * Verifies the lightweight client-side track representation contract.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class LocalTrackTest {

    @Test
    fun `localTrack default values`() {
        val track = LocalTrack(
            localTrackId = "lt-abc123",
            displayName = "test.mp3",
            contentUri = android.net.Uri.parse("content://test"),
        )
        assertEquals("lt-abc123", track.localTrackId)
        assertEquals("test.mp3", track.displayName)
        assertEquals("", track.artistIfAvailable)
        assertEquals("", track.albumIfAvailable)
        assertNull(track.artworkUriIfAvailable)
        assertEquals(0L, track.durationMs)
        assertEquals("", track.mimeType)
        assertNull(track.sourceSha256IfAvailable)
        assertNull(track.reconstructionJobId)
        assertNull(track.reconstructionResultId)
        assertEquals(ReconstructionStatus.LOCAL_ONLY, track.reconstructionStatus)
    }

    @Test
    fun `localTrack with all fields`() {
        val uri = android.net.Uri.parse("content://com.test/audio/song.flac")
        val artworkUri = android.net.Uri.parse("content://com.test/art/cover.jpg")
        val track = LocalTrack(
            localTrackId = "lt-full-001",
            displayName = "Song Title",
            artistIfAvailable = "Artist Name",
            albumIfAvailable = "Album Name",
            artworkUriIfAvailable = artworkUri,
            contentUri = uri,
            durationMs = 210_000L,
            mimeType = "audio/flac",
            sourceSha256IfAvailable = "abcd1234",
            reconstructionJobId = "job-xyz",
            reconstructionResultId = "res-xyz",
            reconstructionStatus = ReconstructionStatus.READY,
        )
        assertEquals("Song Title", track.displayName)
        assertEquals("Artist Name", track.artistIfAvailable)
        assertEquals(210_000L, track.durationMs)
        assertEquals("audio/flac", track.mimeType)
        assertEquals("abcd1234", track.sourceSha256IfAvailable)
        assertEquals("job-xyz", track.reconstructionJobId)
        assertEquals(ReconstructionStatus.READY, track.reconstructionStatus)
    }

    @Test
    fun `localTrack copy preserves immutability`() {
        val original = LocalTrack(
            localTrackId = "lt-copy",
            displayName = "original.mp3",
            contentUri = android.net.Uri.parse("content://test"),
            reconstructionStatus = ReconstructionStatus.LOCAL_ONLY,
        )
        val updated = original.copy(reconstructionStatus = ReconstructionStatus.RECONSTRUCTING)
        assertNotSame(original, updated)
        assertEquals(ReconstructionStatus.LOCAL_ONLY, original.reconstructionStatus) // unchanged
        assertEquals(ReconstructionStatus.RECONSTRUCTING, updated.reconstructionStatus)
        assertEquals(original.localTrackId, updated.localTrackId) // preserved
    }
}
