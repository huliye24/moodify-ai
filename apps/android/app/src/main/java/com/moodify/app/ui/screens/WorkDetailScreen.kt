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
import androidx.compose.runtime.Composable
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
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.theme.*

@Composable
fun WorkDetailScreen(onBack: () -> Unit, onProcessAgain: () -> Unit, onPublish: () -> Unit) {
    val context = LocalContext.current
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
        Spacer(Modifier.height(16.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回", tint = MoodifyNavy) }
            Text("作品详情", Modifier.weight(1f), color = MoodifyNavy, fontSize = 23.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            IconButton(onClick = {
                val intent = Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, "AI Demo Track · Moodify 处理完成") }
                context.startActivity(Intent.createChooser(intent, "分享作品"))
            }) { Icon(Icons.Outlined.IosShare, "分享", tint = MoodifyNavy) }
        }
        Spacer(Modifier.height(16.dp))
        DetailCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(92.dp).background(Brush.linearGradient(listOf(Color(0xFF5425C9), Color(0xFFA931D2), Color(0xFF2840AE))), RoundedCornerShape(16.dp)))
                Column(Modifier.padding(start = 16.dp)) { Text("AI Demo Track", color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold); Text("泫榛  ✦", color = MoodifyNavy, fontSize = 14.sp); Spacer(Modifier.height(10.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Text("03:24", color = MoodifyMuted); Spacer(Modifier.width(12.dp)); StatusPill("已完成") } }
            }
            Spacer(Modifier.height(18.dp)); DetailWaveform(Modifier.fillMaxWidth().height(42.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Text("01:12", color = MoodifyMuted, fontSize = 12.sp); Text("03:24", color = MoodifyMuted, fontSize = 12.sp) }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = {}) { Icon(Icons.Outlined.SkipPrevious, null, tint = MoodifyBlue) }; Spacer(Modifier.width(30.dp)); FilledIconButton(onClick = {}, modifier = Modifier.size(62.dp), colors = IconButtonDefaults.filledIconButtonColors(containerColor = MoodifyPurple)) { Icon(Icons.Outlined.Pause, "暂停", tint = Color.White, modifier = Modifier.size(30.dp)) }; Spacer(Modifier.width(30.dp)); IconButton(onClick = {}) { Icon(Icons.Outlined.SkipNext, null, tint = MoodifyBlue) }
            }
        }
        Spacer(Modifier.height(14.dp))
        DetailCard { Text("处理结果", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { ResultChip(Icons.Outlined.GraphicEq, "标准处理", true); ResultChip(Icons.Outlined.CheckCircle, "响度标准化"); ResultChip(Icons.Outlined.ShowChart, "True Peak") }; Spacer(Modifier.height(11.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyGreen, modifier = Modifier.size(20.dp)); Text("  声音已优化，可用于发布与存档", color = MoodifyMuted, fontSize = 13.sp) } }
        Spacer(Modifier.height(14.dp))
        DetailCard { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Metric(Icons.Outlined.Speed, "LUFS", "-14 LUFS"); Metric(Icons.Outlined.ShowChart, "True Peak", "-1.0 dBTP"); Metric(Icons.Outlined.Timelapse, "动态范围", "8.6 dB"); Metric(Icons.Outlined.GraphicEq, "采样率", "48 kHz") } }
        Spacer(Modifier.height(14.dp))
        DetailCard { Text("导出与发布", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { ExportAction(Icons.Outlined.FileDownload, "导出音频", "WAV / MP3", Modifier.weight(1f)) {}; ExportAction(Icons.Outlined.AudioFile, "下载曲谱", "PDF 格式", Modifier.weight(1f)) {}; ExportAction(Icons.Outlined.Publish, "发布作品", "分享给听众", Modifier.weight(1f), onPublish) } }
        Spacer(Modifier.height(18.dp)); GradientButton("再次处理", onProcessAgain); TextButton(onClick = {}) { Text("查看完整报告", color = MoodifyBlue, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }; Spacer(Modifier.height(18.dp))
    }
}

@Composable private fun DetailCard(content: @Composable ColumnScope.() -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(5.dp)) { Column(Modifier.padding(18.dp), content = content) } }
@Composable private fun StatusPill(text: String) { Surface(color = Color(0xFFE8F8EE), shape = RoundedCornerShape(7.dp)) { Text(text, color = Color(0xFF32A763), fontSize = 12.sp, modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp)) } }
@Composable private fun ResultChip(icon: ImageVector, text: String, selected: Boolean = false) { Surface(shape = RoundedCornerShape(9.dp), border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) MoodifyPurple.copy(.25f) else MoodifyOutline), color = if (selected) Color(0xFFF7F5FF) else Color.White) { Row(Modifier.padding(horizontal = 8.dp, vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) { Icon(icon, null, tint = if (selected) MoodifyPurple else MoodifyMuted, modifier = Modifier.size(16.dp)); Text("  $text", color = if (selected) MoodifyPurple else MoodifyMuted, fontSize = 11.sp) } } }
@Composable private fun Metric(icon: ImageVector, label: String, value: String) { Column(horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(25.dp)); Text(label, color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp)); Text(value, color = MoodifyNavy, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 4.dp)) } }
@Composable private fun ExportAction(icon: ImageVector, title: String, subtitle: String, modifier: Modifier, onClick: () -> Unit) { OutlinedCard(onClick = onClick, modifier = modifier, shape = RoundedCornerShape(14.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Column(Modifier.fillMaxWidth().padding(vertical = 13.dp), horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(25.dp)); Text(title, color = MoodifyNavy, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 5.dp)); Text(subtitle, color = MoodifyMuted, fontSize = 9.sp) } } }
@Composable private fun DetailWaveform(modifier: Modifier) { Canvas(modifier) { val count = 68; repeat(count) { i -> val strength = (.18f + ((i * 37) % 19) / 25f) * (if (i < 25) 1f else .45f); val x = size.width * i / (count - 1); val half = size.height * strength / 2; drawLine(if (i < 25) MoodifyBlue else MoodifyOutline, Offset(x, size.height / 2 - half), Offset(x, size.height / 2 + half), 1.5.dp.toPx(), StrokeCap.Round) } } }
