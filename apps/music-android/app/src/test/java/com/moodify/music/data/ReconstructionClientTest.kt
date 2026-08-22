package com.moodify.music.data

import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * P09 ReconstructionClient stub tests.
 * Verifies the client contract and stub responses.
 * Once real HTTP is wired, these tests should be updated to use a mock server.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class ReconstructionClientTest {

    private val client = ReconstructionClient()

    @Test
    fun `submit returns ACCEPTED with jobId and token`() = runTest {
        val request = SubmitReconstructionRequest(
            source = AudioAssetRef(displayName = "test.mp3", mimeType = "audio/mpeg"),
            idempotencyKey = "idem-001",
        )
        val response = client.submit(request)

        assertNotNull(response)
        assertEquals("ACCEPTED", response!!.status)
        assertTrue(response.jobId.startsWith("job-"))
        assertNotNull(response.ownerToken)
        assertTrue(response.ownerToken!!.startsWith("tok-stub-"))
    }

    @Test
    fun `submit with different keys returns different jobs`() = runTest {
        val r1 = client.submit(SubmitReconstructionRequest(
            source = AudioAssetRef("a.mp3"), idempotencyKey = "key-1",
        ))
        val r2 = client.submit(SubmitReconstructionRequest(
            source = AudioAssetRef("b.flac"), idempotencyKey = "key-2",
        ))

        assertNotNull(r1)
        assertNotNull(r2)
        assertNotEquals(r1!!.jobId, r2!!.jobId)
    }

    @Test
    fun `pollStatus returns terminal state`() = runTest {
        val response = client.pollStatus("job-test")
        assertNotNull(response)
        // Stub always returns READY/SOURCE_WINS
        assertEquals("READY", response!!.phase)
        assertEquals("SOURCE_WINS", response.outcome)
    }

    @Test
    fun `getResultPlayback returns info`() = runTest {
        val info = client.getResultPlayback("res-001", "tok-001")
        assertNotNull(info)
        assertEquals("res-001", info!!.resultId)
        // Stub returns null URL (no real server)
        assertNull(info.playbackUrl)
        assertEquals(300, info.ttlSeconds)
    }

    @Test
    fun `privacy defaults to false`() {
        val perms = PrivacyPermissions()
        assertFalse(perms.trainingPermission)
        assertFalse(perms.publicDemoPermission)
    }
}
