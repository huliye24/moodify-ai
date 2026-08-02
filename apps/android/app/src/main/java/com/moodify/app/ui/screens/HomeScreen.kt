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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun HomeScreen(onStartProcessing: () -> Unit, onOpenDrawer: () -> Unit = {}, onOpenSearch: () -> Unit = {}, onOpenNotifications: () -> Unit = {}) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(18.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onOpenDrawer) { Icon(Icons.Outlined.Menu, "菜单", tint = MoodifyNavy) }
            Row(Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) { MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold) }
            IconButton(onClick = onOpenSearch) { Icon(Icons.Outlined.Search, "搜索", tint = MoodifyNavy) }
            BadgedBox(badge = { Badge(containerColor = Color(0xFFFF4D5E)) }) { IconButton(onClick = onOpenNotifications) { Icon(Icons.Outlined.NotificationsNone, "通知", tint = MoodifyNavy) } }
        }
        Text("发现 AI 音乐", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold)
        Text("好听的音乐，由 AI 创作", color = MoodifyMuted, fontSize = 14.sp)
        Spacer(Modifier.height(16.dp)); FeaturedTrack(); Spacer(Modifier.height(14.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            ActionCard(Icons.Outlined.CloudUpload, "上传作品", "分享你的 AI 音乐", true, Modifier.weight(1f), onStartProcessing)
            ActionCard(Icons.Outlined.IosShare, "分享主页", "邀请更多听众", false, Modifier.weight(1f)) {}
        }
        Spacer(Modifier.height(14.dp)); PopularWorks(); Spacer(Modifier.height(14.dp)); ContinueListening(); Spacer(Modifier.height(14.dp)); PopularCreators(); Spacer(Modifier.height(20.dp))
    }
}

@Composable private fun FeaturedTrack() {
    Box(Modifier.fillMaxWidth().height(250.dp).background(Brush.linearGradient(listOf(Color(0xFF312780), Color(0xFF7651D8), Color(0xFFDB8CE9))), RoundedCornerShape(24.dp))) {
        Canvas(Modifier.fillMaxSize()) {
            repeat(28) { i -> val x = size.width * ((i * 37) % 97) / 97f; val y = size.height * ((i * 19) % 55) / 100f; drawCircle(Color.White.copy(.45f), 1.2f, Offset(x, y)) }
            drawCircle(Color(0x55FFE5FF), size.width * .20f, Offset(size.width * .72f, size.height * .34f)); drawCircle(Color.White.copy(.65f), size.width * .15f, Offset(size.width * .72f, size.height * .34f), style = androidx.compose.ui.graphics.drawscope.Stroke(2.dp.toPx()))
            val mountain = Path().apply { moveTo(0f, size.height * .70f); lineTo(size.width * .27f, size.height * .48f); lineTo(size.width * .43f, size.height * .65f); lineTo(size.width * .63f, size.height * .52f); lineTo(size.width, size.height * .70f); lineTo(size.width, size.height); lineTo(0f, size.height); close() }; drawPath(mountain, Color(0xAA171652))
        }
        Column(Modifier.fillMaxSize().padding(18.dp)) {
            Surface(color = Color(0x55351C92), shape = RoundedCornerShape(14.dp)) { Text("今日推荐", color = Color.White, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 11.dp, vertical = 6.dp)) }
            Spacer(Modifier.weight(1f)); Text("Dreamscape", color = Color.White, fontSize = 25.sp, fontWeight = FontWeight.Bold)
            Text("泫榛  ✦", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.SemiBold); Text("梦境般的旋律，带你遨游星海", color = Color.White.copy(.8f), fontSize = 13.sp, modifier = Modifier.padding(top = 5.dp))
            Row(verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.PlayArrow, null, tint = Color.White, modifier = Modifier.size(17.dp)); Text("128.6万     ♡ 1.2万     ▢ 342", color = Color.White.copy(.85f), fontSize = 11.sp); Spacer(Modifier.weight(1f)); FilledIconButton(onClick = {}, colors = IconButtonDefaults.filledIconButtonColors(containerColor = Color.White), modifier = Modifier.size(54.dp)) { Icon(Icons.Outlined.PlayArrow, "播放", tint = MoodifyPurple, modifier = Modifier.size(30.dp)) } }
        }
    }
}

@Composable private fun ActionCard(icon: ImageVector, title: String, subtitle: String, primary: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Card(onClick = onClick, modifier = modifier.height(104.dp), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = if (primary) MoodifyBlue else Color.White), elevation = CardDefaults.cardElevation(4.dp)) {
        Row(Modifier.fillMaxSize().padding(14.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(48.dp).background(if (primary) Color.White else Color(0xFFF4F5FF), RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(29.dp)) }; Column(Modifier.padding(start = 12.dp).weight(1f)) { Text(title, color = if (primary) Color.White else MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold); Text(subtitle, color = if (primary) Color.White.copy(.8f) else MoodifyMuted, fontSize = 11.sp) }; Icon(Icons.Outlined.ChevronRight, null, tint = if (primary) Color.White else MoodifyMuted) }
    }
}

@Composable private fun PopularWorks() { SectionCard("热门作品") { TrackRow("AI Demo Track", "泫榛", "03:24", "12.4万", listOf(Color(0xFF7B2BDB), Color(0xFF263BB4))); HorizontalDivider(color = MoodifyOutline); TrackRow("Sunset Drive", "Aurora", "03:57", "8.7万", listOf(Color(0xFFFF9D61), Color(0xFFD64C67))); HorizontalDivider(color = MoodifyOutline); TrackRow("Midnight Walk", "Echo", "02:45", "6.1万", listOf(Color(0xFF3ABCA1), Color(0xFF17475E))) } }
@Composable private fun TrackRow(title: String, artist: String, duration: String, plays: String, colors: List<Color>) { Row(Modifier.fillMaxWidth().padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) { Cover(colors, Modifier.size(52.dp)); Column(Modifier.padding(start = 11.dp).weight(1f)) { Text(title, color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold); Text("$artist  ✦", color = MoodifyNavy, fontSize = 11.sp); Text("$duration     ▷ $plays     ♡ 2,341", color = MoodifyMuted, fontSize = 10.sp) }; OutlinedIconButton(onClick = {}, modifier = Modifier.size(35.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Icon(Icons.Outlined.PlayArrow, null, tint = MoodifyBlue, modifier = Modifier.size(19.dp)) }; Icon(Icons.Outlined.MoreHoriz, null, tint = MoodifyMuted, modifier = Modifier.padding(start = 5.dp).size(18.dp)) } }

@Composable private fun ContinueListening() { SectionCard("继续收听") { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MiniTrack("Midnight Walk", "02:45", listOf(Color(0xFF3ABCA1), Color(0xFF17475E)), Modifier.weight(1f)); MiniTrack("Sunset Drive", "03:57", listOf(Color(0xFFFF9D61), Color(0xFFD64C67)), Modifier.weight(1f)); MiniTrack("Dreamscape", "03:24", listOf(Color(0xFF7B2BDB), Color(0xFF263BB4)), Modifier.weight(1f)) } } }
@Composable private fun MiniTrack(title: String, duration: String, colors: List<Color>, modifier: Modifier) { Row(modifier.background(Color(0xFFFBFCFF), RoundedCornerShape(13.dp)).padding(6.dp), verticalAlignment = Alignment.CenterVertically) { Cover(colors, Modifier.size(42.dp)); Column(Modifier.padding(start = 6.dp).weight(1f)) { Text(title, color = MoodifyNavy, fontSize = 9.sp, maxLines = 1); Text(duration, color = MoodifyMuted, fontSize = 9.sp) }; Icon(Icons.Outlined.PlayCircle, null, tint = MoodifyBlue, modifier = Modifier.size(20.dp)) } }

@Composable private fun PopularCreators() { SectionCard("热门创作者") { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Creator("泫榛", "128.6万", Color(0xFF28206C), true); Creator("Aurora", "96.2万", Color(0xFFE7A6D4)); Creator("Echo", "72.4万", Color(0xFFCAD1D9)) } } }
@Composable private fun Creator(name: String, followers: String, color: Color, followed: Boolean = false) { Row(verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(42.dp).background(color, CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color.White) }; Column(Modifier.padding(start = 7.dp)) { Text("$name ✦", color = MoodifyNavy, fontSize = 11.sp, fontWeight = FontWeight.Bold); Text("$followers 粉丝", color = MoodifyMuted, fontSize = 9.sp); Surface(shape = RoundedCornerShape(10.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyBlue), color = Color.Transparent) { Text(if (followed) "已关注" else "+ 关注", color = MoodifyBlue, fontSize = 9.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 2.dp)) } } } }

@Composable private fun SectionCard(title: String, content: @Composable ColumnScope.() -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) { Column(Modifier.padding(13.dp)) { Row(verticalAlignment = Alignment.CenterVertically) { Text(title, Modifier.weight(1f), color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold); Text("查看全部  ›", color = MoodifyMuted, fontSize = 11.sp) }; content() } } }
@Composable private fun Cover(colors: List<Color>, modifier: Modifier) { Box(modifier.background(Brush.linearGradient(colors), RoundedCornerShape(9.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.PlayCircle, null, tint = Color.White, modifier = Modifier.size(23.dp)) } }
