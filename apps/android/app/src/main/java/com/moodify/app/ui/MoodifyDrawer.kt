package com.moodify.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FactCheck
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.VideoLibrary
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
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

private data class DrawerItem(val icon: ImageVector, val label: String, val destination: Int)

@Composable
fun MoodifyDrawerContent(selected: Int, onDestination: (Int) -> Unit) {
    ModalDrawerSheet(
        modifier = Modifier.fillMaxWidth(.78f),
        drawerContainerColor = MoodifyInstrumentField,
        drawerShape = RoundedCornerShape(topEnd = 16.dp, bottomEnd = 16.dp),
    ) {
        Column(Modifier.fillMaxSize().padding(horizontal = 20.dp)) {
            Column(
                Modifier.fillMaxWidth().padding(top = 42.dp, bottom = 30.dp),
                horizontalAlignment = Alignment.Start,
            ) {
                MoodifyMark(Modifier.size(42.dp, 26.dp))
                Text("MOODIFY", color = MoodifyInstrumentText, fontSize = 13.sp, letterSpacing = 2.4.sp, modifier = Modifier.padding(top = 14.dp))
                Text("THE EAR OF AI", color = MoodifyInstrumentMuted, fontSize = 10.sp, letterSpacing = 1.2.sp, modifier = Modifier.padding(top = 5.dp))
            }
            listOf(
                DrawerItem(Icons.Outlined.FactCheck, stringResource(R.string.nav_process), 1),
                DrawerItem(Icons.Outlined.VideoLibrary, stringResource(R.string.cases_title), 0),
            ).forEach { DrawerRow(it, selected, onDestination) }
            HorizontalDivider(Modifier.padding(vertical = 16.dp), color = MoodifyInstrumentOutline)
            DrawerRow(DrawerItem(Icons.Outlined.Settings, stringResource(R.string.nav_settings), 4), selected, onDestination)
            DrawerRow(DrawerItem(Icons.Outlined.Info, stringResource(R.string.settings_about), 6), selected, onDestination)
            Spacer(Modifier.weight(1f))
            Text("V1 / HUMAN AUTHORITY", color = MoodifyInstrumentMuted, fontSize = 9.sp, letterSpacing = 1.1.sp, modifier = Modifier.padding(bottom = 28.dp))
        }
    }
}

@Composable
private fun DrawerRow(item: DrawerItem, selected: Int, onDestination: (Int) -> Unit) {
    val active = item.destination == selected
    Surface(
        onClick = { onDestination(item.destination) },
        modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
        color = if (active) MoodifyInstrumentSurface else MoodifyInstrumentField,
        shape = RoundedCornerShape(10.dp),
    ) {
        androidx.compose.foundation.layout.Row(
            Modifier.height(52.dp).padding(horizontal = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(item.icon, null, tint = if (active) MoodifyInstrumentSignal else MoodifyInstrumentMuted, modifier = Modifier.size(21.dp))
            Text(item.label, color = if (active) MoodifyInstrumentText else MoodifyInstrumentMuted, fontSize = 14.sp, modifier = Modifier.padding(start = 16.dp))
        }
    }
}
