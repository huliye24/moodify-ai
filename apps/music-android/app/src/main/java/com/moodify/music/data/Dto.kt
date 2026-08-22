package com.moodify.music.data

import org.json.JSONObject

/** Public Music client DTOs shared in meaning with the Web client contract. */
data class ApiError(val code: String, val message: String, val requestId: String) {
    companion object {
        fun from(json: JSONObject): ApiError {
            val error = json.optJSONObject("error") ?: JSONObject()
            return ApiError(
                code = error.optString("code", "UNKNOWN"),
                message = error.optString("message", "unknown error"),
                requestId = error.optString("request_id", ""),
            )
        }
    }
}

data class Track(
    val id: String,
    val title: String,
    val creatorId: String,
    val creatorHandle: String?,
    val status: String,
    val primaryLanguage: String?,
    val durationMs: Long?,
    val publishedAt: String?,
    val audioAssetKey: String?,
    val externalUri: String? = null,
) {
    companion object {
        fun from(json: JSONObject): Track {
            val version = json.optJSONObject("version")
            return Track(
                id = json.optString("id"),
                title = json.optString("title"),
                creatorId = json.optString("creator_id"),
                creatorHandle = json.optString("creator_handle", "").ifEmpty { null },
                status = json.optString("status", "draft"),
                primaryLanguage = json.optString("primary_language", "").ifEmpty { null },
                durationMs = if (json.has("duration_ms") && !json.isNull("duration_ms")) json.optLong("duration_ms") else null,
                publishedAt = json.optString("published_at", "").ifEmpty { null },
                audioAssetKey = version?.optString("audio_asset_key", "")?.ifEmpty { null },
                externalUri = null,
            )
        }
    }
}

data class Catalogue(val tracks: List<Track>) {
    companion object {
        fun from(json: JSONObject): Catalogue = Catalogue(buildList {
            val array = json.optJSONArray("tracks") ?: return@buildList
            for (index in 0 until array.length()) add(Track.from(array.getJSONObject(index)))
        })
    }
}

data class Bootstrap(val userId: String?, val capabilities: Map<String, Boolean>) {
    companion object {
        fun from(json: JSONObject): Bootstrap {
            val capabilities = json.optJSONObject("capabilities") ?: JSONObject()
            return Bootstrap(
                userId = json.optString("id", "").ifEmpty { null },
                capabilities = mapOf(
                    "account_actions" to capabilities.optBoolean("account_actions", false),
                    "creator_writes" to capabilities.optBoolean("creator_writes", false),
                ),
            )
        }
    }
}
