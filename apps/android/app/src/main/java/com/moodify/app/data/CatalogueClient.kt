package com.moodify.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/** Public Music catalogue DTOs — shared meaning with the Web client contract. */
data class CatalogueTrack(
    val id: String,
    val title: String,
    val creatorId: String,
    val creatorHandle: String?,
    val status: String,
    val primaryLanguage: String?,
    val durationMs: Long?,
    val publishedAt: String?,
    val audioAssetKey: String?,
) {
    companion object {
        fun from(json: JSONObject): CatalogueTrack {
            val version = json.optJSONObject("version")
            return CatalogueTrack(
                id = json.optString("id"),
                title = json.optString("title"),
                creatorId = json.optString("creator_id"),
                creatorHandle = json.optString("creator_handle", "").ifEmpty { null },
                status = json.optString("status", "draft"),
                primaryLanguage = json.optString("primary_language", "").ifEmpty { null },
                durationMs = if (json.has("duration_ms") && !json.isNull("duration_ms")) json.optLong("duration_ms") else null,
                publishedAt = json.optString("published_at", "").ifEmpty { null },
                audioAssetKey = version?.optString("audio_asset_key", "")?.ifEmpty { null },
            )
        }
    }
}

data class Catalogue(val tracks: List<CatalogueTrack>, val nextCursor: String? = null) {
    companion object {
        fun from(json: JSONObject): Catalogue = Catalogue(
            tracks = buildList {
                val array = json.optJSONArray("tracks") ?: return@buildList
                for (index in 0 until array.length()) add(CatalogueTrack.from(array.getJSONObject(index)))
            },
            nextCursor = json.optString("next_cursor", "").ifEmpty { null },
        )
    }
}

/**
 * Public Music BFF client — anonymous /api/v1/music only.
 * Never talks to PolarDB; never holds internal service keys.
 */
class CatalogueClient(private val baseUrl: String = "https://rongjinwenchuan.xyz/api/v1/music") {

    companion object {
        private const val CACHE = "moodify_music_catalogue"
        private const val CACHE_TRACKS = "playable_tracks"

        fun cached(context: Context): Catalogue? = runCatching {
            val raw = context.getSharedPreferences(CACHE, Context.MODE_PRIVATE)
                .getString(CACHE_TRACKS, null) ?: return null
            val array = JSONArray(raw)
            Catalogue(buildList {
                for (index in 0 until array.length()) add(CatalogueTrack.from(array.getJSONObject(index)))
            }).takeIf { it.tracks.isNotEmpty() }
        }.getOrNull()

        fun cache(context: Context, catalogue: Catalogue) {
            val array = JSONArray()
            catalogue.tracks.forEach { track ->
                array.put(JSONObject().apply {
                    put("id", track.id)
                    put("title", track.title)
                    put("creator_id", track.creatorId)
                    put("creator_handle", track.creatorHandle)
                    put("status", track.status)
                    put("primary_language", track.primaryLanguage)
                    put("duration_ms", track.durationMs)
                    put("published_at", track.publishedAt)
                    put("version", JSONObject().put("audio_asset_key", track.audioAssetKey))
                })
            }
            context.getSharedPreferences(CACHE, Context.MODE_PRIVATE)
                .edit().putString(CACHE_TRACKS, array.toString()).apply()
        }
    }

    fun catalogue(): Catalogue {
        val tracks = mutableListOf<CatalogueTrack>()
        var cursor: String? = null
        do {
            val suffix = if (cursor == null) {
                "/catalogue?limit=100"
            } else {
                "/catalogue?limit=100&cursor=${java.net.URLEncoder.encode(cursor, "UTF-8")}"
            }
            val page = Catalogue.from(getJson(suffix))
            tracks += page.tracks
            cursor = page.nextCursor
        } while (cursor != null)
        return Catalogue(tracks)
    }

    /**
     * Catalogue rows intentionally omit the media version. Resolve each public
     * track through its canonical detail endpoint before presenting it as
     * playable; this avoids inventing fallback media in the client.
     */
    fun playableCatalogue(): Catalogue = Catalogue(
        catalogue().tracks.mapNotNull { summary ->
            if (summary.audioAssetKey != null) summary
            else runCatching { track(summary.id) }.getOrNull()?.takeIf { it.audioAssetKey != null }
        }
    )

    fun track(id: String): CatalogueTrack = CatalogueTrack.from(getJson("/tracks/$id"))

    private fun getJson(path: String): JSONObject {
        val conn = URL("$baseUrl$path").openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 10_000
        conn.readTimeout = 15_000
        conn.setRequestProperty("Accept", "application/json")
        val status = conn.responseCode
        val body = (if (status in 200..299) conn.inputStream else conn.errorStream)
            ?.bufferedReader()?.use { it.readText() } ?: "{}"
        conn.disconnect()
        val json = JSONObject(if (body.isEmpty()) "{}" else body)
        if (status !in 200..299) throw ConnectionError.NotFound("catalogue unavailable ($status)")
        return json
    }
}
