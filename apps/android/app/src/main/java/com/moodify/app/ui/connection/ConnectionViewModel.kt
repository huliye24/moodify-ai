package com.moodify.app.ui.connection

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.moodify.app.data.BaseUrlStore
import com.moodify.app.data.ConnectionRepository
import com.moodify.app.data.ConnectionState
import com.moodify.app.data.MoodifyApiClient
import com.moodify.app.data.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class ConnectionViewModel(application: Application) : AndroidViewModel(application) {

    private val prefs = application.getSharedPreferences("moodify_connection", Application.MODE_PRIVATE)
    private val tokenStore = TokenStore(application)
    private val baseUrlStore = BaseUrlStore(application)
    private val repository = ConnectionRepository(
        client = MoodifyApiClient(baseUrlProvider = { baseUrlStore.baseUrl }),
        tokenStore = tokenStore,
    )

    private val _state = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val state: StateFlow<ConnectionState> = _state.asStateFlow()

    private val _baseUrl = MutableStateFlow(baseUrlStore.baseUrl)
    val baseUrl: StateFlow<String> = _baseUrl.asStateFlow()

    private val _paired = MutableStateFlow(tokenStore.tokenId() != null)
    val paired: StateFlow<Boolean> = _paired.asStateFlow()

    init {
        val deviceId = prefs.getString("device_id", null) ?: UUID.randomUUID().toString().also {
            prefs.edit().putString("device_id", it).apply()
        }
        repository.setDevice(deviceId, "Moodify-Android")
    }

    fun connect() {
        viewModelScope.launch {
            _state.value = ConnectionState.Connecting
            _state.value = repository.connect()
        }
    }

    fun pair() {
        viewModelScope.launch {
            _state.value = ConnectionState.Connecting
            try {
                repository.pair()
                _paired.value = true
                _state.value = repository.connect()
            } catch (e: Exception) {
                _state.value = ConnectionState.Error(
                    com.moodify.app.data.ConnectionError.Offline(e)
                )
            }
        }
    }

    fun revoke() {
        viewModelScope.launch {
            repository.revoke()
            _paired.value = false
            _state.value = ConnectionState.Disconnected
        }
    }

    fun updateBaseUrl(value: String) {
        baseUrlStore.baseUrl = value
        _baseUrl.value = baseUrlStore.baseUrl
    }

    fun isPaired(): Boolean = tokenStore.tokenId() != null
}
