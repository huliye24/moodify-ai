package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.ui.theme.*

@Composable
fun SearchScreen(onCancel: () -> Unit) {
    var query by remember { mutableStateOf("") }
    var tab by remember { mutableIntStateOf(0) }
    var recent by remember { mutableStateOf(listOf("Dreamscape", "AI人声", "法语", "Lumière", "氛围")) }
    val tracks = listOf("Dreamscape" to "泫榛", "Sunset Drive" to "Aurora", "Midnight Walk" to "Echo").filter { query.isBlank() || it.first.contains(query, true) || it.second.contains(query, true) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(18.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(query, { query = it }, Modifier.weight(1f), placeholder = { Text(stringResource(R.string.search_placeholder), color = MoodifyMuted) }, leadingIcon = { Icon(Icons.Outlined.Search, null) }, trailingIcon = { if (query.isNotEmpty()) IconButton(onClick = { query = "" }) { Icon(Icons.Outlined.Close, null) } }, singleLine = true, shape = RoundedCornerShape(28.dp))
            TextButton(onClick = onCancel) { Text(stringResource(R.string.search_cancel), color = MoodifyBlue, fontSize = 16.sp) }
        }
        Spacer(Modifier.height(18.dp))
        Row(verticalAlignment = Alignment.CenterVertically) { Text(stringResource(R.string.search_recent), Modifier.weight(1f), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); TextButton(onClick = { recent = emptyList() }) { Text(stringResource(R.string.search_clear), color = MoodifyMuted); Icon(Icons.Outlined.DeleteOutline, null, tint = MoodifyMuted, modifier = Modifier.size(19.dp)) } }
        Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) { recent.forEach { text -> OutlinedButton(onClick = { query = text }, shape = RoundedCornerShape(20.dp)) { Text(text, color = MoodifyNavy, fontSize = 11.sp) } } }
        Spacer(Modifier.height(26.dp)); Text(stringResource(R.string.search_trending), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(10.dp))
        Row { Column(Modifier.weight(1f)) { Rank(1, "Dreamscape 🔥", "12.8万"); Rank(2, "电子 🔥", "9.6万"); Rank(3, "AI Vocal", "7.2万") }; Column(Modifier.weight(1f)) { Rank(4, "紫色氛围", "5.4万"); Rank(5, "法语流行", "4.1万") } }
        Spacer(Modifier.height(22.dp)); Text(stringResource(R.string.search_suggested), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(10.dp)); Tags(listOf("♫ 流行", "⌁ 电子", "☁ 氛围", "✦ AI人声", "☆ 梦幻", "◌ Chill", "≈ Ambient")) { query = it.substringAfter(' ') }
        Spacer(Modifier.height(22.dp))
        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) {
            Column(Modifier.padding(12.dp)) {
                Row(Modifier.fillMaxWidth().background(Color(0xFFF4F5FA), RoundedCornerShape(11.dp))) { listOf(stringResource(R.string.nav_works), stringResource(R.string.search_tab_creators), stringResource(R.string.search_tab_tags)).forEachIndexed { i, label -> Surface(onClick = { tab = i }, modifier = Modifier.weight(1f), color = if (tab == i) Color(0xFFF0EDFF) else Color.Transparent, shape = RoundedCornerShape(11.dp)) { Text(label, color = if (tab == i) MoodifyBlue else MoodifyMuted, textAlign = androidx.compose.ui.text.style.TextAlign.Center, modifier = Modifier.padding(10.dp)) } } }
                when (tab) { 0 -> tracks.forEach { TrackResult(it.first, it.second) }; 1 -> CreatorResults(); else -> Tags(listOf("流行", "电子", "氛围", "AI人声", "梦幻", "Chill", "Ambient", "法语")) { query = it } }
            }
        }
        Spacer(Modifier.height(18.dp)); Text(stringResource(R.string.search_tab_creators), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(10.dp)); CreatorResults(); Spacer(Modifier.height(22.dp))
    }
}

@Composable private fun Rank(n: Int, label: String, count: String) { Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(27.dp).background(if (n <= 3) listOf(Color(0xFFFF5575), Color(0xFFFF9B3D), Color(0xFFFFC82E))[n - 1] else Color(0xFFF0F2F7), RoundedCornerShape(7.dp)), contentAlignment = Alignment.Center) { Text("$n", color = if (n <= 3) Color.White else MoodifyMuted, fontSize = 11.sp) }; Text(label, Modifier.padding(start = 9.dp).weight(1f), color = MoodifyNavy, fontSize = 12.sp); Text(count, color = MoodifyMuted, fontSize = 10.sp) } }
@Composable private fun Tags(items: List<String>, onClick: (String) -> Unit) { Column(verticalArrangement = Arrangement.spacedBy(7.dp)) { items.chunked(4).forEach { row -> Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { row.forEach { tag -> OutlinedButton(onClick = { onClick(tag) }, shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.outlinedButtonColors(containerColor = Color(0xFFF4F0FF)), contentPadding = PaddingValues(horizontal = 11.dp, vertical = 4.dp)) { Text(tag, color = MoodifyPurple, fontSize = 10.sp) } } } } } }
@Composable private fun TrackResult(title: String, artist: String) { Row(Modifier.fillMaxWidth().padding(vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(56.dp).background(Brush.linearGradient(listOf(Color(0xFF6334D2), Color(0xFF27399E))), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.PlayCircle, null, tint = Color.White) }; Column(Modifier.padding(start = 11.dp).weight(1f)) { Text(title, color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold); Text("$artist ✦", color = MoodifyMuted, fontSize = 10.sp); Text("03:24   ▷ 12.8万   ♡ 1.2万   ▢ 342", color = MoodifyMuted, fontSize = 8.sp) }; OutlinedIconButton(onClick = {}, modifier = Modifier.size(36.dp)) { Icon(Icons.Outlined.PlayArrow, null, tint = MoodifyBlue) } } }
@Composable private fun CreatorResults() { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(7.dp)) { listOf("泫榛" to "128.6万", "Aurora" to "96.2万", "Echo" to "72.4万").forEach { (name, fans) -> Card(Modifier.weight(1f), shape = RoundedCornerShape(14.dp), colors = CardDefaults.cardColors(containerColor = Color.White), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Column(Modifier.fillMaxWidth().padding(9.dp), horizontalAlignment = Alignment.CenterHorizontally) { Box(Modifier.size(42.dp).background(Color(0xFFD6D0FF), CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = MoodifyNavy) }; Text("$name ✦", color = MoodifyNavy, fontSize = 10.sp, fontWeight = FontWeight.Bold); Text(stringResource(R.string.home_followers, fans), color = MoodifyMuted, fontSize = 8.sp); OutlinedButton(onClick = {}, modifier = Modifier.height(29.dp), contentPadding = PaddingValues(horizontal = 10.dp)) { Text(stringResource(R.string.home_follow), fontSize = 8.sp) } } } } } }
