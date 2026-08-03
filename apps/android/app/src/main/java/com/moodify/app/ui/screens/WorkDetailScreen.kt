package com.moodify.app.ui.screens

import android.content.Intent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.ProcessedWork
import com.moodify.app.data.QueueItem
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.PlaybackBar
import com.moodify.app.ui.theme.*

@Composable
fun WorkDetailScreen(work: ProcessedWork?, onBack: () -> Unit, onProcessAgain: () -> Unit, onPublish: () -> Unit) {
    val context = LocalContext.current
    val title = work?.filename ?: "AI Demo Track"
    var playOriginal by remember { mutableStateOf(false) }
    val abQueue = remember(work) { buildAbQueue(work, title) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
        Spacer(Modifier.height(16.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回", tint = MoodifyNavy) }
            Text("作品详情", Modifier.weight(1f), color = MoodifyNavy, fontSize = 23.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            IconButton(onClick = {
                val intent = Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, "$title · Moodify 处理完成") }
                context.startActivity(Intent.createChooser(intent, "分享作品"))
            }) { Icon(Icons.Outlined.IosShare, "分享", tint = MoodifyNavy) }
        }
        Spacer(Modifier.height(16.dp))
        DetailCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(92.dp).background(Brush.linearGradient(listOf(Color(0xFF5425C9), Color(0xFFA931D2), Color(0xFF2840AE))), RoundedCornerShape(16.dp)))
                Column(Modifier.padding(start = 16.dp)) { Text(title, color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis); Text("泫榛  ✦", color = MoodifyNavy, fontSize = 14.sp); Spacer(Modifier.height(10.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Text(work?.preset ?: "标准处理", color = MoodifyMuted); Spacer(Modifier.width(12.dp)); StatusPill(if (work?.gatePassed == true) "质量门通过" else if (work == null) "已完成" else "质量门未通过") } }
            }
            Spacer(Modifier.height(18.dp)); DetailWaveform(Modifier.fillMaxWidth().height(42.dp))
            Spacer(Modifier.height(14.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                CompareButton("处理前", playOriginal && work?.uploadId != null, Modifier.weight(1f)) {
                    if (work?.uploadId != null) { playOriginal = true; PlaybackManager.playQueue(abQueue, 0) }
                }
                Spacer(Modifier.width(10.dp))
                CompareButton("处理后", !playOriginal && work?.artifactId != null, Modifier.weight(1f)) {
                    if (work?.artifactId != null) { playOriginal = false; PlaybackManager.playQueue(abQueue, 1) }
                }
            }
            Spacer(Modifier.height(12.dp))
            PlaybackBar()
            Spacer(Modifier.height(8.dp))
            Text("点击切换处理前/后，直观感受 AI 处理的音质提升", color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.align(Alignment.CenterHorizontally))
        }
        Spacer(Modifier.height(14.dp))
        DetailCard { Text("处理结果", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { ResultChip(Icons.Outlined.GraphicEq, work?.preset ?: "标准处理", true); ResultChip(Icons.Outlined.CheckCircle, "响度标准化"); ResultChip(Icons.Outlined.ShowChart, "True Peak") }; Spacer(Modifier.height(11.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyGreen, modifier = Modifier.size(20.dp)); Text("  声音已优化，可用于发布与存档", color = MoodifyMuted, fontSize = 13.sp) } }
        Spacer(Modifier.height(14.dp))
        DetailCard {
            Text("真实处理指标", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
            if (work != null) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    Metric(Icons.Outlined.GraphicEq, "处理方案", work.preset)
                    Metric(Icons.Outlined.Speed, "MRS 前", work.mrsBefore?.let { "%.1f".format(it) } ?: "—")
                    Metric(Icons.Outlined.ShowChart, "MRS 后", work.mrsAfter?.let { "%.1f".format(it) } ?: "—")
                    Metric(Icons.Outlined.Timelapse, "提升", work.mrsDelta?.let { "Δ%.1f".format(it) } ?: "—")
                }
                if (work.issues.isNotEmpty()) {
                    Spacer(Modifier.height(10.dp))
                    Text("诊断：${work.issues.take(2).joinToString("；")}", color = MoodifyMuted, fontSize = 11.sp)
                }
            } else {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Metric(Icons.Outlined.Speed, "LUFS", "-14 LUFS"); Metric(Icons.Outlined.ShowChart, "True Peak", "-1.0 dBTP"); Metric(Icons.Outlined.Timelapse, "动态范围", "8.6 dB"); Metric(Icons.Outlined.GraphicEq, "采样率", "48 kHz") }
            }
        }
        Spacer(Modifier.height(14.dp))
        DetailCard { Text("导出与发布", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { ExportAction(Icons.Outlined.FileDownload, "导出音频", "WAV / MP3", Modifier.weight(1f)) {}; ExportAction(Icons.Outlined.AudioFile, "下载曲谱", "PDF 格式", Modifier.weight(1f)) {}; ExportAction(Icons.Outlined.Publish, "发布作品", "分享给听众", Modifier.weight(1f), onPublish) } }
        Spacer(Modifier.height(18.dp)); GradientButton("再次处理", onProcessAgain); TextButton(onClick = {}) { Text("查看完整报告", color = MoodifyBlue, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }; Spacer(Modifier.height(18.dp))
    }
}

private fun buildAbQueue(work: ProcessedWork?, title: String): List<QueueItem> = buildList {
    if (work == null) return@buildList
    work.uploadId?.let {
        add(QueueItem("$title（处理前）", "原始音频", "/uploads/$it/download", isOriginal = true, preset = work.preset))
    }
    work.artifactId?.let {
        add(QueueItem(title, "AI 处理完成", "/artifacts/$it/download", isOriginal = false, preset = work.preset, mrsDelta = work.mrsDelta, gatePassed = work.gatePassed))
    }
}

@Composable
private fun CompareButton(label: String, selected: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(14.dp),
        color = if (selected) MoodifyPurple else Color.White,
        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) MoodifyPurple else MoodifyOutline),
        modifier = modifier,
    ) {
        Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
            Icon(if (selected) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, null, tint = if (selected) Color.White else MoodifyPurple, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(6.dp))
            Text(label, color = if (selected) Color.White else MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable private fun DetailCard(content: @Composable ColumnScope.() -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(5.dp)) { Column(Modifier.padding(18.dp), content = content) } }
@Composable private fun StatusPill(text: String) { Surface(color = Color(0xFFE8F8EE), shape = RoundedCornerShape(7.dp)) { Text(text, color = Color(0xFF32A763), fontSize = 12.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp)) } }
@Composable private fun ResultChip(icon: ImageVector, text: String, selected: Boolean = false) { Surface(shape = RoundedCornerShape(9.dp), border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) MoodifyPurple.copy(.25f) else MoodifyOutline), color = if (selected) Color(0xFFF7F5FF) else Color.White) { Row(Modifier.padding(horizontal = 8.dp, vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) { Icon(icon, null, tint = if (selected) MoodifyPurple else MoodifyMuted, modifier = Modifier.size(16.dp)); Text("  $text", color = if (selected) MoodifyPurple else MoodifyMuted, fontSize = 11.sp) } } }
@Composable private fun Metric(icon: ImageVector, label: String, value: String) { Column(horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(25.dp)); Text(label, color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp)); Text(value, color = MoodifyNavy, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 4.dp)) } }
@Composable private fun ExportAction(icon: ImageVector, title: String, subtitle: String, modifier: Modifier, onClick: () -> Unit) { OutlinedCard(onClick = onClick, modifier = modifier, shape = RoundedCornerShape(14.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Column(Modifier.fillMaxWidth().padding(vertical = 13.dp), horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(25.dp)); Text(title, color = MoodifyNavy, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 5.dp)); Text(subtitle, color = MoodifyMuted, fontSize = 9.sp) } } }
@Composable private fun DetailWaveform(modifier: Modifier) { Canvas(modifier) { val count = 68; repeat(count) { i -> val strength = (.18f + ((i * 37) % 19) / 25f) * (if (i < 25) 1f else .45f); val x = size.width * i / (count - 1); val half = size.height * strength / 2; drawLine(if (i < 25) MoodifyBlue else MoodifyOutline, Offset(x, size.height / 2 - half), Offset(x, size.height / 2 + half), 1.5.dp.toPx(), StrokeCap.Round) } } }
