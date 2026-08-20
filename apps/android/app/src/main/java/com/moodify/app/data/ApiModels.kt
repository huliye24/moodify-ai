package com.moodify.app.data

import org.json.JSONObject

data class Health(
    val apiVersion: String,
    val minClientVersion: String,
    val mode: String,
    val serverTime: String,
) {
    companion object {
        fun fromJson(json: JSONObject): Health = Health(
            apiVersion = json.getString("api_version"),
            minClientVersion = json.getString("min_client_version"),
            mode = json.getString("mode"),
            serverTime = json.getString("server_time"),
        )
    }
}

data class Capabilities(
    val apiVersion: String,
    val endpoints: Map<String, String>,
    val presets: List<String>,
    val maxUploadBytes: Long,
    val auth: String,
) {
    companion object {
        fun fromJson(json: JSONObject): Capabilities {
            val endpoints = JSONObject()
            json.getJSONObject("endpoints").let { endpointsJson ->
                endpointsJson.keys().forEach { key -> endpoints.put(key, endpointsJson.getString(key)) }
            }
            val presets = mutableListOf<String>()
            json.getJSONArray("presets").let { arr ->
                for (i in 0 until arr.length()) presets.add(arr.getString(i))
            }
            return Capabilities(
                apiVersion = json.getString("api_version"),
                endpoints = endpoints.keys().asSequence().associateWith { endpoints.getString(it) },
                presets = presets,
                maxUploadBytes = json.getLong("max_upload_bytes"),
                auth = json.getString("auth"),
            )
        }
    }
}

data class PairResult(
    val token: String,
    val tokenId: String,
    val apiVersion: String,
) {
    companion object {
        fun fromJson(json: JSONObject): PairResult = PairResult(
            token = json.getString("token"),
            tokenId = json.getString("token_id"),
            apiVersion = json.getString("api_version"),
        )
    }
}

/** Pairwise Auditory Judge result (DSK-MFY-PAIRWISE-JUDGE-001). */
data class PairwiseJudgmentResult(
    val judgmentId: String,
    val outcome: String,
    val confidenceLevel: String,
    val winnerMargin: Double,
    val evidenceCoverage: Double,
    val topReasons: List<String>,
) {
    companion object {
        fun fromJson(json: JSONObject): PairwiseJudgmentResult {
            val reasons = mutableListOf<String>()
            json.optJSONArray("top_reasons")?.let { arr ->
                for (i in 0 until arr.length()) reasons.add(arr.getString(i))
            }
            return PairwiseJudgmentResult(
                judgmentId = json.getString("judgment_id"),
                outcome = json.getString("outcome"),
                confidenceLevel = json.optString("confidence_level", "LOW"),
                winnerMargin = json.optDouble("winner_margin", 0.0),
                evidenceCoverage = json.optDouble("evidence_coverage", 0.0),
                topReasons = reasons,
            )
        }
    }
}
