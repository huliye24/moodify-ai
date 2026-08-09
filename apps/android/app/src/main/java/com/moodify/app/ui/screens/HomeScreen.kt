package com.moodify.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.data.BaseUrlStore
import com.moodify.app.data.CatalogSong
import com.moodify.app.data.DemoProcessRepository
import com.moodify.app.data.MoodifyApiClient
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.QueueItem
import com.moodify.app.data.TokenStore
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun HomeScreen(onOpenDrawer: () -> Unit = {}, onOpenSearch: () -> Unit = {}) {
    val context = LocalContext.current
    val repo = remember {
        DemoProcessRepository(
            client = MoodifyApiClient(baseUrlProvider = { BaseUrlStore(context).baseUrl }),
            tokenProvider = { TokenStore(context).token() },
        )
    }
    var songs by remember { mutableStateOf<List<CatalogSong>?>(null) }
    LaunchedEffect(Unit) {
        songs = try { repo.catalog() } catch (_: Exception) { null }
    }
    val realSongs = songs?.takeIf { it.isNotEmpty() }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(18.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onOpenDrawer) { Icon(Icons.Outlined.Menu, stringResource(R.string.accessibility_open_menu), tint = MoodifyNavy) }
            Row(Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) { MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold) }
            IconButton(onClick = onOpenSearch) { Icon(Icons.Outlined.Search, stringResource(R.string.accessibility_search), tint = MoodifyNavy) }
        }
        Text(stringResource(R.string.home_discover_title), color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold)
        Text(stringResource(R.string.home_discover_subtitle), color = MoodifyMuted, fontSize = 14.sp)
        Spacer(Modifier.height(16.dp))
        if (realSongs != null) {
            FeaturedTrack(realSongs[0], { playCatalog(realSongs, 0) })
            Spacer(Modifier.height(14.dp))
            PopularWorks(realSongs) { index -> playCatalog(realSongs, index) }
        } else {
            FeaturedTrack(null, {})
            Spacer(Modifier.height(14.dp))
            PopularWorks(emptyList()) { }
        }
        Spacer(Modifier.height(14.dp)); ContinueListening(); Spacer(Modifier.height(14.dp)); PopularCreators(); Spacer(Modifier.height(20.dp))
    }
}

private fun playCatalog(songs: List<CatalogSong>, startIndex: Int) {
    val queue = songs.map {
        QueueItem(
            title = it.title,
            subtitle = it.artist,
            path = "/catalog/${it.songId}/download",
            preset = it.preset,
        )
    }
    PlaybackManager.playQueue(queue, startIndex)
}

@Composable private fun FeaturedTrack(song: CatalogSong?, onPlay: () -> Unit) {
    Box(Modifier.fillMaxWidth().height(250.dp).background(Brush.linearGradient(listOf(Color(0xFF312780), Color(0xFF7651D8), Color(0xFFDB8CE9))), RoundedCornerShape(24.dp))) {
        Canvas(Modifier.fillMaxSize()) {
            repeat(28) { i -> val x = size.width * ((i * 37) % 97) / 97f; val y = size.height * ((i * 19) % 55) / 100f; drawCircle(Color.White.copy(.45f), 1.2f, Offset(x, y)) }
            drawCircle(Color(0x55FFE5FF), size.width * .20f, Offset(size.width * .72f, size.height * .34f)); drawCircle(Color.White.copy(.65f), size.width * .15f, Offset(size.width * .72f, size.height * .34f), style = androidx.compose.ui.graphics.drawscope.Stroke(2.dp.toPx()))
            val mountain = Path().apply { moveTo(0f, size.height * .70f); lineTo(size.width * .27f, size.height * .48f); lineTo(size.width * .43f, size.height * .65f); lineTo(size.width * .63f, size.height * .52f); lineTo(size.width, size.height * .70f); lineTo(size.width, size.height); lineTo(0f, size.height); close() }; drawPath(mountain, Color(0xAA171652))
        }
        Column(Modifier.fillMaxSize().padding(18.dp)) {
            Surface(color = Color(0x55351C92), shape = RoundedCornerShape(14.dp)) { Text(stringResource(R.string.home_today_recommend), color = Color.White, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 11.dp, vertical = 6.dp)) }
            Spacer(Modifier.weight(1f))
            Text(song?.title ?: "Dreamscape", color = Color.White, fontSize = 25.sp, fontWeight = FontWeight.Bold, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis)
            Text("${song?.artist ?: "泫榛"}  ✦", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
            Text(if (song != null) "${stringResource(R.string.home_platform_master)} · ${song.preset}" else stringResource(R.string.home_dream_placeholder), color = Color.White.copy(.8f), fontSize = 13.sp, modifier = Modifier.padding(top = 5.dp))
            Row(verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.PlayArrow, null, tint = Color.White, modifier = Modifier.size(17.dp)); Text(song?.durationS?.let { "${it / 60}:%02d".format(it % 60) } ?: "128.6万     ♡ 1.2万     ▢ 342", color = Color.White.copy(.85f), fontSize = 11.sp); Spacer(Modifier.weight(1f)); FilledIconButton(onClick = onPlay, colors = IconButtonDefaults.filledIconButtonColors(containerColor = Color.White), modifier = Modifier.size(54.dp)) { Icon(Icons.Outlined.PlayArrow, "播放", tint = MoodifyPurple, modifier = Modifier.size(30.dp)) } }
        }
    }
}

@Composable private fun PopularWorks(songs: List<CatalogSong>, onPlay: (Int) -> Unit) {
    SectionCard(stringResource(R.string.home_hot_works)) {
        if (songs.isEmpty()) {
            TrackRow("AI Demo Track", "泫榛", "03:24", "12.4万", listOf(Color(0xFF7B2BDB), Color(0xFF263BB4))) {}
            HorizontalDivider(color = MoodifyOutline)
            TrackRow("Sunset Drive", "Aurora", "03:57", "8.7万", listOf(Color(0xFFFF9D61), Color(0xFFD64C67))) {}
            HorizontalDivider(color = MoodifyOutline)
            TrackRow("Midnight Walk", "Echo", "02:45", "6.1万", listOf(Color(0xFF3ABCA1), Color(0xFF17475E))) {}
        } else {
            songs.take(3).forEachIndexed { index, song ->
                TrackRow(song.title, song.artist, song.durationS?.let { "${it / 60}:%02d".format(it % 60) } ?: "—", "${song.preset}", listOf(Color(0xFF7B2BDB), Color(0xFF263BB4))) { onPlay(index) }
                if (index < 2) HorizontalDivider(color = MoodifyOutline)
            }
        }
    }
}
@Composable private fun TrackRow(title: String, artist: String, duration: String, plays: String, colors: List<Color>, onPlay: () -> Unit = {}) { Row(Modifier.fillMaxWidth().padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) { Cover(colors, Modifier.size(52.dp)); Column(Modifier.padding(start = 11.dp).weight(1f)) { Text(title, color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis); Text("$artist  ✦", color = MoodifyNavy, fontSize = 11.sp); Text("$duration     ▷ $plays     ♡ 2,341", color = MoodifyMuted, fontSize = 10.sp) }; OutlinedIconButton(onClick = onPlay, modifier = Modifier.size(35.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Icon(Icons.Outlined.PlayArrow, null, tint = MoodifyBlue, modifier = Modifier.size(19.dp)) }; Icon(Icons.Outlined.MoreHoriz, null, tint = MoodifyMuted, modifier = Modifier.padding(start = 5.dp).size(18.dp)) } }

@Composable private fun ContinueListening() { SectionCard(stringResource(R.string.home_continue_listening)) { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MiniTrack("Midnight Walk", "02:45", listOf(Color(0xFF3ABCA1), Color(0xFF17475E)), Modifier.weight(1f)); MiniTrack("Sunset Drive", "03:57", listOf(Color(0xFFFF9D61), Color(0xFFD64C67)), Modifier.weight(1f)); MiniTrack("Dreamscape", "03:24", listOf(Color(0xFF7B2BDB), Color(0xFF263BB4)), Modifier.weight(1f)) } } }
@Composable private fun MiniTrack(title: String, duration: String, colors: List<Color>, modifier: Modifier) { Row(modifier.background(Color(0xFFFBFCFF), RoundedCornerShape(13.dp)).padding(6.dp), verticalAlignment = Alignment.CenterVertically) { Cover(colors, Modifier.size(42.dp)); Column(Modifier.padding(start = 6.dp).weight(1f)) { Text(title, color = MoodifyNavy, fontSize = 9.sp, maxLines = 1); Text(duration, color = MoodifyMuted, fontSize = 9.sp) }; Icon(Icons.Outlined.PlayCircle, null, tint = MoodifyBlue, modifier = Modifier.size(20.dp)) } }

@Composable private fun PopularCreators() { SectionCard(stringResource(R.string.home_hot_creators)) { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Creator("泫榛", "128.6万", Color(0xFF28206C), true); Creator("Aurora", "96.2万", Color(0xFFE7A6D4)); Creator("Echo", "72.4万", Color(0xFFCAD1D9)) } } }
@Composable private fun Creator(name: String, followers: String, color: Color, followed: Boolean = false) { Row(verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(42.dp).background(color, CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color.White) }; Column(Modifier.padding(start = 7.dp)) { Text("$name ✦", color = MoodifyNavy, fontSize = 11.sp, fontWeight = FontWeight.Bold); Text(stringResource(R.string.home_followers, followers), color = MoodifyMuted, fontSize = 9.sp); Surface(shape = RoundedCornerShape(10.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyBlue), color = Color.Transparent) { Text(if (followed) stringResource(R.string.home_following) else stringResource(R.string.home_follow), color = MoodifyBlue, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 2.dp)) } } } }

@Composable private fun SectionCard(title: String, content: @Composable ColumnScope.() -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) { Column(Modifier.padding(13.dp)) { Row(verticalAlignment = Alignment.CenterVertically) { Text(title, Modifier.weight(1f), color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold); Text(stringResource(R.string.home_view_all), color = MoodifyMuted, fontSize = 11.sp) }; content() } } }
@Composable private fun Cover(colors: List<Color>, modifier: Modifier) { Box(modifier.background(Brush.linearGradient(colors), RoundedCornerShape(9.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.PlayCircle, null, tint = Color.White, modifier = Modifier.size(23.dp)) } }
