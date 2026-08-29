package com.moodify.music.data

import android.net.Uri

/**
 * P09 Local Track Model — lightweight client-side track representation.
 *
 * Does NOT mirror cloud ProductionCase.  Android only carries what it needs
 * for selection, playback, and reconstruction job binding.
 */
data class LocalTrack(
    val localTrackId: String,                    // UUIDv7 or similar
    val displayName: String,
    val artistIfAvailable: String = "",
    val albumIfAvailable: String = "",
    val artworkUriIfAvailable: Uri? = null,
    val contentUri: Uri,                         // SAF content:// URI (persisted)
    val durationMs: Long = 0L,                   // 0 = unknown / not yet probed
    val mimeType: String = "",
    val sourceSha256IfAvailable: String? = null,

    // --- reconstruction binding ---
    val reconstructionJobId: String? = null,
    val reconstructionResultId: String? = null,
    var reconstructionStatus: ReconstructionStatus = ReconstructionStatus.LOCAL_ONLY,
)

/**
 * P09 Track lifecycle states.
 *
 * These are the ONLY states the v0.1 UI exposes to the user.
 */
enum class ReconstructionStatus {
    LOCAL_ONLY,           // fresh local pick, never submitted
    UPLOADING,            // audio body uploading to cloud
    RECONSTRUCTING,       // cloud processing (Listen → Judge → Intervene → Verify)
    READY,                // reconstructed result available for playback
    SOURCE_PRESERVED,     // cloud decided original is better (SOURCE_WINS)
    FAILED,               // transient or permanent failure
    HUMAN_REQUIRED,       // cloud escalated — needs human judgment
}
