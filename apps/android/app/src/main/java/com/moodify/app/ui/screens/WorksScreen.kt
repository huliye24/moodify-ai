package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

private data class WorkItem(
    val title: String, val duration: String, val status: String, val date: String,
    val colors: List<Color>, val tags: List<Pair<ImageVector, String>>, val progress: Float? = null,
)

private val demoWorks = listOf(
    WorkItem("AI Demo Track", "03:24", "已完成", "2025-07-30 14:20", listOf(Color(0xFF5425C9), Color(0xFFA931D2), Color(0xFF283B9E)), listOf(Icons.Outlined.Verified to "标准处理", Icons.Outlined.GraphicEq to "响度优化", Icons.Outlined.ShowChart to "True Peak")),
    WorkItem("Dreamscape", "04:18", "处理中 68%", "2025-07-30 11:15", listOf(Color(0xFF3948E8), Color(0xFF795CF4), Color(0xFF25258E)), listOf(Icons.Outlined.Group to "合作计划", Icons.Outlined.GraphicEq to "响度标准化", Icons.Outlined.Tune to "频段平衡"), .68f),
    WorkItem("Sunset Drive", "03:57", "已完成", "2025-07-29 18:42", listOf(Color(0xFFFF936D), Color(0xFFE74A9D), Color(0xFF8A37A9)), listOf(Icons.Outlined.Verified to "标准处理", Icons.Outlined.PhoneAndroid to "平台适配", Icons.Outlined.ShowChart to "True Peak")),
    WorkItem("Midnight Walk", "02:45", "草稿", "2025-07-28 09:30", listOf(Color(0xFF75DFC5), Color(0xFF45C6C7), Color(0xFF3B9CB5)), listOf(Icons.Outlined.Timer to "未处理")),
)

@Composable
fun WorksScreen(onOpenDetail: () -> Unit = {}) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
        Spacer(Modifier.height(24.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
            MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp))
            Text("Moodify", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold)
        }
        Text("让每一首音乐都更动人", Modifier.fillMaxWidth(), color = MoodifyMuted, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        Spacer(Modifier.height(28.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("我的作品", color = MoodifyNavy, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
            OutlinedButton(onClick = {}, shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) {
                Text("筛选", color = MoodifyMuted); Spacer(Modifier.width(6.dp)); Icon(Icons.Outlined.FilterList, null, tint = MoodifyMuted, modifier = Modifier.size(18.dp))
            }
        }
        Spacer(Modifier.height(12.dp))
        demoWorks.forEach { WorkCard(it, onOpenDetail); Spacer(Modifier.height(14.dp)) }
        OutlinedButton(onClick = {}, modifier = Modifier.fillMaxWidth().height(54.dp), shape = RoundedCornerShape(27.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyBlue)) {
            Icon(Icons.Outlined.Add, null, tint = MoodifyBlue); Spacer(Modifier.width(8.dp)); Text("导入作品", color = MoodifyBlue, fontSize = 16.sp)
        }
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun WorkCard(item: WorkItem, onOpenDetail: () -> Unit) {
    Card(onClick = onOpenDetail, modifier = Modifier.fillMaxWidth().shadow(12.dp, RoundedCornerShape(22.dp), ambientColor = Color(0x160B214F), spotColor = Color(0x160B214F)), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Row(Modifier.padding(16.dp)) {
            Box(Modifier.size(82.dp).background(Brush.linearGradient(item.colors), RoundedCornerShape(14.dp))) {
                Box(Modifier.fillMaxSize().padding(14.dp).background(Color.White.copy(.08f), RoundedCornerShape(30.dp)))
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(item.title, color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                    IconButton(onClick = {}, modifier = Modifier.size(38.dp)) { Icon(if (item.progress == null) Icons.Outlined.PlayArrow else Icons.Outlined.Pause, null, tint = MoodifyPurple) }
                }
                Text("${item.duration}  ·  ${item.status}  ·  ${item.date}", color = MoodifyMuted, fontSize = 12.sp)
                item.progress?.let { Spacer(Modifier.height(10.dp)); LinearProgressIndicator(progress = { it }, modifier = Modifier.fillMaxWidth().height(4.dp), color = MoodifyBlue, trackColor = MoodifyOutline) }
                Spacer(Modifier.height(12.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    item.tags.take(3).forEach { (icon, label) ->
                        Surface(shape = RoundedCornerShape(9.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline), color = Color.White, modifier = Modifier.padding(end = 6.dp)) {
                            Row(Modifier.padding(horizontal = 7.dp, vertical = 5.dp), verticalAlignment = Alignment.CenterVertically) { Icon(icon, null, tint = MoodifyMuted, modifier = Modifier.size(14.dp)); Spacer(Modifier.width(4.dp)); Text(label, color = MoodifyMuted, fontSize = 10.sp) }
                        }
                    }
                    Icon(Icons.Outlined.MoreHoriz, null, tint = MoodifyMuted, modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}
