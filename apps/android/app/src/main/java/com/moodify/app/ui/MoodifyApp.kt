package com.moodify.app.ui

import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.VideoLibrary
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.moodify.app.R
import com.moodify.app.ui.theme.MoodifyInstrumentField
import com.moodify.app.ui.theme.MoodifyInstrumentMuted
import com.moodify.app.ui.theme.MoodifyInstrumentSignal
import com.moodify.app.ui.theme.MoodifyInstrumentSurface
import com.moodify.app.ui.theme.MoodifyInstrumentText
import com.moodify.app.ui.screens.HomeScreen
import com.moodify.app.ui.screens.DataCenterScreen
import com.moodify.app.ui.screens.UploadFlowScreen
import com.moodify.app.ui.screens.ProcessingScreen
import com.moodify.app.ui.screens.ProcessingHubScreen
import com.moodify.app.ui.screens.SettingsScreen
import com.moodify.app.ui.screens.AboutScreen
import com.moodify.app.ui.screens.WorkDetailScreen
import com.moodify.app.ui.screens.WorksScreen
import kotlinx.coroutines.launch

private data class MainDestination(val label: String, val icon: ImageVector)

@Composable
fun MoodifyApp() {
    val destinations = listOf(
        MainDestination(stringResource(R.string.nav_home), Icons.Outlined.Home),
        MainDestination(stringResource(R.string.nav_process), Icons.Outlined.GraphicEq),
        MainDestination(stringResource(R.string.nav_cases), Icons.Outlined.VideoLibrary),
    )
    var selected by rememberSaveable { mutableIntStateOf(0) }
    var processingOpen by remember { mutableStateOf(false) }
    var detailOpen by remember { mutableStateOf(false) }
    var uploadOpen by remember { mutableStateOf(false) }
    var settingsOpen by rememberSaveable { mutableStateOf(false) }
    var aboutOpen by remember { mutableStateOf(false) }
    var startUploadPage by remember { mutableIntStateOf(0) }
    var processingUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    val appContext = androidx.compose.ui.platform.LocalContext.current
    com.moodify.app.data.PlaybackManager.init(appContext)
    val drawerState = androidx.compose.material3.rememberDrawerState(androidx.compose.material3.DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()

    val backEnabled = processingOpen || detailOpen || uploadOpen || settingsOpen || aboutOpen
    BackHandler(enabled = backEnabled) {
        when {
            aboutOpen -> aboutOpen = false
            settingsOpen -> settingsOpen = false
            uploadOpen -> uploadOpen = false
            processingOpen -> processingOpen = false
            detailOpen -> detailOpen = false
        }
    }

    fun closeOverlays() {
        processingOpen = false
        detailOpen = false
        uploadOpen = false
        settingsOpen = false
        aboutOpen = false
    }

    androidx.compose.material3.ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = !processingOpen && !detailOpen && !uploadOpen && !settingsOpen && !aboutOpen,
        drawerContent = {
            val drawerHighlight = when {
                selected == 2 -> 0
                selected == 1 -> 1
                else -> -1
            }
            MoodifyDrawerContent(drawerHighlight) { index ->
                when (index) {
                    0 -> { closeOverlays(); selected = 2 }
                    1 -> { closeOverlays(); selected = 1 }
                    2 -> { /* cloud space: not wired */ }
                    4 -> { closeOverlays(); settingsOpen = true }
                    6 -> { closeOverlays(); aboutOpen = true }
                }
                scope.launch { drawerState.close() }
            }
        },
    ) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            NavigationBar(containerColor = MoodifyInstrumentSurface, tonalElevation = 0.dp) {
                        destinations.forEachIndexed { index, item ->
                            NavigationBarItem(
                                selected = selected == index,
                                onClick = {
                                    closeOverlays()
                                    selected = index
                                },
                                icon = { Icon(item.icon, contentDescription = item.label) },
                                label = { Text(item.label) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = MoodifyInstrumentField,
                                    selectedTextColor = MoodifyInstrumentText,
                                    indicatorColor = MoodifyInstrumentSignal,
                                    unselectedIconColor = MoodifyInstrumentMuted,
                                    unselectedTextColor = MoodifyInstrumentMuted,
                                ),
                            )
                        }
            }
        },
    ) { padding ->
        Box(Modifier.padding(padding)) {
            when {
                settingsOpen -> SettingsScreen(onBack = { settingsOpen = false }, onAbout = { settingsOpen = false; aboutOpen = true })
                aboutOpen -> AboutScreen(onBack = { aboutOpen = false })
                uploadOpen -> UploadFlowScreen(startPage = startUploadPage, onExit = { uploadOpen = false }, onProcess = { uris -> processingUris = uris; uploadOpen = false; processingOpen = true }, onLibrary = { uploadOpen = false; selected = 2 })
                detailOpen -> WorkDetailScreen(work = remember { com.moodify.app.data.WorkLibrary(appContext).all().firstOrNull() }.let { it }, onBack = { detailOpen = false }, onProcessAgain = { detailOpen = false; processingOpen = true })
                processingOpen -> ProcessingScreen(uri = processingUris.firstOrNull(), onBackHome = { processingOpen = false; selected = 2 }, onDone = { processingOpen = false; selected = 2 })
                selected == 0 -> HomeScreen(
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                    onStartAnalysis = { selected = 1 },
                )
                selected == 1 -> ProcessingHubScreen(
                    onPickAudio = { startUploadPage = 0; uploadOpen = true },
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                )
                selected == 2 -> WorksScreen(onBack = null, onOpenDetail = { detailOpen = true })
                else -> HomeScreen(
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                    onStartAnalysis = { selected = 1 },
                )
            }
        }
    }
    }
}
