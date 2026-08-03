package com.moodify.app.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

/** One real processed work saved from a demo pipeline run. */
data class ProcessedWork(
    val filename: String,
    val preset: String,
    val mrsBefore: Double?,
    val mrsAfter: Double?,
    val mrsDelta: Double?,
    val gatePassed: Boolean,
    val createdAt: Long,
    val issues: List<String>,
    val artifactId: String? = null,
    val uploadId: String? = null,
)

/**
 * Local persistence of real processed works (SharedPreferences JSON list).
 * Demo scope only: production would sync via the API project/artifact model.
 */
class WorkLibrary(context: Context) {
    private val prefs = context.getSharedPreferences("moodify_works", Context.MODE_PRIVATE)

    fun add(summary: DemoResultSummary) {
        val all = all().toMutableList()
        all.add(0, ProcessedWork(
            filename = summary.filename,
            preset = summary.preset,
            mrsBefore = summary.mrsBefore,
            mrsAfter = summary.mrsAfter,
            mrsDelta = summary.mrsDelta,
            gatePassed = summary.gatePassed,
            createdAt = System.currentTimeMillis(),
            issues = summary.issues,
            artifactId = summary.artifactId,
            uploadId = summary.uploadId,
        ))
        save(all)
    }

    fun all(): List<ProcessedWork> {
        val raw = prefs.getString("works", null) ?: return emptyList()
        return try {
            val arr = JSONArray(raw)
            buildList {
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    add(ProcessedWork(
                        filename = o.getString("filename"),
                        preset = o.optString("preset"),
                        mrsBefore = if (o.isNull("mrs_before")) null else o.optDouble("mrs_before"),
                        mrsAfter = if (o.isNull("mrs_after")) null else o.optDouble("mrs_after"),
                        mrsDelta = if (o.isNull("mrs_delta")) null else o.optDouble("mrs_delta"),
                        gatePassed = o.optBoolean("gate_passed", false),
                        createdAt = o.optLong("created_at", 0L),
                        issues = buildList {
                            val issues = o.optJSONArray("issues") ?: return@buildList
                            for (j in 0 until issues.length()) add(issues.optString(j))
                        },
                        artifactId = o.optString("artifact_id").ifEmpty { null },
                        uploadId = o.optString("upload_id").ifEmpty { null },
                    ))
                }
            }
        } catch (_: Exception) {
            emptyList()
        }
    }

    fun clear() {
        prefs.edit().remove("works").apply()
    }

    private fun save(works: List<ProcessedWork>) {
        val arr = JSONArray()
        works.forEach { w ->
            arr.put(JSONObject()
                .put("filename", w.filename)
                .put("preset", w.preset)
                .put("mrs_before", w.mrsBefore ?: JSONObject.NULL)
                .put("mrs_after", w.mrsAfter ?: JSONObject.NULL)
                .put("mrs_delta", w.mrsDelta ?: JSONObject.NULL)
                .put("gate_passed", w.gatePassed)
                .put("created_at", w.createdAt)
                .put("issues", JSONArray().apply { w.issues.forEach(::put) })
                .put("artifact_id", w.artifactId ?: JSONObject.NULL)
                .put("upload_id", w.uploadId ?: JSONObject.NULL))
        }
        prefs.edit().putString("works", arr.toString()).apply()
    }
}
