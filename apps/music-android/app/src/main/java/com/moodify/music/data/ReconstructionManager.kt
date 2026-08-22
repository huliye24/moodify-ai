package com.moodify.music.data

import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

/**
 * P09 Reconstruction Manager — owns the client-side reconstruction lifecycle.
 *
 * Single source of truth for:
 *  - library of LocalTracks
 *  - active reconstruction jobs and their status
 *  - mapping between local URIs and tracks
 *
 * Thread-safe: all mutations happen through coroutine-safe methods.
 * UI observes via StateFlow.
 */
class ReconstructionManager(private val reconstructionClient: ReconstructionClient = ReconstructionClient()) {

    private val _tracks = MutableStateFlow<List<LocalTrack>>(emptyList())
    val tracks: StateFlow<List<LocalTrack>> = _tracks.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    // -----------------------------------------------------------------------
    // Track management
    // -----------------------------------------------------------------------

    /**
     * Add a track from a SAF content URI (user picked via ACTION_OPEN_DOCUMENT).
     */
    fun addTrack(uri: Uri, displayName: String): LocalTrack {
        val track = LocalTrack(
            localTrackId = "lt-${UUID.randomUUID().toString().take(8)}",
            displayName = displayName,
            contentUri = uri,
            mimeType = inferMimeType(displayName),
            reconstructionStatus = ReconstructionStatus.LOCAL_ONLY,
        )
        _tracks.value = _tracks.value + track
        return track
    }

    /**
     * Add a track from an external intent (ACTION_VIEW / SEND).
     */
    fun addExternalTrack(uri: Uri, displayName: String): LocalTrack =
        addTrack(uri, displayName)

    /**
     * Update status for a track (called after poll or submit response).
     */
    fun updateStatus(localTrackId: String, status: ReconstructionStatus) {
        _tracks.value = _tracks.value.map {
            if (it.localTrackId == localTrackId) it.copy(reconstructionStatus = status) else it
        }
    }

    fun updateJobBinding(localTrackId: String, jobId: String?, resultId: String? = null) {
        _tracks.value = _tracks.value.map {
            if (it.localTrackId == localTrackId) it.copy(
                reconstructionJobId = jobId,
                reconstructionResultId = resultId,
            ) else it
        }
    }

    // -----------------------------------------------------------------------
    // Reconstruction flow
    // -----------------------------------------------------------------------

    /**
     * Submit a track for cloud reconstruction.
     *
     * Idempotency key is generated per (trackId, attempt) to allow safe retry.
     */
    suspend fun submitReconstruction(localTrackId: String) {
        val track = _tracks.value.find { it.localTrackId == localTrackId } ?: return
        _isProcessing.value = true

        try {
            updateStatus(localTrackId, ReconstructionStatus.UPLOADING)

            val idempotencyKey = "recon-${track.localTrackId}-${System.currentTimeMillis()}"
            val response = reconstructionClient.submit(
                SubmitReconstructionRequest(
                    source = AudioAssetRef(
                        displayName = track.displayName,
                        mimeType = track.mimeType,
                        sha256 = track.sourceSha256IfAvailable,
                    ),
                    idempotencyKey = idempotencyKey,
                ),
            )

            if (response != null && response.status == "ACCEPTED") {
                updateJobBinding(localTrackId, response.jobId)
                updateStatus(localTrackId, ReconstructionStatus.RECONSTRUCTING)
                // Start polling
                pollUntilDone(localTrackId, response.jobId)
            } else {
                updateStatus(localTrackId, ReconstructionStatus.FAILED)
            }
        } catch (_: Exception) {
            updateStatus(localTrackId, ReconstructionStatus.FAILED)
        } finally {
            _isProcessing.value = false
        }
    }

    /**
     * Poll job status until terminal state.
     *
     * In production this should use exponential backoff + max attempts.
     * For v0.1 we do a simple loop with stub responses.
     */
    private suspend fun pollUntilDone(localTrackId: String, jobId: String) {
        repeat(MAX_POLL_ATTEMPTS) { attempt ->
            kotlinx.coroutines.delay(POLL_INTERVAL_MS)

            val status = reconstructionClient.pollStatus(jobId) ?: run {
                updateStatus(localTrackId, ReconstructionStatus.FAILED)
                return
            }

            when {
                status.phase in listOf("READY", "COMPLETED") -> {
                    when (status.outcome) {
                        "SOURCE_WINS" -> updateStatus(localTrackId, ReconstructionStatus.SOURCE_PRESERVED)
                        "CANDIDATE_READY" -> {
                            updateJobBinding(localTrackId, jobId, status.resultId)
                            updateStatus(localTrackId, ReconstructionStatus.READY)
                        }
                        "HUMAN_REQUIRED" -> updateStatus(localTrackId, ReconstructionStatus.HUMAN_REQUIRED)
                        "FAILED" -> updateStatus(localTrackId, ReconstructionStatus.FAILED)
                        else -> updateStatus(localTrackId, ReconstructionStatus.READY)
                    }
                    return
                }
                status.phase == "FAILED" || status.error != null -> {
                    updateStatus(localTrackId, ReconstructionStatus.FAILED)
                    return
                }
                // Still processing — continue polling
                status.phase in listOf("PREPARING", "LISTENING", "RECONSTRUCTING", "VERIFYING") -> {
                    updateStatus(localTrackId, ReconstructionStatus.RECONSTRUCTING)
                }
            }
        }
        // Exhausted polls
        updateStatus(localTrackId, ReconstructionStatus.RECONSTRUCTING) // still in-flight
    }

    companion object {
        const val MAX_POLL_ATTEMPTS = 60          // ~2 min at 2s intervals
        const val POLL_INTERVAL_MS = 2000L       // 2 seconds
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
private fun inferMimeType(fileName: String): String = when {
    fileName.endsWith(".mp3", ignoreCase = true) -> "audio/mpeg"
    fileName.endsWith(".wav", ignoreCase = true) -> "audio/wav"
    fileName.endsWith(".flac", ignoreCase = true) -> "audio/flac"
    fileName.endsWith(".m4a", ignoreCase = true) -> "audio/mp4"
    fileName.endsWith(".aac", ignoreCase = true) -> "audio/aac"
    fileName.endsWith(".ogg", ignoreCase = true) -> "audio/ogg"
    else -> "audio/*"
}
