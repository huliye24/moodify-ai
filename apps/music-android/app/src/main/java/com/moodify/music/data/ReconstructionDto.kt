package com.moodify.music.data

import kotlinx.serialization.Serializable

// ---------------------------------------------------------------------------
// P08 Cloud Reconstruction Job — API request / response DTOs
// Maps to P08 API contract (POST/GET /api/v1/reconstruction/jobs, etc.)
// ---------------------------------------------------------------------------

@Serializable
data class SubmitReconstructionRequest(
    val source: AudioAssetRef,
    val privacy: PrivacyPermissions = PrivacyPermissions(),
    val idempotencyKey: String,
)

@Serializable
data class AudioAssetRef(
    /** Client-provided label; not used as authoritative identity. */
    val displayName: String = "",
    /** SHA-256 of the audio body (optional pre-computed). */
    val sha256: String? = null,
    /** MIME type. */
    val mimeType: String = "",
)

@Serializable
data class PrivacyPermissions(
    val trainingPermission: Boolean = false,
    val publicDemoPermission: Boolean = false,
)

@Serializable
data class SubmitReconstructionResponse(
    val jobId: String,
    val status: String,          // "ACCEPTED" | "DEFERRED" | "REJECTED"
    val ownerToken: String? = null,   // short-lived auth token for this job
)

@Serializable
data class JobStatusResponse(
    val jobId: String,
    val phase: String,           // PREPARING | LISTENING | RECONSTRUCTING | VERIFYING | READY | COMPLETED
    val outcome: String? = null, // "SOURCE_WINS" | "CANDIDATE_READY" | "HUMAN_REQUIRED" | "FAILED"
    val candidateIds: List<String> = emptyList(),
    val resultId: String? = null,
    val error: String? = null,
)

@Serializable
data class ResultPlaybackInfo(
    val resultId: String,
    /** Short-lived authenticated URL for streaming the reconstructed audio. */
    val playbackUrl: String? = null,
    /** TTL seconds. */
    val ttlSeconds: Int = 0,
)
