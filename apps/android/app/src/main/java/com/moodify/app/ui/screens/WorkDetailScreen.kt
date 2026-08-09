package com.moodify.app.ui.screens

import android.content.Context
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.data.BaseUrlStore
import com.moodify.app.data.MoodifyApiClient
import com.moodify.app.data.PairwiseJudgmentResult
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.ProcessedWork
import com.moodify.app.data.QueueItem
import com.moodify.app.data.TokenStore
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.PlaybackBar
import com.moodify.app.ui.theme.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun WorkDetailScreen(work: ProcessedWork?, onBack: () -> Unit, onProcessAgain: () -> Unit) {
    val context = LocalContext.current
    val title = work?.filename ?: "AI Demo Track"
    var playOriginal by remember { mutableStateOf(false) }
    var reportOpen by remember { mutableStateOf(false) }
    val abQueue = remember(work) { buildAbQueue(context, work, title) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
        Spacer(Modifier.height(16.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back), tint = MoodifyNavy) }
            Text(stringResource(R.string.work_detail_title), Modifier.weight(1f), color = MoodifyNavy, fontSize = 23.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            IconButton(onClick = {
                val intent = Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, context.getString(R.string.work_share_text, title)) }
                context.startActivity(Intent.createChooser(intent, context.getString(R.string.work_share)))
            }) { Icon(Icons.Outlined.IosShare, stringResource(R.string.work_share), tint = MoodifyNavy) }
        }
        Spacer(Modifier.height(16.dp))
        DetailCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(92.dp).background(Brush.linearGradient(listOf(Color(0xFF5425C9), Color(0xFFA931D2), Color(0xFF2840AE))), RoundedCornerShape(16.dp)))
                Column(Modifier.padding(start = 16.dp)) { Text(title, color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis); Text("泫榛  ✦", color = MoodifyNavy, fontSize = 14.sp); Spacer(Modifier.height(10.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Text(work?.preset ?: "标准处理", color = MoodifyMuted); Spacer(Modifier.width(12.dp)); StatusPill(if (work?.gatePassed == true) stringResource(R.string.works_gate_passed) else if (work == null) stringResource(R.string.work_detail_done) else stringResource(R.string.works_gate_failed)) } }
            }
            Spacer(Modifier.height(18.dp)); DetailWaveform(Modifier.fillMaxWidth().height(42.dp))
            Spacer(Modifier.height(14.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                CompareButton(stringResource(R.string.work_detail_before), playOriginal && work?.uploadId != null, Modifier.weight(1f)) {
                    if (work?.uploadId != null) { playOriginal = true; PlaybackManager.playQueue(abQueue, 0) }
                }
                Spacer(Modifier.width(10.dp))
                CompareButton(stringResource(R.string.work_detail_after), !playOriginal && work?.artifactId != null, Modifier.weight(1f)) {
                    if (work?.artifactId != null) { playOriginal = false; PlaybackManager.playQueue(abQueue, 1) }
                }
            }
            Spacer(Modifier.height(12.dp))
            PlaybackBar()
            Spacer(Modifier.height(8.dp))
            Text(stringResource(R.string.work_detail_ab_hint), color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.align(Alignment.CenterHorizontally))
        }
        Spacer(Modifier.height(14.dp))
        if (work != null) { JudgeCard(work); Spacer(Modifier.height(14.dp)) }
        DetailCard { Text(stringResource(R.string.work_detail_results), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { ResultChip(Icons.Outlined.GraphicEq, work?.preset ?: "标准处理", true); ResultChip(Icons.Outlined.CheckCircle, "响度标准化"); ResultChip(Icons.Outlined.ShowChart, "True Peak") }; Spacer(Modifier.height(11.dp)); Row(verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.CheckCircle, null, tint = MoodifyGreen, modifier = Modifier.size(20.dp)); Text("  " + stringResource(R.string.work_detail_optimized), color = MoodifyMuted, fontSize = 13.sp) } }
        Spacer(Modifier.height(14.dp))
        DetailCard {
            Text(stringResource(R.string.work_detail_metrics_title), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
            if (work != null) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    Metric(Icons.Outlined.GraphicEq, stringResource(R.string.work_detail_metric_preset), work.preset)
                    Metric(Icons.Outlined.Speed, stringResource(R.string.work_detail_mrs_before), work.mrsBefore?.let { "%.1f".format(it) } ?: "—")
                    Metric(Icons.Outlined.ShowChart, stringResource(R.string.work_detail_mrs_after), work.mrsAfter?.let { "%.1f".format(it) } ?: "—")
                    Metric(Icons.Outlined.Timelapse, stringResource(R.string.work_detail_improvement), work.mrsDelta?.let { "Δ%.1f".format(it) } ?: "—")
                }
                if (work.issues.isNotEmpty()) {
                    Spacer(Modifier.height(10.dp))
                    Text(stringResource(R.string.work_detail_diagnosis, work.issues.take(2).joinToString("；")), color = MoodifyMuted, fontSize = 11.sp)
                }
            } else {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Metric(Icons.Outlined.Speed, "LUFS", "-14 LUFS"); Metric(Icons.Outlined.ShowChart, "True Peak", "-1.0 dBTP"); Metric(Icons.Outlined.Timelapse, stringResource(R.string.work_detail_dynamic_range), "8.6 dB"); Metric(Icons.Outlined.GraphicEq, stringResource(R.string.work_detail_sample_rate), "48 kHz") }
            }
        }
        Spacer(Modifier.height(14.dp))
        DetailCard { Text(stringResource(R.string.work_detail_export_title), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(12.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { ExportAction(Icons.Outlined.FileDownload, stringResource(R.string.work_detail_export_audio), "WAV / MP3", Modifier.weight(1f)) {}; ExportAction(Icons.Outlined.AudioFile, stringResource(R.string.work_detail_download_score), "PDF 格式", Modifier.weight(1f)) {} } }
        Spacer(Modifier.height(18.dp)); GradientButton(stringResource(R.string.work_detail_reprocess), onProcessAgain); TextButton(onClick = { reportOpen = true }) { Text(stringResource(R.string.work_detail_full_report), color = MoodifyBlue, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }; Spacer(Modifier.height(18.dp))
    }
    if (reportOpen) {
        AlertDialog(
            onDismissRequest = { reportOpen = false },
            confirmButton = { TextButton(onClick = { reportOpen = false }) { Text("Close") } },
            title = { Text("Auditory Report") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Moodify heard: ${work?.filename ?: title}", fontWeight = FontWeight.Bold)
                    Text("Technical status: ${if (work?.gatePassed == true) "reviewable" else "partial / review required"}")
                    Text("Findings: ${work?.issues?.take(3)?.joinToString() ?: "No persisted findings"}")
                    Text("Evidence: persisted case measurements and analysis artifacts")
                    Text("Human listening authority is required for artistic approval.", color = MoodifyPurple)
                }
            },
        )
    }
}

@Composable
private fun JudgeCard(work: ProcessedWork) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var judging by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<PairwiseJudgmentResult?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var humanDecision by remember { mutableStateOf<String?>(null) }

    val client = remember {
        MoodifyApiClient(baseUrlProvider = { BaseUrlStore(context).baseUrl })
    }
    val token = remember { TokenStore(context).token() }
    val requiresPairingLabel = stringResource(R.string.judge_requires_pairing)
    val failedLabel = stringResource(R.string.judge_failed)

    fun judge() {
        val uploadId = work.uploadId
        val artifactId = work.artifactId
        val currentToken = token
        if (uploadId == null || artifactId == null || currentToken == null) {
            error = requiresPairingLabel
            return
        }
        scope.launch {
            judging = true
            error = null
            try {
                result = withContext(Dispatchers.IO) {
                    client.judgePair(uploadId, artifactId, null, currentToken)
                }
            } catch (e: Exception) {
                error = failedLabel
            } finally {
                judging = false
            }
        }
    }

    fun submitDecision(decision: String) {
        val current = result ?: return
        val currentToken = token ?: return
        scope.launch {
            try {
                withContext(Dispatchers.IO) {
                    client.submitHumanDecision(current.judgmentId, decision, "", currentToken)
                }
                humanDecision = decision
            } catch (e: Exception) {
                error = failedLabel
            }
        }
    }

    DetailCard {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.Gavel, null, tint = MoodifyPurple, modifier = Modifier.size(22.dp))
            Text(stringResource(R.string.judge_title), color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(start = 8.dp))
        }
        Spacer(Modifier.height(12.dp))
        val current = result
        when {
            judging -> Row(verticalAlignment = Alignment.CenterVertically) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = MoodifyPurple)
                Spacer(Modifier.width(10.dp))
                Text(stringResource(R.string.judge_start), color = MoodifyMuted, fontSize = 12.sp)
            }
            current != null -> {
                val outcomeLabel = when (current.outcome) {
                    "A_WINS" -> stringResource(R.string.judge_outcome_a_wins)
                    "B_WINS" -> stringResource(R.string.judge_outcome_b_wins)
                    else -> stringResource(R.string.judge_outcome_inconclusive)
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(color = if (current.outcome == "INCONCLUSIVE") Color(0xFFFFF2E8) else Color(0xFFE8F8EE), shape = RoundedCornerShape(9.dp)) {
                        Text(outcomeLabel, color = if (current.outcome == "INCONCLUSIVE") Color(0xFFE08A3C) else Color(0xFF31A35E), fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
                    }
                    Spacer(Modifier.width(10.dp))
                    Text(stringResource(R.string.judge_confidence, current.confidenceLevel), color = MoodifyMuted, fontSize = 11.sp)
                }
                if (current.topReasons.isNotEmpty()) {
                    Spacer(Modifier.height(8.dp))
                    Text(stringResource(R.string.judge_reasons) + "：${current.topReasons.take(2).joinToString("；")}", color = MoodifyMuted, fontSize = 10.sp)
                }
                Spacer(Modifier.height(12.dp))
                if (humanDecision == null) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(onClick = { submitDecision("CONFIRM_MODEL") }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(14.dp)) { Text(stringResource(R.string.judge_confirm_model), fontSize = 11.sp) }
                        OutlinedButton(onClick = { submitDecision("CHOOSE_A") }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(14.dp)) { Text(stringResource(R.string.judge_choose_a), fontSize = 11.sp) }
                        OutlinedButton(onClick = { submitDecision("CHOOSE_B") }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(14.dp)) { Text(stringResource(R.string.judge_choose_b), fontSize = 11.sp) }
                        OutlinedButton(onClick = { submitDecision("UNDECIDED") }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(14.dp)) { Text(stringResource(R.string.judge_undecided), fontSize = 11.sp) }
                    }
                } else {
                    Text(stringResource(R.string.judge_recorded, humanDecision ?: ""), color = MoodifyPurple, fontSize = 11.sp)
                }
            }
            else -> {
                Button(onClick = { judge() }, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = MoodifyPurple), shape = RoundedCornerShape(16.dp)) {
                    Icon(Icons.Outlined.Gavel, null, modifier = Modifier.size(17.dp))
                    Spacer(Modifier.width(6.dp))
                    Text(stringResource(R.string.judge_start), color = Color.White)
                }
            }
        }
        error?.let {
            Spacer(Modifier.height(8.dp))
            Text(it, color = Color(0xFFE05B5B), fontSize = 11.sp)
        }
    }
}

private fun buildAbQueue(context: Context, work: ProcessedWork?, title: String): List<QueueItem> = buildList {
    if (work == null) return@buildList
    work.uploadId?.let {
        add(QueueItem(context.getString(R.string.work_detail_ab_before, title), context.getString(R.string.works_original_audio), "/uploads/$it/download", isOriginal = true, preset = work.preset))
    }
    work.artifactId?.let {
        add(QueueItem(title, context.getString(R.string.works_ai_processed), "/artifacts/$it/download", isOriginal = false, preset = work.preset, mrsDelta = work.mrsDelta, gatePassed = work.gatePassed))
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
