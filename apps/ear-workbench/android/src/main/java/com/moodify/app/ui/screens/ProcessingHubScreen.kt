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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FileUpload
import androidx.compose.material.icons.outlined.Menu
import androidx.compose.material.icons.outlined.Verified
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
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

@Composable
fun ProcessingHubScreen(
    onPickAudio: () -> Unit,
    onOpenDrawer: () -> Unit = {},
) {
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
                    "LISTEN",
                    color = MoodifyInstrumentText,
                    fontSize = 12.sp,
                    letterSpacing = 2.1.sp,
                    modifier = Modifier.padding(start = 10.dp),
                )
            }
            Spacer(Modifier.size(48.dp))
        }
        Spacer(Modifier.height(42.dp))
        Text("SOURCE / 01", color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge)
        Text(
            stringResource(R.string.analysis_title),
            color = MoodifyInstrumentText,
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
        Text(
            stringResource(R.string.home_subtitle),
            color = MoodifyInstrumentMuted,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 10.dp),
        )
        Spacer(Modifier.height(34.dp))
        OutlinedCard(
            onClick = onPickAudio,
            modifier = Modifier.fillMaxWidth().height(210.dp),
            shape = RoundedCornerShape(14.dp),
            border = BorderStroke(1.dp, MoodifyInstrumentOutline),
            colors = CardDefaults.outlinedCardColors(containerColor = MoodifyInstrumentSurface),
        ) {
            Column(
                Modifier.fillMaxSize().padding(22.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Box(
                    Modifier.size(54.dp).background(
                        MoodifyInstrumentSignal.copy(alpha = .10f),
                        RoundedCornerShape(10.dp),
                    ),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(Icons.Outlined.FileUpload, null, tint = MoodifyInstrumentSignal, modifier = Modifier.size(27.dp))
                }
                Text(
                    stringResource(R.string.analysis_pick_audio),
                    color = MoodifyInstrumentText,
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 18.dp),
                )
                Text(
                    stringResource(R.string.analysis_pick_audio_support),
                    color = MoodifyInstrumentMuted,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 7.dp),
                )
            }
        }
        Spacer(Modifier.height(24.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.Verified, null, tint = MoodifyInstrumentSignal, modifier = Modifier.size(18.dp))
            Text(
                "One source. One evidence trail. Human authority retained.",
                color = MoodifyInstrumentMuted,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(start = 10.dp),
            )
        }
        Spacer(Modifier.height(40.dp))
    }
}
