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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun ProcessingHubScreen(
    onPickAudio: () -> Unit,
    onWechatImport: () -> Unit,
    onCloudImport: () -> Unit,
    onStandardProcess: () -> Unit,
    onFreeSave: () -> Unit,
    onOpenRecentTask: () -> Unit,
    onOpenDrawer: () -> Unit = {},
) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(18.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onOpenDrawer) { Icon(Icons.Outlined.Menu, "菜单", tint = MoodifyNavy) }
            Row(Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) { MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp)); Text("处理", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold) }
            Icon(Icons.Outlined.HelpOutline, null, tint = MoodifyMuted)
        }
        Spacer(Modifier.height(20.dp))
        PickAudioCard(onPickAudio)
        Spacer(Modifier.height(14.dp))
        Text("导入来源", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(11.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
            SourceCard(Icons.Outlined.Folder, "本地导入", "从手机存储选择", Modifier.weight(1f), onPickAudio)
            SourceCard(Icons.Outlined.Chat, "微信导入", "聊天文件与收藏", Modifier.weight(1f), onWechatImport)
            SourceCard(Icons.Outlined.CloudQueue, "云端导入", "云盘或远程空间", Modifier.weight(1f), onCloudImport)
        }
        Spacer(Modifier.height(20.dp))
        Text("处理方案", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(11.dp))
        PlanCard(Icons.Outlined.Verified, "标准处理", "响度 · 音质 · 平台适配", "¥30", true, onStandardProcess)
        Spacer(Modifier.height(9.dp))
        PlanCard(Icons.Outlined.FreeBreakfast, "免费入驻", "先保存到作品库，之后再处理或发布", "", false, onFreeSave)
        Spacer(Modifier.height(20.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("最近处理任务", Modifier.weight(1f), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold)
            Text("查看全部  ›", color = MoodifyMuted, fontSize = 11.sp)
        }
        Spacer(Modifier.height(11.dp))
        RecentTask("Dreamscape", "处理中 68%", 0.68f, onOpenRecentTask)
        RecentTask("Sunset Drive", "已完成", null, onOpenRecentTask)
        RecentTask("AI Demo Track", "等待处理", null, onOpenRecentTask)
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun PickAudioCard(onPick: () -> Unit) {
    OutlinedCard(onClick = onPick, modifier = Modifier.fillMaxWidth().height(200.dp), shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.5.dp, MoodifyPurple.copy(.5f))) {
        Column(Modifier.fillMaxSize().background(Color(0xFFF9F8FF)), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Box(Modifier.size(66.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(18.dp)), contentAlignment = Alignment.Center) {
                Icon(Icons.Outlined.FileUpload, null, tint = Color.White, modifier = Modifier.size(38.dp))
            }
            Text("选择音频文件", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 18.dp))
            Text("支持 WAV / MP3 / FLAC / AAC / M4A，单个不超过 200MB", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 9.dp))
        }
    }
}

@Composable
private fun SourceCard(icon: ImageVector, title: String, sub: String, modifier: Modifier, click: () -> Unit) {
    Card(onClick = click, modifier = modifier.height(130.dp), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
        Column(Modifier.padding(14.dp)) {
            Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(36.dp))
            Spacer(Modifier.weight(1f))
            Text(title, color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            Text(sub, color = MoodifyMuted, fontSize = 9.sp)
        }
    }
}

@Composable
private fun PlanCard(icon: ImageVector, title: String, sub: String, price: String, primary: Boolean, click: () -> Unit) {
    Card(onClick = click, modifier = Modifier.fillMaxWidth().height(92.dp), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = if (primary) MoodifyBlue else Color.White), elevation = CardDefaults.cardElevation(4.dp)) {
        Row(Modifier.fillMaxSize().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.size(48.dp).background(if (primary) Color.White else Color(0xFFF4F5FF), RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) {
                Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(28.dp))
            }
            Column(Modifier.padding(start = 12.dp).weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(title, color = if (primary) Color.White else MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    if (price.isNotEmpty()) Spacer(Modifier.width(8.dp))
                    if (price.isNotEmpty()) Surface(color = Color(0xFFFFE0B2), shape = RoundedCornerShape(9.dp)) {
                        Text(price, color = Color(0xFFB25E00), fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp))
                    }
                }
                Text(sub, color = if (primary) Color.White.copy(.8f) else MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 5.dp))
            }
            Icon(Icons.Outlined.ChevronRight, null, tint = if (primary) Color.White else MoodifyMuted)
        }
    }
}

@Composable
private fun RecentTask(name: String, status: String, progress: Float?, click: () -> Unit) {
    Card(onClick = click, modifier = Modifier.fillMaxWidth().padding(bottom = 9.dp), shape = RoundedCornerShape(17.dp), colors = CardDefaults.cardColors(containerColor = Color.White), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) {
        Row(Modifier.padding(13.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.size(46.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) {
                Icon(Icons.Outlined.MusicNote, null, tint = Color.White, modifier = Modifier.size(24.dp))
            }
            Column(Modifier.padding(start = 13.dp).weight(1f)) {
                Text(name, color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                Text(status, color = if (status.contains("完成")) MoodifyGreen else if (status.contains("等待")) MoodifyOrange else MoodifyPurple, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                if (progress != null) LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth().padding(top = 6.dp).height(4.dp), color = MoodifyBlue, trackColor = MoodifyOutline)
            }
            Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted)
        }
    }
}
