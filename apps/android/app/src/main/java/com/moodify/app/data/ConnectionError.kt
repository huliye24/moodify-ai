package com.moodify.app.data

/** Client-side classification of Moodify API v1 failures (see docs/api/v1.md). */
sealed class ConnectionError(val code: String, message: String) : Exception(message) {
    class Offline(cause: Throwable?) : ConnectionError("OFFLINE", "无法连接服务器，请检查 USB 转发或网络") {
        init { this.initCause(cause) }
    }
    class Timeout(cause: Throwable?) : ConnectionError("TIMEOUT", "连接超时，请检查服务是否启动") {
        init { this.initCause(cause) }
    }
    class Unauthorized(msg: String = "令牌无效或已撤销，请重新配对") : ConnectionError("UNAUTHORIZED", msg)
    class Incompatible(msg: String) : ConnectionError("INCOMPATIBLE", msg)
    class ServerError(msg: String) : ConnectionError("SERVER_ERROR", msg)
    class NotFound(msg: String) : ConnectionError("NOT_FOUND", msg)
    class Validation(msg: String) : ConnectionError("VALIDATION", msg)
    class NotImplemented(msg: String) : ConnectionError("NOT_IMPLEMENTED", msg)
}

/** Structured error body returned by the server: {"error": {"code", "message", "request_id"}}. */
data class ApiErrorBody(val code: String, val message: String, val requestId: String?)
