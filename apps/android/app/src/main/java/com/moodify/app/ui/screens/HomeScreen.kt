package com.moodify.app.ui.screens

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
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.Menu
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
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

private val auditoryLoop = listOf("LISTEN", "REPRESENT", "JUDGE", "INTERVENE", "VERIFY", "LEARN")

@Composable
fun HomeScreen(onOpenDrawer: () -> Unit = {}, onStartAnalysis: () -> Unit = {}) {
    Column(
        Modifier
            .fillMaxSize()
            .background(MoodifyInstrumentField)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp),
    ) {
        InstrumentHeader(onOpenDrawer)
        Spacer(Modifier.height(42.dp))
        Text(
            "AUDITORY INTELLIGENCE / 01",
            color = MoodifyInstrumentSignal,
            style = MaterialTheme.typography.labelLarge,
        )
        Spacer(Modifier.height(12.dp))
        Text(
            stringResource(R.string.home_title),
            color = MoodifyInstrumentText,
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            stringResource(R.string.home_subtitle),
            color = MoodifyInstrumentMuted,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
        Spacer(Modifier.height(34.dp))
        ListeningState(onStartAnalysis)
        Spacer(Modifier.height(28.dp))
        LoopSequence()
        Spacer(Modifier.height(36.dp))
        EvidenceList()
        Spacer(Modifier.height(36.dp))
    }
}

@Composable
private fun InstrumentHeader(onOpenDrawer: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().padding(top = 18.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(onClick = onOpenDrawer) {
            Icon(Icons.Outlined.Menu, stringResource(R.string.accessibility_open_menu), tint = MoodifyInstrumentMuted)
        }
        Row(
            Modifier.weight(1f),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            MoodifyMark(Modifier.size(35.dp, 22.dp))
            Text(
                "MOODIFY",
                color = MoodifyInstrumentText,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                letterSpacing = 2.1.sp,
                modifier = Modifier.padding(start = 10.dp),
            )
        }
        Spacer(Modifier.size(48.dp))
    }
}

@Composable
private fun ListeningState(onStartAnalysis: () -> Unit) {
    Card(
        onClick = onStartAnalysis,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, MoodifyInstrumentOutline),
        colors = CardDefaults.cardColors(containerColor = MoodifyInstrumentSurface),
        elevation = CardDefaults.cardElevation(0.dp),
    ) {
        Column(Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(7.dp).background(MoodifyInstrumentSignal, CircleShape))
                Text(
                    "SYSTEM READY",
                    color = MoodifyInstrumentSignal,
                    style = MaterialTheme.typography.labelLarge,
                    modifier = Modifier.padding(start = 10.dp),
                )
                Spacer(Modifier.weight(1f))
                Text("HUMAN AUTHORITY", color = MoodifyInstrumentMuted, fontSize = 10.sp, letterSpacing = 1.sp)
            }
            HorizontalDivider(Modifier.padding(vertical = 18.dp), color = MoodifyInstrumentOutline)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    Modifier.size(48.dp).background(MoodifyInstrumentSignal.copy(alpha = .10f), RoundedCornerShape(10.dp)),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(Icons.Outlined.GraphicEq, null, tint = MoodifyInstrumentSignal, modifier = Modifier.size(25.dp))
                }
                Column(Modifier.padding(start = 16.dp)) {
                    Text(
                        stringResource(R.string.home_start_analysis),
                        color = MoodifyInstrumentText,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        stringResource(R.string.home_import_audio),
                        color = MoodifyInstrumentMuted,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
    }
}

@Composable
private fun LoopSequence() {
    Text("AUDITORY LOOP", color = MoodifyInstrumentMuted, style = MaterialTheme.typography.labelLarge)
    Row(
        Modifier.fillMaxWidth().padding(top = 14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        auditoryLoop.forEachIndexed { index, stage ->
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    Modifier.size(if (index == 0) 8.dp else 5.dp)
                        .background(if (index == 0) MoodifyInstrumentSignal else MoodifyInstrumentOutline, CircleShape),
                )
                Text(stage.take(3), color = MoodifyInstrumentMuted, fontSize = 8.sp, letterSpacing = .7.sp, modifier = Modifier.padding(top = 8.dp))
            }
        }
    }
}

@Composable
private fun EvidenceList() {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(stringResource(R.string.home_recent_works), color = MoodifyInstrumentText, style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.weight(1f))
        Text("EVIDENCE", color = MoodifyInstrumentMuted, style = MaterialTheme.typography.labelLarge)
    }
    Spacer(Modifier.height(12.dp))
    Text(
        stringResource(R.string.home_no_recent_works),
        color = MoodifyInstrumentMuted,
        style = MaterialTheme.typography.bodyMedium,
        modifier = Modifier.padding(vertical = 24.dp),
    )
}
