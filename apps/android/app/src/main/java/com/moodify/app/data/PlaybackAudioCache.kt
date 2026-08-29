package com.moodify.app.data

import android.content.Context
import androidx.annotation.OptIn
import androidx.media3.common.util.UnstableApi
import androidx.media3.database.StandaloneDatabaseProvider
import androidx.media3.datasource.DataSpec
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.datasource.cache.CacheDataSource
import androidx.media3.datasource.cache.CacheWriter
import androidx.media3.datasource.cache.LeastRecentlyUsedCacheEvictor
import androidx.media3.datasource.cache.SimpleCache
import java.io.File
import java.util.concurrent.Executors

/** Bounded disk cache with a small startup prefetch window for the next ten tracks. */
@OptIn(UnstableApi::class)
internal class PlaybackAudioCache(context: Context, upstream: DefaultHttpDataSource.Factory) {
    private val cache = SimpleCache(
        File(context.cacheDir, "moodify_playback_v2"),
        LeastRecentlyUsedCacheEvictor(MAX_CACHE_BYTES),
        StandaloneDatabaseProvider(context),
    )
    val dataSourceFactory: CacheDataSource.Factory = CacheDataSource.Factory()
        .setCache(cache)
        .setUpstreamDataSourceFactory(upstream)
        .setFlags(CacheDataSource.FLAG_IGNORE_CACHE_ON_ERROR)

    private val prefetchExecutor = Executors.newSingleThreadExecutor { task ->
        Thread(task, "moodify-audio-prefetch").apply { isDaemon = true }
    }
    @Volatile private var generation = 0L

    fun prefetch(urls: List<String>) {
        val requestGeneration = ++generation
        val uniqueUrls = urls.distinct().take(PREFETCH_TRACKS)
        prefetchExecutor.execute {
            for (url in uniqueUrls) {
                if (requestGeneration != generation) return@execute
                runCatching {
                    val dataSpec = DataSpec.Builder()
                        .setUri(url)
                        .setKey(url)
                        .setLength(PREFETCH_BYTES_PER_TRACK)
                        .build()
                    CacheWriter(dataSourceFactory.createDataSourceForDownloading(), dataSpec, null, null).cache()
                }
            }
        }
    }

    companion object {
        private const val PREFETCH_TRACKS = 10
        private const val PREFETCH_BYTES_PER_TRACK = 2L * 1024 * 1024
        private const val MAX_CACHE_BYTES = 512L * 1024 * 1024
    }
}
