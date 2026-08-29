package com.moodify.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

sealed interface ConnectionState {
    data object Disconnected : ConnectionState
    data object Connecting : ConnectionState
    data class Connected(val health: Health) : ConnectionState
    data class Error(val error: ConnectionError) : ConnectionState
}

/**
 * Owns pairing state: stores the token in the Keystore-backed TokenStore,
 * re-pairs automatically when the server restarted (token invalidated),
 * and surfaces a single [ConnectionState] for the UI.
 */
class ConnectionRepository(
    private val client: MoodifyApiClient,
    private val tokenStore: TokenStore,
) {
    private var deviceId: String? = null
    private var deviceName: String = "Moodify-Android"

    fun setDevice(deviceId: String, deviceName: String) {
        this.deviceId = deviceId
        this.deviceName = deviceName
    }

    fun storedToken(): String? = tokenStore.token()

    suspend fun connect(): ConnectionState = withContext(Dispatchers.IO) {
        try {
            ConnectionState.Connected(client.health())
        } catch (e: ConnectionError) {
            if (e is ConnectionError.Unauthorized) tokenStore.clear()
            ConnectionState.Error(e)
        } catch (e: Exception) {
            ConnectionState.Error(ConnectionError.Offline(e))
        }
    }

    suspend fun pair(): PairResult = withContext(Dispatchers.IO) {
        val id = deviceId ?: throw ConnectionError.Offline(IllegalStateException("device id not set"))
        val result = client.pair(id, deviceName)
        tokenStore.save(result.token, result.tokenId)
        result
    }

    suspend fun revoke() = withContext(Dispatchers.IO) {
        val token = tokenStore.token()
        if (token != null) {
            try {
                client.revoke(token)
            } catch (_: ConnectionError) {
                // token already dead server-side; clearing locally is enough
            }
        }
        tokenStore.clear()
    }

    fun clearLocal() = tokenStore.clear()
}
