package com.moodify.app.ui.screens

import android.media.MediaPlayer
import androidx.annotation.RawRes
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Verified
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.MoodifyInstrumentField
import com.moodify.app.ui.theme.MoodifyInstrumentMuted
import com.moodify.app.ui.theme.MoodifyInstrumentOutline
import com.moodify.app.ui.theme.MoodifyInstrumentSignal
import com.moodify.app.ui.theme.MoodifyInstrumentSurface
import com.moodify.app.ui.theme.MoodifyInstrumentText

private data class DemoMetric(val label: String, val before: String, val after: String)

private data class ReportFigure(val title: String, val resource: Int)

private data class OfflineDemoCase(
    val caseId: String,
    val title: String,
    val note: String,
    val summary: String,
    val meaning: String,
    @RawRes val sourceAudio: Int,
    @RawRes val candidateAudio: Int,
    val metrics: List<DemoMetric>,
    val findings: List<String> = emptyList(),
    val interventionPlan: List<String> = emptyList(),
    val figures: List<ReportFigure> = emptyList(),
)

private val offlineCases = listOf(
    OfflineDemoCase(
        caseId = "CASE 080BAC / B",
        title = "J'apprends la tendresse pour toi",
        note = "Presence restored while clipping remains at zero.",
        summary = "候选版本的人声更清楚、更靠前，同时没有产生削波。低频占比被适度收回，为人声存在感让出空间。",
        meaning = "这是一种克制的音色再平衡，而不是单纯把声音变大。试听时要确认清晰度提升，同时没有失去温度与亲密感。",
        sourceAudio = R.raw.case_tendresse_source,
        candidateAudio = R.raw.case_tendresse_candidate,
        metrics = listOf(
            DemoMetric("PRESENCE", "2.53%", "3.84%"),
            DemoMetric("BASS", "18.24%", "15.66%"),
            DemoMetric("TRUE PEAK", "-3.71", "-3.36 dBFS"),
            DemoMetric("CLIPPING", "0", "0"),
        ),
        findings = listOf(
            "存在感能量由 2.53% 升至 3.84%，人声细节更容易被听见。",
            "低频占比由 18.24% 降至 15.66%，减少低频对人声的遮蔽。",
            "峰值提高 0.35 dB，但削波样本仍为零。",
            "这些数字能描述变化，但不能独立证明情感表达变得更好。",
        ),
        interventionPlan = listOf(
            "用 A/B 片段比较咬字清晰度与人声亲密感。",
            "确认低频减少没有让编曲显得单薄或变小。",
            "只有在人声更清楚且没有刺耳感时，才保留候选版本。",
            "在耳机与小型扬声器上复核后，再进行艺术批准。",
        ),
    ),
    OfflineDemoCase(
        caseId = "CASE CF920E / B",
        title = "Des portes et des lampes",
        note = "Low-frequency weight reduced; presence and air increased.",
        summary = "候选版本打开了混音空间：低频重量下降，人声轮廓与空气感上升，声场也略微变宽。",
        meaning = "这次干预的目标是解除拥挤，而不是重新设计歌曲。试听时应关注分离度是否改善，同时警惕声音变薄、变亮或声像不稳定。",
        sourceAudio = R.raw.case_portes_source,
        candidateAudio = R.raw.case_portes_candidate,
        metrics = listOf(
            DemoMetric("PRESENCE", "2.35%", "3.65%"),
            DemoMetric("BASS", "23.25%", "20.52%"),
            DemoMetric("WIDTH", "24.44%", "26.65%"),
            DemoMetric("CLIPPING", "0", "0"),
        ),
        findings = listOf(
            "存在感由 2.35% 升至 3.65%，中高频轮廓更加明确。",
            "低频占比由 23.25% 降至 20.52%，中央声像周围获得更多空间。",
            "立体声宽度由 24.44% 升至 26.65%；变化克制，最终仍需结合听感判断。",
            "测得的候选版本没有引入削波。",
        ),
        interventionPlan = listOf(
            "判断低频减少是否改善分离度，同时没有削弱冲击力。",
            "在偏亮的耳机上检查人声存在感是否转为尖锐。",
            "声场加宽后复核单声道兼容性。",
            "只有在空间更开放且歌曲重量感仍被保留时，才批准候选版本。",
        ),
    ),
    OfflineDemoCase(
        caseId = "DEEP EAR / V4 -> V5",
        title = "Vieillir et devenir nouveau avec toi",
        note = "Auditory scan and de-esser intervention verification.",
        summary = "V5 在没有产生削波的前提下控制了齿音，并保留了有效的动态起伏；变化不只是简单的音量调整。",
        meaning = "候选版本在技术上已具备进入听感复核的条件。尚未解决的是艺术问题：去齿音是否降低了疲劳感，同时保留人声空气感、生命力与情感距离？",
        sourceAudio = R.raw.case_vieillir_v4,
        candidateAudio = R.raw.case_vieillir_v5,
        metrics = listOf(
            DemoMetric("INTEGRATED", "V5", "-10.53 LUFS"),
            DemoMetric("TRUE PEAK", "V5", "-0.96 dBTP est."),
            DemoMetric("CREST FACTOR", "V5", "13.59 dB"),
            DemoMetric("CLIPPING", "V5", "0 samples"),
            DemoMetric("V4 -> V5 RESIDUAL", "0 ms lag", "10.26%"),
        ),
        findings = listOf(
            "V5 未检测到削波或非有限数值样本。",
            "动态轮廓仍然活跃：峰均比为 13.59 dB。",
            "立体声相关性总体连贯；6.27% 的帧为负相关，需要重点试听。",
            "在约 17.86 kHz 处检测到频谱边缘，置信度 0.55；这是一项启发式观察。",
            "V5 与 V4 的差异不只是整体增益：相对残差为 10.26%，对齐延迟为零。",
        ),
        interventionPlan = listOf(
            "以 V4 为试听参考，以 V5 为去齿音候选版本。",
            "结合人声清晰度、瞬态生命力与空气感，判断齿音控制是否合适。",
            "将真峰值保持在约 -0.95 dBTP 或以下，并确保不产生削波。",
            "在耳机和扬声器上完成真人 A/B 试听后，才授予艺术批准。",
        ),
        figures = listOf(
            ReportFigure("LOUDNESS EVOLUTION", R.drawable.report_vieillir_loudness),
            ReportFigure("AVERAGE SPECTRUM", R.drawable.report_vieillir_spectrum),
            ReportFigure("BEFORE / AFTER / RESIDUAL", R.drawable.report_vieillir_residual),
            ReportFigure("HIGH-FREQUENCY CUTOFF", R.drawable.report_vieillir_hf_cutoff),
        ),
    ),
)

@Composable
fun WorksScreen(onBack: (() -> Unit)? = null, onOpenDetail: () -> Unit = {}) {
    var selectedCase by remember { mutableStateOf<OfflineDemoCase?>(null) }
    selectedCase?.let { demoCase ->
        CaseDetailScreen(demoCase = demoCase, onBack = { selectedCase = null })
        return
    }

    Column(
        Modifier
            .fillMaxSize()
            .background(MoodifyInstrumentField)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp),
    ) {
        Row(
            Modifier.fillMaxWidth().padding(top = 18.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (onBack != null) {
                IconButton(onClick = onBack) {
                    Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back), tint = MoodifyInstrumentMuted)
                }
            } else {
                Spacer(Modifier.size(48.dp))
            }
            Row(
                Modifier.weight(1f),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                MoodifyMark(Modifier.size(35.dp, 22.dp))
                Text("EVIDENCE", color = MoodifyInstrumentText, fontSize = 12.sp, letterSpacing = 2.1.sp, modifier = Modifier.padding(start = 10.dp))
            }
            Spacer(Modifier.size(48.dp))
        }
        Spacer(Modifier.height(42.dp))
        Text("OFFLINE DEMONSTRATION / V1", color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge)
        Text(
            stringResource(R.string.cases_title),
            color = MoodifyInstrumentText,
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
        Text(
            "Real precomputed cases. No server connection required.",
            color = MoodifyInstrumentMuted,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 10.dp, bottom = 24.dp),
        )
        offlineCases.forEach { demoCase ->
            OfflineCaseListCard(demoCase = demoCase, onClick = { selectedCase = demoCase })
            Spacer(Modifier.height(16.dp))
        }
        Spacer(Modifier.height(28.dp))
    }
}

@Composable
private fun OfflineCaseListCard(demoCase: OfflineDemoCase, onClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, MoodifyInstrumentOutline),
        colors = CardDefaults.cardColors(containerColor = MoodifyInstrumentSurface),
        elevation = CardDefaults.cardElevation(0.dp),
    ) {
        Row(Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(demoCase.caseId, color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge)
                Text(demoCase.title, color = MoodifyInstrumentText, style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(top = 12.dp))
                Text(demoCase.summary, color = MoodifyInstrumentMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 8.dp))
                Row(Modifier.padding(top = 15.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(7.dp).background(MoodifyInstrumentSignal, CircleShape))
                    Text("OFFLINE · A/B READY", color = MoodifyInstrumentMuted, fontSize = 9.sp, letterSpacing = .8.sp, modifier = Modifier.padding(start = 8.dp))
                }
            }
            Icon(Icons.Outlined.ChevronRight, "Open case", tint = MoodifyInstrumentSignal, modifier = Modifier.padding(start = 14.dp))
        }
    }
}

@Composable
private fun CaseDetailScreen(demoCase: OfflineDemoCase, onBack: () -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .background(MoodifyInstrumentField)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp),
    ) {
        Row(Modifier.fillMaxWidth().padding(top = 18.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back), tint = MoodifyInstrumentMuted)
            }
            Text("CASE REPORT", color = MoodifyInstrumentText, fontSize = 12.sp, letterSpacing = 2.1.sp, modifier = Modifier.padding(start = 10.dp))
        }
        Spacer(Modifier.height(24.dp))
        OfflineCaseCard(demoCase)
        Spacer(Modifier.height(32.dp))
    }
}

@Composable
private fun OfflineCaseCard(demoCase: OfflineDemoCase) {
    val context = LocalContext.current
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var active by remember { mutableStateOf<String?>(null) }
    var reportExpanded by remember { mutableStateOf(true) }

    fun play(label: String, @RawRes resource: Int) {
        player?.release()
        player = MediaPlayer.create(context, resource).apply {
            setOnCompletionListener {
                active = null
                it.release()
                player = null
            }
            start()
        }
        active = label
    }

    fun stop() {
        player?.release()
        player = null
        active = null
    }

    DisposableEffect(Unit) { onDispose { player?.release() } }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, MoodifyInstrumentOutline),
        colors = CardDefaults.cardColors(containerColor = MoodifyInstrumentSurface),
        elevation = CardDefaults.cardElevation(0.dp),
    ) {
        Column(Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(7.dp).background(MoodifyInstrumentSignal, CircleShape))
                Text(demoCase.caseId, color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge, modifier = Modifier.padding(start = 10.dp))
                Spacer(Modifier.weight(1f))
                Text("REAL CASE", color = MoodifyInstrumentMuted, fontSize = 9.sp, letterSpacing = 1.sp)
            }
            Text(demoCase.title, color = MoodifyInstrumentText, style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(top = 18.dp))
            Text(demoCase.note, color = MoodifyInstrumentMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 7.dp))
            Text("EXECUTIVE SUMMARY", color = MoodifyInstrumentSignal, fontSize = 10.sp, letterSpacing = 1.2.sp, modifier = Modifier.padding(top = 20.dp))
            Text(demoCase.summary, color = MoodifyInstrumentText, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = 9.dp))
            Text("WHAT THIS MEANS", color = MoodifyInstrumentMuted, fontSize = 9.sp, letterSpacing = 1.sp, modifier = Modifier.padding(top = 16.dp))
            Text(demoCase.meaning, color = MoodifyInstrumentMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 7.dp))
            Row(Modifier.fillMaxWidth().padding(top = 18.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                AudioButton("A / SOURCE", active == "A", Modifier.weight(1f)) {
                    if (active == "A") stop() else play("A", demoCase.sourceAudio)
                }
                AudioButton("B / CANDIDATE", active == "B", Modifier.weight(1f)) {
                    if (active == "B") stop() else play("B", demoCase.candidateAudio)
                }
            }
            HorizontalDivider(Modifier.padding(vertical = 18.dp), color = MoodifyInstrumentOutline)
            Text("SOUND STATE / BEFORE -> AFTER", color = MoodifyInstrumentSignal, fontSize = 10.sp, letterSpacing = 1.2.sp, modifier = Modifier.padding(bottom = 9.dp))
            demoCase.metrics.forEach { metric ->
                Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(metric.label, color = MoodifyInstrumentMuted, fontSize = 10.sp, letterSpacing = .7.sp, modifier = Modifier.weight(1f))
                    Text(metric.before, color = MoodifyInstrumentMuted, fontSize = 12.sp)
                    Text("  ->  ", color = MoodifyInstrumentOutline, fontSize = 12.sp)
                    Text(metric.after, color = MoodifyInstrumentText, fontSize = 12.sp)
                }
            }
            Row(Modifier.padding(top = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.Verified, null, tint = MoodifyInstrumentSignal, modifier = Modifier.size(17.dp))
                Text("PASS TO LISTENING", color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge, modifier = Modifier.padding(start = 9.dp))
            }
            if (demoCase.findings.isNotEmpty()) {
                OutlinedButton(
                    onClick = { reportExpanded = !reportExpanded },
                    modifier = Modifier.fillMaxWidth().padding(top = 18.dp).height(44.dp),
                    shape = RoundedCornerShape(9.dp),
                    border = BorderStroke(1.dp, MoodifyInstrumentOutline),
                ) {
                    Icon(Icons.Outlined.GraphicEq, null, tint = MoodifyInstrumentSignal, modifier = Modifier.size(17.dp))
                    Text(
                        if (reportExpanded) "HIDE SCAN REPORT" else "VIEW SCAN REPORT",
                        color = MoodifyInstrumentText,
                        fontSize = 10.sp,
                        letterSpacing = .8.sp,
                        modifier = Modifier.padding(start = 8.dp),
                    )
                }
            }
            if (reportExpanded) {
                ReportSection("MACHINE ANALYSIS") {
                    demoCase.findings.forEach { finding ->
                        Text("•  $finding", color = MoodifyInstrumentMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 9.dp))
                    }
                }
                ReportSection("POST-PROCESSING PLAN") {
                    demoCase.interventionPlan.forEachIndexed { index, item ->
                        Row(Modifier.padding(top = 10.dp), verticalAlignment = Alignment.Top) {
                            Text("0${index + 1}", color = MoodifyInstrumentSignal, fontSize = 10.sp, modifier = Modifier.padding(top = 2.dp))
                            Text(item, color = MoodifyInstrumentMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(start = 12.dp))
                        }
                    }
                }
                if (demoCase.figures.isNotEmpty()) {
                    ReportSection("EVIDENCE ARTIFACTS") {
                        demoCase.figures.forEach { figure ->
                            Text(figure.title, color = MoodifyInstrumentMuted, fontSize = 9.sp, letterSpacing = 1.sp, modifier = Modifier.padding(top = 14.dp, bottom = 7.dp))
                            Image(
                                painter = painterResource(figure.resource),
                                contentDescription = figure.title,
                                modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)),
                            )
                        }
                        Text("Charts support measurement review; they do not determine artistic quality.", color = MoodifyInstrumentMuted, fontSize = 9.sp, modifier = Modifier.padding(top = 14.dp))
                    }
                }
            }
            Text("Human listening required · Artistic approval not granted", color = MoodifyInstrumentMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp))
        }
    }
}

@Composable
private fun ReportSection(title: String, content: @Composable () -> Unit) {
    HorizontalDivider(Modifier.padding(top = 20.dp, bottom = 18.dp), color = MoodifyInstrumentOutline)
    Text(title, color = MoodifyInstrumentSignal, fontSize = 10.sp, letterSpacing = 1.2.sp)
    content()
}

@Composable
private fun AudioButton(label: String, playing: Boolean, modifier: Modifier, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier.height(46.dp),
        shape = RoundedCornerShape(9.dp),
        border = BorderStroke(1.dp, if (playing) MoodifyInstrumentSignal else MoodifyInstrumentOutline),
    ) {
        Icon(
            if (playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow,
            null,
            tint = if (playing) MoodifyInstrumentSignal else MoodifyInstrumentMuted,
            modifier = Modifier.size(17.dp),
        )
        Text(label, color = if (playing) MoodifyInstrumentText else MoodifyInstrumentMuted, fontSize = 10.sp, modifier = Modifier.padding(start = 6.dp))
    }
}
