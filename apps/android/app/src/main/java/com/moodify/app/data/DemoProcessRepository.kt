package com.moodify.app.data

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.security.MessageDigest

/** Project created on the server; the job auto-starts (DSK-MFY-DEMO-001). */
data class ProjectCreated(
    val projectId: String,
    val jobId: String,
) {
    companion object {
        fun fromJson(json: JSONObject): ProjectCreated = ProjectCreated(
            projectId = json.getString("project_id"),
            jobId = json.getString("job_id"),
        )
    }
}

/** Live job status from GET /api/v1/jobs/{id}. */
data class DemoJobStatus(
    val jobId: String,
    val status: String,
    val progress: Float,
    val stage: String,
    val errorCode: String?,
) {
    val finished: Boolean get() = status == "done" || status == "failed" || status == "cancelled"

    companion object {
        fun fromJson(json: JSONObject): DemoJobStatus = DemoJobStatus(
            jobId = json.getString("job_id"),
            status = json.getString("status"),
            progress = json.optDouble("progress", 0.0).toFloat(),
            stage = json.optString("stage"),
            errorCode = json.optString("error_code").ifEmpty { null },
        )
    }
}

/** Real processing summary from GET /api/v1/jobs/{id}/result. */
data class DemoResultSummary(
    val jobId: String,
    val uploadId: String?,
    val filename: String,
    val preset: String,
    val mrsBefore: Double?,
    val mrsAfter: Double?,
    val mrsDelta: Double?,
    val gatePassed: Boolean,
    val issues: List<String>,
    val outputFilename: String,
    val artifactId: String?,
) {
    companion object {
        fun fromJson(json: JSONObject): DemoResultSummary {
            val gate = json.optJSONObject("quality_gate")
            val issues = json.optJSONArray("issues")
            return DemoResultSummary(
                jobId = json.getString("job_id"),
                uploadId = json.optString("upload_id").ifEmpty { null },
                filename = json.optString("filename"),
                preset = json.optString("preset"),
                mrsBefore = if (json.isNull("mrs_before")) null else json.optDouble("mrs_before"),
                mrsAfter = if (json.isNull("mrs_after")) null else json.optDouble("mrs_after"),
                mrsDelta = if (json.isNull("mrs_delta")) null else json.optDouble("mrs_delta"),
                gatePassed = gate?.optBoolean("passed", false) ?: false,
                issues = buildList {
                    for (i in 0 until (issues?.length() ?: 0)) add(issues!!.optString(i))
                },
                outputFilename = json.optString("output_filename"),
                artifactId = json.optString("artifact_id").ifEmpty { null },
            )
        }
    }
}

/**
 * Real end-to-end demo processing flow:
 * pick audio -> upload -> create project (auto-starts job) -> poll progress.
 */
class DemoProcessRepository(
    private val client: MoodifyApiClient,
    private val tokenProvider: () -> String?,
) {
    class NotPairedException : ConnectionError("NOT_PAIRED", "请先在“我的”中连接并配对电脑端")

    private fun requireToken(): String =
        tokenProvider() ?: throw NotPairedException()

    /** Read a content or file Uri into bytes + display name + sha256. */
    suspend fun uploadFromUri(context: Context, uri: Uri): Pair<String, String> =
        withContext(Dispatchers.IO) {
            val token = requireToken()
            val resolver = context.contentResolver
            val filename: String
            val bytes: ByteArray
            val mime: String
            if (uri.scheme == "file") {
                val file = java.io.File(uri.path ?: "")
                filename = file.name
                bytes = file.readBytes()
                mime = "audio/wav"
            } else {
                filename = resolver.query(uri, null, null, null, null)?.use { cursor ->
                    val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (idx >= 0 && cursor.moveToFirst()) cursor.getString(idx) else null
                } ?: "audio.wav"
                bytes = resolver.openInputStream(uri)?.use { it.readBytes() }
                    ?: throw ConnectionError.Validation("无法读取所选文件")
                mime = resolver.getType(uri) ?: "audio/wav"
            }
            if (bytes.size > MAX_UPLOAD_BYTES) {
                throw ConnectionError.Validation("文件超过 50MB 上限，请选择更小的音频")
            }
            val sha = sha256Hex(bytes)
            val projectId = "prj-mobile-${System.currentTimeMillis()}"
            val uploadId = client.uploadAudio(
                token = token,
                projectId = projectId,
                filename = filename,
                sizeBytes = bytes.size.toLong(),
                sha256 = sha,
                fileBytes = bytes,
                mime = mime,
            )
            uploadId to filename
        }

    suspend fun startProject(title: String, uploadId: String): ProjectCreated =
        withContext(Dispatchers.IO) {
            val created = client.createProject(title, listOf(uploadId), requireToken())
            created
        }

    suspend fun pollJob(jobId: String, onProgress: (DemoJobStatus) -> Unit): DemoJobStatus {
        while (true) {
            val status = withContext(Dispatchers.IO) { client.getJob(jobId, requireToken()) }
            onProgress(status)
            if (status.finished) return status
            delay(POLL_INTERVAL_MS)
        }
    }

    suspend fun result(jobId: String): DemoResultSummary =
        withContext(Dispatchers.IO) {
            client.getJobResult(jobId, requireToken())
        }

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256")
            .digest(bytes)
            .joinToString("") { "%02x".format(it) }

    companion object {
        const val POLL_INTERVAL_MS = 2000L
        const val MAX_UPLOAD_BYTES = 50 * 1024 * 1024
    }
}
