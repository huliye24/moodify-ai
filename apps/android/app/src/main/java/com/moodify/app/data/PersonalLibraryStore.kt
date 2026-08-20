package com.moodify.app.data

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

data class UserPlaylist(
    val id: String,
    val name: String,
    val tracks: List<QueueItem> = emptyList(),
)

data class PersonalLibraryState(
    val favouritePaths: Set<String> = emptySet(),
    val playlists: List<UserPlaylist> = emptyList(),
)

/** User-owned library state. The public catalogue and playback queue never write here implicitly. */
class PersonalLibraryStore(context: Context) {
    private val preferences = context.applicationContext.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE)
    private val _state = MutableStateFlow(read())
    val state: StateFlow<PersonalLibraryState> = _state.asStateFlow()

    fun toggleFavourite(track: QueueItem) {
        val paths = _state.value.favouritePaths.toMutableSet()
        if (!paths.add(track.path)) paths.remove(track.path)
        update(_state.value.copy(favouritePaths = paths))
    }

    fun createPlaylist(name: String, firstTrack: QueueItem? = null): Boolean {
        val cleanName = name.trim()
        if (cleanName.isEmpty()) return false
        val playlist = UserPlaylist(
            id = UUID.randomUUID().toString(),
            name = cleanName,
            tracks = firstTrack?.let(::listOf).orEmpty(),
        )
        update(_state.value.copy(playlists = _state.value.playlists + playlist))
        return true
    }

    fun addToPlaylist(playlistId: String, track: QueueItem) {
        val playlists = _state.value.playlists.map { playlist ->
            if (playlist.id != playlistId || playlist.tracks.any { it.path == track.path }) playlist
            else playlist.copy(tracks = playlist.tracks + track)
        }
        update(_state.value.copy(playlists = playlists))
    }

    private fun update(next: PersonalLibraryState) {
        _state.value = next
        preferences.edit().putString(STATE, encode(next).toString()).apply()
    }

    private fun read(): PersonalLibraryState = runCatching {
        val root = JSONObject(preferences.getString(STATE, null) ?: return PersonalLibraryState())
        val favourites = buildSet {
            val array = root.optJSONArray("favourites") ?: JSONArray()
            for (index in 0 until array.length()) add(array.getString(index))
        }
        val playlists = buildList {
            val array = root.optJSONArray("playlists") ?: JSONArray()
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                val tracks = buildList {
                    val rows = item.optJSONArray("tracks") ?: JSONArray()
                    for (trackIndex in 0 until rows.length()) {
                        val row = rows.getJSONObject(trackIndex)
                        add(QueueItem(row.getString("title"), row.optString("subtitle"), row.getString("path")))
                    }
                }
                add(UserPlaylist(item.getString("id"), item.getString("name"), tracks))
            }
        }
        PersonalLibraryState(favourites, playlists)
    }.getOrDefault(PersonalLibraryState())

    private fun encode(state: PersonalLibraryState) = JSONObject().apply {
        put("favourites", JSONArray(state.favouritePaths.toList()))
        put("playlists", JSONArray().apply {
            state.playlists.forEach { playlist ->
                put(JSONObject().apply {
                    put("id", playlist.id)
                    put("name", playlist.name)
                    put("tracks", JSONArray().apply {
                        playlist.tracks.forEach { track ->
                            put(JSONObject().apply {
                                put("title", track.title)
                                put("subtitle", track.subtitle)
                                put("path", track.path)
                            })
                        }
                    })
                })
            }
        })
    }

    private companion object {
        const val PREFERENCES = "moodify_personal_library_v2"
        const val STATE = "state"
    }
}
