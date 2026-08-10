package com.moodify.app.ui.screens

import android.media.MediaPlayer
import androidx.annotation.RawRes
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
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
import androidx.compose.ui.platform.LocalContext
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

private data class OfflineDemoCase(
    val caseId: String,
    val title: String,
    val note: String,
    @RawRes val sourceAudio: Int,
    @RawRes val candidateAudio: Int,
    val metrics: List<DemoMetric>,
)

private val offlineCases = listOf(
    OfflineDemoCase(
        caseId = "CASE 080BAC / B",
        title = "J'apprends la tendresse pour toi",
        note = "Presence restored while clipping remains at zero.",
        sourceAudio = R.raw.case_tendresse_source,
        candidateAudio = R.raw.case_tendresse_candidate,
        metrics = listOf(
            DemoMetric("PRESENCE", "2.53%", "3.84%"),
            DemoMetric("BASS", "18.24%", "15.66%"),
            DemoMetric("TRUE PEAK", "-3.71", "-3.36 dBFS"),
            DemoMetric("CLIPPING", "0", "0"),
        ),
    ),
    OfflineDemoCase(
        caseId = "CASE CF920E / B",
        title = "Des portes et des lampes",
        note = "Low-frequency weight reduced; presence and air increased.",
        sourceAudio = R.raw.case_portes_source,
        candidateAudio = R.raw.case_portes_candidate,
        metrics = listOf(
            DemoMetric("PRESENCE", "2.35%", "3.65%"),
            DemoMetric("BASS", "23.25%", "20.52%"),
            DemoMetric("WIDTH", "24.44%", "26.65%"),
            DemoMetric("CLIPPING", "0", "0"),
        ),
    ),
)

@Composable
fun WorksScreen(onBack: (() -> Unit)? = null, onOpenDetail: () -> Unit = {}) {
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
            OfflineCaseCard(demoCase)
            Spacer(Modifier.height(16.dp))
        }
        Spacer(Modifier.height(28.dp))
    }
}

@Composable
private fun OfflineCaseCard(demoCase: OfflineDemoCase) {
    val context = LocalContext.current
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var active by remember { mutableStateOf<String?>(null) }

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
            Row(Modifier.fillMaxWidth().padding(top = 18.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                AudioButton("A / SOURCE", active == "A", Modifier.weight(1f)) {
                    if (active == "A") stop() else play("A", demoCase.sourceAudio)
                }
                AudioButton("B / CANDIDATE", active == "B", Modifier.weight(1f)) {
                    if (active == "B") stop() else play("B", demoCase.candidateAudio)
                }
            }
            HorizontalDivider(Modifier.padding(vertical = 18.dp), color = MoodifyInstrumentOutline)
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
            Text("Human listening required · Artistic approval not granted", color = MoodifyInstrumentMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp))
        }
    }
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
