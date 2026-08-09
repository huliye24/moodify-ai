package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.moodify.app.R
import com.moodify.app.data.LocaleKit
import com.moodify.app.data.LocaleStore
import com.moodify.app.data.WorkLibrary
import com.moodify.app.data.ProcessedWork
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private data class WorkItem(
    val title: String, val duration: String, val status: String, val date: String,
    val colors: List<Color>, val tags: List<Pair<ImageVector, String>>, val progress: Float? = null,
    val artifactId: String? = null, val uploadId: String? = null,
)

private val demoWorks = listOf(
    WorkItem("AI Demo Track", "03:24", "已完成", "2025-07-30 14:20", listOf(Color(0xFF5425C9), Color(0xFFA931D2), Color(0xFF283B9E)), listOf(Icons.Outlined.Verified to "标准处理", Icons.Outlined.GraphicEq to "响度优化", Icons.Outlined.ShowChart to "True Peak")),
    WorkItem("Dreamscape", "04:18", "已完成", "2025-07-30 11:15", listOf(Color(0xFF3948E8), Color(0xFF795CF4), Color(0xFF25258E)), listOf(Icons.Outlined.Verified to "标准处理", Icons.Outlined.GraphicEq to "响度标准化", Icons.Outlined.Tune to "频段平衡")),
    WorkItem("Sunset Drive", "03:57", "已完成", "2025-07-29 18:42", listOf(Color(0xFFFF936D), Color(0xFFE74A9D), Color(0xFF8A37A9)), listOf(Icons.Outlined.Verified to "标准处理", Icons.Outlined.PhoneAndroid to "平台适配", Icons.Outlined.ShowChart to "True Peak")),
    WorkItem("Midnight Walk", "02:45", "草稿", "2025-07-28 09:30", listOf(Color(0xFF75DFC5), Color(0xFF45C6C7), Color(0xFF3B9CB5)), listOf(Icons.Outlined.Timer to "未处理")),
)

private val realWorkColors = listOf(Color(0xFF7B61FF), Color(0xFF4A9BFF), Color(0xFF25258E))

/** Queue with [original, processed] adjacent per work for one-tap A/B. */
private fun buildQueue(works: List<ProcessedWork>, originalLabel: String, processedLabel: String): List<com.moodify.app.data.QueueItem> {
    val items = mutableListOf<com.moodify.app.data.QueueItem>()
    works.forEach { w ->
        w.uploadId?.let {
            items.add(com.moodify.app.data.QueueItem(
                title = w.filename,
                subtitle = originalLabel,
                path = "/uploads/$it/download",
                isOriginal = true,
                preset = w.preset,
            ))
        }
        w.artifactId?.let {
            items.add(com.moodify.app.data.QueueItem(
                title = w.filename,
                subtitle = processedLabel,
                path = "/artifacts/$it/download",
                isOriginal = false,
                preset = w.preset,
                mrsDelta = w.mrsDelta,
                gatePassed = w.gatePassed,
            ))
        }
    }
    return items
}

private fun realWorkItem(w: ProcessedWork, processedLabel: String, gatePassedLabel: String, gateFailedLabel: String, mrsImprovedLabel: String, dateLocale: Locale): WorkItem = WorkItem(
    title = w.filename,
    duration = processedLabel,
    status = if (w.gatePassed) gatePassedLabel else gateFailedLabel,
    date = SimpleDateFormat("yyyy-MM-dd HH:mm", dateLocale).format(Date(w.createdAt)),
    colors = realWorkColors,
    tags = buildList {
        add(Icons.Outlined.Verified to w.preset)
        w.mrsDelta?.let { add(Icons.Outlined.ShowChart to "MRS Δ+%.1f".format(it)) }
        add(Icons.Outlined.GraphicEq to (w.mrsBefore?.let { "MRS %.0f→%.0f".format(it, w.mrsAfter ?: 0.0) } ?: mrsImprovedLabel))
    },
    progress = null,
    artifactId = w.artifactId,
    uploadId = w.uploadId,
)

private fun playFromWorks(works: List<ProcessedWork>, item: WorkItem, originalLabel: String, processedLabel: String) {
    val queue = buildQueue(works, originalLabel, processedLabel)
    val idx = queue.indexOfFirst { !it.isOriginal && it.title == item.title }
    com.moodify.app.data.PlaybackManager.playQueue(queue, if (idx >= 0) idx else 0)
}

@Composable
fun WorksScreen(onBack: (() -> Unit)? = null, onOpenDetail: () -> Unit = {}) {
    val context = LocalContext.current
    val originalLabel = stringResource(R.string.works_original_audio)
    val processedLabel = stringResource(R.string.works_processed)
    val aiProcessedLabel = stringResource(R.string.works_ai_processed)
    val gatePassedLabel = stringResource(R.string.works_gate_passed)
    val gateFailedLabel = stringResource(R.string.works_gate_failed)
    val mrsImprovedLabel = stringResource(R.string.works_mrs_improved)
    val dateLocale = Locale.forLanguageTag(LocaleKit.normalize(LocaleStore.currentTag() ?: Locale.getDefault().toLanguageTag()))
    val realWorks = remember { WorkLibrary(context).all() }
    val works = realWorks.map { realWorkItem(it, processedLabel, gatePassedLabel, gateFailedLabel, mrsImprovedLabel, dateLocale) } + demoWorks
    val playbackState by com.moodify.app.data.PlaybackManager.state.collectAsStateWithLifecycle()
    androidx.compose.foundation.layout.Box(Modifier.fillMaxSize()) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = if (playbackState.url != null) 88.dp else 0.dp)) {
        Spacer(Modifier.height(24.dp))
        if (onBack == null) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp))
                Text("Moodify", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold)
            }
            Text(stringResource(R.string.works_motto), Modifier.fillMaxWidth(), color = MoodifyMuted, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        } else {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back)) }
                Text(stringResource(R.string.cases_title), Modifier.weight(1f), color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                Spacer(Modifier.width(48.dp))
            }
        }
        Spacer(Modifier.height(28.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text(stringResource(R.string.cases_title), color = MoodifyNavy, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
            OutlinedButton(onClick = {}, shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) {
                Text(stringResource(R.string.works_filter), color = MoodifyMuted); Spacer(Modifier.width(6.dp)); Icon(Icons.Outlined.FilterList, null, tint = MoodifyMuted, modifier = Modifier.size(18.dp))
            }
        }
        Spacer(Modifier.height(12.dp))
        works.forEach { item ->
            WorkCard(item, onOpenDetail, onPlay = item.artifactId?.let {
                { playFromWorks(realWorks, item, originalLabel, aiProcessedLabel) }
            })
            Spacer(Modifier.height(14.dp))
        }
        OutlinedButton(onClick = {}, modifier = Modifier.fillMaxWidth().height(54.dp), shape = RoundedCornerShape(27.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyBlue)) {
            Icon(Icons.Outlined.Add, null, tint = MoodifyBlue); Spacer(Modifier.width(8.dp)); Text(stringResource(R.string.works_import), color = MoodifyBlue, fontSize = 16.sp)
        }
        Spacer(Modifier.height(14.dp))
        Spacer(Modifier.height(20.dp))
    }
    com.moodify.app.ui.components.PlaybackBar(
        Modifier.align(androidx.compose.ui.Alignment.BottomCenter).padding(horizontal = 12.dp, vertical = 8.dp)
    )
    }
}

@Composable
private fun WorkCard(item: WorkItem, onOpenDetail: () -> Unit, onPlay: (() -> Unit)? = null) {
    Card(onClick = onOpenDetail, modifier = Modifier.fillMaxWidth().shadow(12.dp, RoundedCornerShape(22.dp), ambientColor = Color(0x160B214F), spotColor = Color(0x160B214F)), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Row(Modifier.padding(16.dp)) {
            Box(Modifier.size(82.dp).background(Brush.linearGradient(item.colors), RoundedCornerShape(14.dp))) {
                Box(Modifier.fillMaxSize().padding(14.dp).background(Color.White.copy(.08f), RoundedCornerShape(30.dp)))
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(item.title, color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                    IconButton(onClick = { onPlay?.invoke() }, modifier = Modifier.size(38.dp), enabled = onPlay != null) { Icon(Icons.Outlined.PlayArrow, null, tint = if (onPlay != null) MoodifyPurple else MoodifyMuted.copy(alpha = 0.4f)) }
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
