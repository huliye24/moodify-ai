package com.moodify.music.data

import android.net.Uri
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * P09 ReconstructionManager tests.
 * Verifies track lifecycle, status transitions, and job binding.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class ReconstructionManagerTest {

    private lateinit var manager: ReconstructionManager

    @Before
    fun setUp() {
        manager = ReconstructionManager()
    }

    @Test
    fun `initial state is empty`() {
        val tracks = manager.tracks.value
        assertTrue(tracks.isEmpty())
        assertFalse(manager.isProcessing.value)
    }

    @Test
    fun `addTrack creates LOCAL_ONLY entry`() = runTest {
        val uri = Uri.parse("content://test/song.mp3")
        val track = manager.addTrack(uri, "song.mp3")

        assertEquals("song.mp3", track.displayName)
        assertEquals(ReconstructionStatus.LOCAL_ONLY, track.reconstructionStatus)
        assertEquals(1, manager.tracks.value.size)
        assertSame(track, manager.tracks.value[0])
    }

    @Test
    fun `addExternalTrack also adds to library`() = runTest {
        val uri = Uri.parse("content://external/audio.wav")
        val track = manager.addExternalTrack(uri, "audio.wav")

        assertEquals("audio.wav", track.displayName)
        assertEquals(1, manager.tracks.value.size)
    }

    @Test
    fun `addMultipleTracks accumulates`() = runTest {
        manager.addTrack(Uri.parse("content://a"), "a.mp3")
        manager.addTrack(Uri.parse("content://b"), "b.flac")
        manager.addTrack(Uri.parse("content://c"), "c.wav")
        assertEquals(3, manager.tracks.value.size)
    }

    @Test
    fun `updateStatus changes only target track`() = runTest {
        val t1 = manager.addTrack(Uri.parse("content://1"), "1.mp3")
        val t2 = manager.addTrack(Uri.parse("content://2"), "2.mp3")

        manager.updateStatus(t1.localTrackId, ReconstructionStatus.RECONSTRUCTING)

        assertEquals(ReconstructionStatus.RECONSTRUCTING, manager.tracks.value[0].reconstructionStatus)
        assertEquals(ReconstructionStatus.LOCAL_ONLY, manager.tracks.value[1].reconstructionStatus) // unchanged
    }

    @Test
    fun `updateJobBinding sets jobId and resultId`() = runTest {
        val track = manager.addTrack(Uri.parse("content://test"), "test.mp3")

        manager.updateJobBinding(track.localTrackId, "job-001", "res-001")

        val updated = manager.tracks.value[0]
        assertEquals("job-001", updated.reconstructionJobId)
        assertEquals("res-001", updated.reconstructionResultId)
    }

    @Test
    fun `status progression through lifecycle`() = runTest {
        val track = manager.addTrack(Uri.parse("content://lifecycle"), "lifecycle.mp3")

        // Simulate the full happy path
        manager.updateStatus(track.localTrackId, ReconstructionStatus.UPLOADING)
        assertEquals(ReconstructionStatus.UPLOADING, manager.tracks.value[0].reconstructionStatus)

        manager.updateStatus(track.localTrackId, ReconstructionStatus.RECONSTRUCTING)
        assertEquals(ReconstructionStatus.RECONSTRUCTING, manager.tracks.value[0].reconstructionStatus)

        manager.updateJobBinding(track.localTrackId, "job-lifecycle", "res-lifecycle")
        manager.updateStatus(track.localTrackId, ReconstructionStatus.READY)
        assertEquals(ReconstructionStatus.READY, manager.tracks.value[0].reconstructionStatus)
        assertEquals("res-lifecycle", manager.tracks.value[0].reconstructionResultId)
    }

    @Test
    fun `SOURCE_WINS is a terminal success state`() = runTest {
        val track = manager.addTrack(Uri.parse("content://sourcewins"), "sourcewins.mp3")
        manager.updateStatus(track.localTrackId, ReconstructionStatus.SOURCE_PRESERVED)
        assertEquals(ReconstructionStatus.SOURCE_PRESERVED, manager.tracks.value[0].reconstructionStatus)
    }

    @Test
    fun `HUMAN_REQUIRED is a terminal blocked state`() = runTest {
        val track = manager.addTrack(Uri.parse("content://human"), "human.mp3")
        manager.updateStatus(track.localTrackId, ReconstructionStatus.HUMAN_REQUIRED)
        assertEquals(ReconstructionStatus.HUMAN_REQUIRED, manager.tracks.value[0].reconstructionStatus)
    }
}
