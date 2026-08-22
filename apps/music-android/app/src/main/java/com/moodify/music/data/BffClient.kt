package com.moodify.music.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Minimal BFF client — public /api/v1/music only.
 * Never talks to PolarDB; never holds internal service keys.
 */
class BffClient(private val baseUrl: String = "https://rongjinwenchuan.xyz/api/v1/music") {

    class BffException(val apiError: ApiError, status: Int) : Exception("${apiError.code} ($status): ${apiError.message}")

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
        if (status !in 200..299) throw BffException(ApiError.from(json), status)
        return json
    }

    fun bootstrap(): Bootstrap = Bootstrap.from(getJson("/bootstrap"))

    fun catalogue(): Catalogue = Catalogue.from(getJson("/catalogue"))

    /**
     * Catalogue rows intentionally omit the media version. Resolve each public
     * track through its canonical detail endpoint before presenting it as
     * playable; this avoids inventing fallback media in the client.
     */
    fun playableCatalogue(): Catalogue {
        val catalogue = catalogue()
        return Catalogue(catalogue.tracks.mapNotNull { summary ->
            runCatching { track(summary.id) }.getOrNull()?.takeIf { it.audioAssetKey != null }
        })
    }

    fun track(id: String): Track = Track.from(getJson("/tracks/$id"))
}
