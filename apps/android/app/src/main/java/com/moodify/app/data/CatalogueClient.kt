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
    val coverAssetKey: String?,
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
                coverAssetKey = version?.optString("cover_asset_key", "")?.ifEmpty { null },
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
class CatalogueClient(private val baseUrl: String = "https://play.rongjingmusic.com/api/v1/music") {

    companion object {
        private const val CACHE = "moodify_music_catalogue"
        private const val CACHE_TRACKS = "playable_tracks"

        /**
         * First-party works used by the internal listening bench when the
         * catalogue service is unavailable. This is a UI fallback, not a
         * second catalogue authority; a healthy BFF response is merged in.
         */
        fun internalTestCatalogue(): Catalogue = Catalogue(
            listOf(
                testTrack("wo-ceng-yaowang-yinhe-xingguang", "我曾遥望银河星光", 164_000),
                testTrack("bao-yu-ye", "暴雨夜", 249_000),
                testTrack("iron-banner-at-dawn", "Iron Banner at Dawn", 124_000),
                testTrack("clash-above-the-crimson-plain", "Clash Above the Crimson Plain", 192_000),
                testTrack("midnight-rooftops-in-the-rain", "Midnight Rooftops in the Rain", 164_000),
                testTrack("rain-over-old-roof-tiles", "Rain Over Old Roof Tiles", 181_000),
                testTrack("tea-steam-in-slow-motion", "Tea Steam In Slow Motion", 169_000),
            )
        )

        private fun testTrack(slug: String, title: String, durationMs: Long) = CatalogueTrack(
            id = "internal-$slug",
            title = title,
            creatorId = "rongjingwenchuan",
            creatorHandle = "荣景文川",
            status = "published",
            primaryLanguage = if (title.firstOrNull()?.code?.let { it > 127 } == true) "zh-CN" else "en",
            durationMs = durationMs,
            publishedAt = null,
            audioAssetKey = "zh-cn/$slug.mp3",
            coverAssetKey = null,
        )

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
                    put("version", JSONObject().apply {
                        put("audio_asset_key", track.audioAssetKey)
                        put("cover_asset_key", track.coverAssetKey)
                    })
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
    fun playableCatalogue(): Catalogue {
        // Studio currently publishes owner-controlled works to this manifest.
        // Read it even when the older BFF is healthy: a successful but stale
        // BFF response must not hide a newly published owner work.
        val ownerTracks = runCatching {
            Catalogue.from(getAbsoluteJson("https://play.rongjingmusic.com/internal-catalogue.json?v=${System.currentTimeMillis()}"))
                .tracks.filter { it.audioAssetKey != null }
        }.getOrDefault(emptyList())
        val bffTracks = runCatching {
            catalogue().tracks.mapNotNull { summary ->
                if (summary.audioAssetKey != null) summary
                else runCatching { track(summary.id) }.getOrNull()?.takeIf { it.audioAssetKey != null }
            }
        }.getOrDefault(emptyList())
        val merged = (ownerTracks + bffTracks).distinctBy { it.id }
        if (merged.isEmpty()) throw ConnectionError.NotFound("catalogue unavailable")
        return Catalogue(merged)
    }

    fun track(id: String): CatalogueTrack = CatalogueTrack.from(getJson("/tracks/$id"))

    private fun getJson(path: String): JSONObject = getAbsoluteJson("$baseUrl$path")

    private fun getAbsoluteJson(url: String): JSONObject {
        val conn = URL(url).openConnection() as HttpURLConnection
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
