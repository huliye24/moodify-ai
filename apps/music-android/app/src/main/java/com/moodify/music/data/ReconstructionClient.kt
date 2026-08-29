package com.moodify.music.data

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.UUID

/**
 * P09 Reconstruction Client — talks to P08 Cloud Reconstruction Job API.
 *
 * Responsibilities:
 *  - Submit a local track for reconstruction (POST /jobs)
 *  - Poll job status (GET /jobs/{id})
 *  - Obtain authenticated playback URL for result (GET /results/{id}/playback)
 *
 * Thread-safety: all methods are suspend and must be called from a coroutine
 * (typically Dispatchers.IO).
 *
 * Auth: uses owner-token returned on submit; tokens are NEVER logged or
 * persisted to disk beyond the in-memory session.
 */
class ReconstructionClient(
    private val baseUrl: String = DEFAULT_BASE_URL,
) {
    // TODO: inject real HTTP client (OkHttp / Ktor) when networking stack is decided.
    // For now this is a **stub** that demonstrates the contract and state machine.
    // P09_COMPLETE_WITH_BLOCKERS: real HTTP integration blocked on networking decision.

    /**
     * Submit a track for cloud reconstruction.
     *
     * @return SubmitReconstructionResponse on success; null on network/auth failure.
     */
    suspend fun submit(request: SubmitReconstructionRequest): SubmitReconstructionResponse? =
        withContext(Dispatchers.IO) {
            Log.d(TAG, "submit: idempotency=${request.idempotencyKey} displayName=${request.source.displayName}")

            // --- STUB ---
            // Real implementation:
            //   1. POST $baseUrl/api/v1/reconstruction/jobs with multipart body
            //   2. Parse SubmitReconstructionResponse
            //   3. Cache ownerToken in-memory only (never write to SecureStore / disk)
            //
            StubResponses.submitResponse(request.idempotencyKey)
        }

    /**
     * Poll current status of a reconstruction job.
     */
    suspend fun pollStatus(jobId: String): JobStatusResponse? =
        withContext(Dispatchers.IO) {
            Log.d(TAG, "pollStatus: jobId=$jobId")

            // --- STUB ---
            StubResponses.pollResponse(jobId)
        }

    /**
     * Get authenticated playback info for a reconstructed result.
     *
     * The returned URL is short-lived and MUST NOT be cached or shared.
     */
    suspend fun getResultPlayback(resultId: String, ownerToken: String?): ResultPlaybackInfo? =
        withContext(Dispatchers.IO) {
            Log.d(TAG, "getResultPlayback: resultId=$resultId")
            // ownerToken sent as Bearer; never logged.

            // --- STUB ---
            StubResponses.playbackInfo(resultId)
        }

    companion object {
        const val DEFAULT_BASE_URL = "https://rongjinwenchuan.xyz"
        private const val TAG = "ReconstructionClient"
    }
}

// ---------------------------------------------------------------------------
// Stub responses — removed once real HTTP client is wired.
// These allow unit tests and UI integration to proceed without server dependency.
// ---------------------------------------------------------------------------
private object StubResponses {
    fun submitResponse(idempotencyKey: String): SubmitReconstructionResponse =
        SubmitReconstructionResponse(
            jobId = "job-${UUID.randomUUID().toString().take(8)}",
            status = "ACCEPTED",
            ownerToken = "tok-stub-${UUID.randomUUID().toString().take(12)}",
        )

    fun pollResponse(jobId: String): JobStatusResponse =
        // Simulate progression: after first poll return RECONSTRUCTING, then READY.
        // In real code the server drives this.
        JobStatusResponse(
            jobId = jobId,
            phase = "READY",
            outcome = "SOURCE_WINS",
            resultId = null,
        )

    fun playbackInfo(resultId: String): ResultPlaybackInfo =
        ResultPlaybackInfo(
            resultId = resultId,
            playbackUrl = null,   // stub: no real URL
            ttlSeconds = 300,
        )
}
