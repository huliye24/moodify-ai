package com.moodify.app.ui.screens

import android.net.Uri
import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.AudioFile
import androidx.compose.material.icons.outlined.FileUpload
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.moodify.app.R
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.theme.MoodifyInstrumentField
import com.moodify.app.ui.theme.MoodifyInstrumentMuted
import com.moodify.app.ui.theme.MoodifyInstrumentOutline
import com.moodify.app.ui.theme.MoodifyInstrumentSignal
import com.moodify.app.ui.theme.MoodifyInstrumentSurface
import com.moodify.app.ui.theme.MoodifyInstrumentText

private data class PickedFile(val uri: Uri, val name: String, val sizeLabel: String)

@Composable
fun UploadFlowScreen(
    startPage: Int = 0,
    onExit: () -> Unit,
    onProcess: (List<Uri>) -> Unit,
    onLibrary: () -> Unit,
) {
    val context = LocalContext.current
    var selected by remember { mutableStateOf<List<Uri>>(emptyList()) }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
        selected = uris
    }
    val files = remember(selected) { selected.map { toPickedFile(context, it) } }

    Column(Modifier.fillMaxSize().background(MoodifyInstrumentField).padding(horizontal = 24.dp)) {
        Row(
            Modifier.fillMaxWidth().padding(top = 18.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = onExit) {
                Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, stringResource(R.string.common_back), tint = MoodifyInstrumentMuted)
            }
            Text(
                stringResource(R.string.upload_title),
                color = MoodifyInstrumentText,
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.weight(1f),
            )
            Spacer(Modifier.size(48.dp))
        }
        Spacer(Modifier.height(42.dp))
        Text("LOCAL SOURCE / 01", color = MoodifyInstrumentSignal, style = MaterialTheme.typography.labelLarge)
        Text(
            if (files.isEmpty()) stringResource(R.string.analysis_pick_audio) else stringResource(R.string.upload_selected_count, files.size.toString()),
            color = MoodifyInstrumentText,
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
        Spacer(Modifier.height(28.dp))
        OutlinedCard(
            onClick = { picker.launch(arrayOf("audio/*")) },
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
                    Modifier.size(54.dp).background(MoodifyInstrumentSignal.copy(alpha = .10f), RoundedCornerShape(10.dp)),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        if (files.isEmpty()) Icons.Outlined.FileUpload else Icons.Outlined.AudioFile,
                        null,
                        tint = MoodifyInstrumentSignal,
                        modifier = Modifier.size(27.dp),
                    )
                }
                Text(
                    files.firstOrNull()?.name ?: stringResource(R.string.analysis_pick_audio),
                    color = MoodifyInstrumentText,
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 18.dp),
                )
                Text(
                    files.firstOrNull()?.sizeLabel ?: stringResource(R.string.analysis_pick_audio_support),
                    color = MoodifyInstrumentMuted,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 7.dp),
                )
            }
        }
        if (files.isNotEmpty()) {
            Spacer(Modifier.height(22.dp))
            Text(
                "The source is preserved. Measurement, evidence, and human judgment remain linked to this case.",
                color = MoodifyInstrumentMuted,
                style = MaterialTheme.typography.bodySmall,
            )
            Spacer(Modifier.height(22.dp))
            GradientButton(stringResource(R.string.upload_start), onClick = { onProcess(files.map { it.uri }) })
        }
    }
}

private fun toPickedFile(context: android.content.Context, uri: Uri): PickedFile {
    var name = "audio"
    var size = -1L
    context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
        val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
        val sizeIndex = cursor.getColumnIndex(OpenableColumns.SIZE)
        if (cursor.moveToFirst()) {
            if (nameIndex >= 0) name = cursor.getString(nameIndex) ?: name
            if (sizeIndex >= 0 && !cursor.isNull(sizeIndex)) size = cursor.getLong(sizeIndex)
        }
    }
    val sizeLabel = when {
        size < 0 -> context.getString(R.string.upload_unknown_size)
        size >= 1024 * 1024 -> "%.1f MB".format(size / (1024.0 * 1024.0))
        else -> "%.0f KB".format(size / 1024.0)
    }
    return PickedFile(uri, name, sizeLabel)
}
