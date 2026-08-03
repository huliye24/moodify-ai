package com.moodify.app.data

import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.net.ConnectException
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URL

/**
 * Zero-dependency Moodify API v1 client (HttpURLConnection + org.json).
 *
 * Classifies failures per docs/api/v1.md:
 * OFFLINE / TIMEOUT client-side, UNAUTHORIZED / INCOMPATIBLE / SERVER_ERROR /
 * NOT_FOUND / VALIDATION / NOT_IMPLEMENTED from the server error body.
 *
 * Never logs tokens, absolute paths or tracebacks.
 */
class MoodifyApiClient(
    private val baseUrlProvider: () -> String,
    private val connectTimeoutMs: Int = 5000,
    private val readTimeoutMs: Int = 10000,
) {
    /** /api/v1 suffix is appended here; the provider returns e.g. http://127.0.0.1:8000 */
    private fun endpoint(path: String): String = "${baseUrlProvider().trimEnd('/')}/api/v1$path"

    fun health(): Health = request("GET", "/health", null) { body ->
        Health.fromJson(JSONObject(body))
    }

    fun pair(deviceId: String, deviceName: String): PairResult {
        val payload = JSONObject()
            .put("device_id", deviceId)
            .put("device_name", deviceName)
            .toString()
        return request("POST", "/pair", payload) { body ->
            PairResult.fromJson(JSONObject(body))
        }
    }

    fun revoke(token: String) {
        request("POST", "/pair/revoke", null, token = token) { /* 200 {"revoked": true} */ }
    }

    fun capabilities(): Capabilities = request("GET", "/capabilities", null) { body ->
        Capabilities.fromJson(JSONObject(body))
    }

    /** Create a project; server auto-starts the pipeline job (DSK-MFY-DEMO-001). */
    fun createProject(title: String, sourceAudioIds: List<String>, token: String): ProjectCreated {
        val payload = JSONObject()
            .put("title", title)
            .put("source_audio_ids", JSONArray().apply { sourceAudioIds.forEach(::put) })
            .toString()
        return request("POST", "/projects", payload, token = token) { body ->
            ProjectCreated.fromJson(JSONObject(body))
        }
    }

    fun getJob(jobId: String, token: String): DemoJobStatus =
        request("GET", "/jobs/$jobId", null, token = token) { body ->
            DemoJobStatus.fromJson(JSONObject(body))
        }

    fun getJobResult(jobId: String, token: String): DemoResultSummary =
        request("GET", "/jobs/$jobId/result", null, token = token) { body ->
            DemoResultSummary.fromJson(JSONObject(body))
        }

    /**
     * Multipart upload of a real audio file. Returns the upload_id.
     * Uses a longer read timeout since 50 MB over USB/LAN can take a while.
     */
    fun uploadAudio(
        token: String,
        projectId: String,
        filename: String,
        sizeBytes: Long,
        sha256: String,
        fileBytes: ByteArray,
        mime: String,
    ): String {
        val boundary = "moodify-${System.nanoTime()}"
        val body = buildMultipart(fields = mapOf(
            "project_id" to projectId,
            "filename" to filename,
            "size_bytes" to sizeBytes.toString(),
            "sha256" to sha256,
        ), fileBytes = fileBytes, filename = filename, mime = mime, boundary = boundary)

        val url = URL(endpoint("/uploads"))
        val connection = open(url, "POST", readTimeoutMs = 120_000)
        try {
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
            connection.setRequestProperty("Authorization", "Bearer $token")
            connection.outputStream.use { it.write(body) }
        } catch (e: java.io.IOException) {
            connection.disconnect()
            throw ConnectionError.Offline(e)
        }
        return requestFinished(connection, "upload") { JSONObject(it).getString("upload_id") }
    }

    private fun open(url: URL, method: String, readTimeoutMs: Int): HttpURLConnection {
        val connection = try {
            url.openConnection() as HttpURLConnection
        } catch (e: ConnectException) {
            throw ConnectionError.Offline(e)
        } catch (e: SocketTimeoutException) {
            throw ConnectionError.Timeout(e)
        } catch (e: java.io.IOException) {
            throw ConnectionError.Offline(e)
        }
        connection.requestMethod = method
        connection.connectTimeout = connectTimeoutMs
        connection.readTimeout = readTimeoutMs
        connection.setRequestProperty("Accept", "application/json")
        connection.doOutput = true
        return connection
    }

    private fun <T> requestFinished(connection: HttpURLConnection, label: String, parse: (String) -> T): T {
        val status: Int
        val responseText: String
        try {
            status = connection.responseCode
            responseText = if (status in 200..299) {
                connection.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
            } else {
                val err = connection.errorStream
                if (err != null) err.use { it.readBytes().toString(Charsets.UTF_8) } else ""
            }
        } catch (e: SocketTimeoutException) {
            throw ConnectionError.Timeout(e)
        } catch (e: java.io.IOException) {
            throw ConnectionError.Offline(e)
        } finally {
            connection.disconnect()
        }
        if (status !in 200..299) {
            throw toApiError(status, responseText)
        }
        return parse(responseText)
    }

    private fun buildMultipart(
        fields: Map<String, String>,
        fileBytes: ByteArray,
        filename: String,
        mime: String,
        boundary: String,
    ): ByteArray {
        val out = ByteArrayOutputStream()
        fun write(s: String) = out.write(s.toByteArray(Charsets.UTF_8))
        fun write(b: ByteArray) = out.write(b)
        val crlf = "\r\n"
        fields.forEach { (key, value) ->
            write("--$boundary$crlf")
            write("Content-Disposition: form-data; name=\"$key\"$crlf$crlf")
            write("$value$crlf")
        }
        write("--$boundary$crlf")
        write("Content-Disposition: form-data; name=\"file\"; filename=\"$filename\"$crlf")
        write("Content-Type: $mime$crlf$crlf")
        write(fileBytes)
        write(crlf)
        write("--$boundary--$crlf")
        return out.toByteArray()
    }

    private fun <T> request(
        method: String,
        path: String,
        jsonBody: String?,
        token: String? = null,
        parse: (String) -> T,
    ): T {
        val url = URL(endpoint(path))
        val connection: HttpURLConnection
        try {
            connection = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = connectTimeoutMs
                readTimeout = readTimeoutMs
                setRequestProperty("Accept", "application/json")
                // Authorization must be set before the stream write opens the connection
                token?.let { setRequestProperty("Authorization", "Bearer $it") }
                if (jsonBody != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    outputStream.use { it.write(jsonBody.toByteArray(Charsets.UTF_8)) }
                }
            }
        } catch (e: ConnectException) {
            throw ConnectionError.Offline(e)
        } catch (e: SocketTimeoutException) {
            throw ConnectionError.Timeout(e)
        } catch (e: java.io.IOException) {
            throw ConnectionError.Offline(e)
        }

        val status: Int
        val responseText: String
        try {
            status = connection.responseCode
            responseText = if (status in 200..299) {
                connection.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
            } else {
                val err = connection.errorStream
                if (err != null) err.use { it.readBytes().toString(Charsets.UTF_8) } else ""
            }
        } catch (e: SocketTimeoutException) {
            throw ConnectionError.Timeout(e)
        } catch (e: java.io.IOException) {
            throw ConnectionError.Offline(e)
        } finally {
            connection.disconnect()
        }

        if (status !in 200..299) {
            throw toApiError(status, responseText)
        }
        return parse(responseText)
    }

    private fun toApiError(status: Int, body: String): ConnectionError {
        val error = try {
            JSONObject(body).optJSONObject("error")
        } catch (_: Exception) {
            null
        }
        val code = error?.optString("code").orEmpty()
        val message = error?.optString("message").orEmpty()
        return when {
            status == 401 || code == "UNAUTHORIZED" -> ConnectionError.Unauthorized(message)
            code == "INCOMPATIBLE" -> ConnectionError.Incompatible(message)
            code == "NOT_FOUND" -> ConnectionError.NotFound(message)
            code == "VALIDATION" -> ConnectionError.Validation(message)
            code == "NOT_IMPLEMENTED" -> ConnectionError.NotImplemented(message)
            else -> ConnectionError.ServerError(message.ifEmpty { "服务器错误 ($status)" })
        }
    }

    companion object {
        /** Parse a structured error body without leaking sensitive fields. */
        fun parseErrorBody(body: String): ApiErrorBody? = try {
            val error = JSONObject(body).optJSONObject("error")
            error?.let {
                ApiErrorBody(
                    code = it.optString("code"),
                    message = it.optString("message"),
                    requestId = it.optString("request_id").ifEmpty { null },
                )
            }
        } catch (_: Exception) {
            null
        }
    }
}
