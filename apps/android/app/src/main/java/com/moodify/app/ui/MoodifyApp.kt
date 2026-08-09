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
import androidx.compose.material.icons.outlined.PersonOutline
import androidx.compose.material.icons.outlined.VideoLibrary
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
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
import com.moodify.app.ui.screens.HomeScreen
import com.moodify.app.ui.screens.DataCenterScreen
import com.moodify.app.ui.screens.UploadFlowScreen
import com.moodify.app.ui.screens.ProfileScreen
import com.moodify.app.ui.screens.ProcessingScreen
import com.moodify.app.ui.screens.ProcessingHubScreen
import com.moodify.app.ui.components.MiniPlayer
import com.moodify.app.ui.components.MiniPlayerVisibility
import com.moodify.app.ui.screens.SearchScreen
import com.moodify.app.ui.screens.SettingsScreen
import com.moodify.app.ui.screens.HelpFeedbackScreen
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
        MainDestination(stringResource(R.string.nav_profile), Icons.Outlined.PersonOutline),
    )
    var selected by rememberSaveable { mutableIntStateOf(0) }
    var processingOpen by remember { mutableStateOf(false) }
    var detailOpen by remember { mutableStateOf(false) }
    var searchOpen by remember { mutableStateOf(false) }
    var dataCenterOpen by remember { mutableStateOf(false) }
    var uploadOpen by remember { mutableStateOf(false) }
    var settingsOpen by rememberSaveable { mutableStateOf(false) }
    var helpOpen by remember { mutableStateOf(false) }
    var aboutOpen by remember { mutableStateOf(false) }
    var startUploadPage by remember { mutableIntStateOf(0) }
    var processingUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var nowPlayingOpen by remember { mutableStateOf(false) }
    var miniPlayerVisibility by rememberSaveable { mutableStateOf(MiniPlayerVisibility.VISIBLE) }
    val appContext = androidx.compose.ui.platform.LocalContext.current
    com.moodify.app.data.PlaybackManager.init(appContext)
    val drawerState = androidx.compose.material3.rememberDrawerState(androidx.compose.material3.DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()

    val backEnabled = nowPlayingOpen || processingOpen || detailOpen || searchOpen ||
        dataCenterOpen ||
        uploadOpen || settingsOpen || helpOpen || aboutOpen
    BackHandler(enabled = backEnabled) {
        when {
            nowPlayingOpen -> nowPlayingOpen = false
            aboutOpen -> aboutOpen = false
            helpOpen -> helpOpen = false
            settingsOpen -> settingsOpen = false
            uploadOpen -> uploadOpen = false
            processingOpen -> processingOpen = false
            detailOpen -> detailOpen = false
            searchOpen -> searchOpen = false
            dataCenterOpen -> dataCenterOpen = false
        }
    }

    fun closeOverlays() {
        processingOpen = false
        detailOpen = false
        searchOpen = false
        dataCenterOpen = false
        uploadOpen = false
        settingsOpen = false
        helpOpen = false
        aboutOpen = false
    }

    androidx.compose.material3.ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = !processingOpen && !detailOpen && !searchOpen && !dataCenterOpen && !uploadOpen && !settingsOpen && !helpOpen && !aboutOpen,
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
                    3 -> { closeOverlays(); dataCenterOpen = true }
                    4 -> { closeOverlays(); settingsOpen = true }
                    5 -> { closeOverlays(); helpOpen = true }
                    6 -> { closeOverlays(); aboutOpen = true }
                }
                scope.launch { drawerState.close() }
            }
        },
    ) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            if (!nowPlayingOpen) {
                Column {
                    MiniPlayer(
                        visibility = miniPlayerVisibility,
                        onVisibilityChange = { miniPlayerVisibility = it },
                        onOpen = { nowPlayingOpen = true },
                    )
                    NavigationBar(tonalElevation = 0.dp) {
                        destinations.forEachIndexed { index, item ->
                            NavigationBarItem(
                                selected = selected == index,
                                onClick = {
                                    closeOverlays()
                                    selected = index
                                },
                                icon = { Icon(item.icon, contentDescription = item.label) },
                                label = { Text(item.label) },
                            )
                        }
                    }
                }
            }
        },
    ) { padding ->
        Box(Modifier.padding(padding)) {
            when {
                nowPlayingOpen -> com.moodify.app.ui.screens.NowPlayingScreen(onClose = { nowPlayingOpen = false })
                settingsOpen -> SettingsScreen(onBack = { settingsOpen = false }, onAbout = { settingsOpen = false; aboutOpen = true })
                helpOpen -> HelpFeedbackScreen(onBack = { helpOpen = false })
                aboutOpen -> AboutScreen(onBack = { aboutOpen = false })
                uploadOpen -> UploadFlowScreen(startPage = startUploadPage, onExit = { uploadOpen = false }, onProcess = { uris -> processingUris = uris; uploadOpen = false; processingOpen = true }, onLibrary = { uploadOpen = false; selected = 2 })
                dataCenterOpen -> DataCenterScreen(onBack = { dataCenterOpen = false })
                searchOpen -> SearchScreen(onCancel = { searchOpen = false })
                detailOpen -> WorkDetailScreen(work = remember { com.moodify.app.data.WorkLibrary(appContext).all().firstOrNull() }.let { it }, onBack = { detailOpen = false }, onProcessAgain = { detailOpen = false; processingOpen = true })
                processingOpen -> ProcessingScreen(uri = processingUris.firstOrNull(), onBackHome = { processingOpen = false; selected = 2 }, onDone = { processingOpen = false; selected = 2 })
                selected == 0 -> HomeScreen(onOpenDrawer = { scope.launch { drawerState.open() } }, onOpenSearch = { searchOpen = true })
                selected == 1 -> ProcessingHubScreen(
                    onPickAudio = { startUploadPage = 0; uploadOpen = true },
                    onWechatImport = { startUploadPage = 1; uploadOpen = true },
                    onCloudImport = { startUploadPage = 0; uploadOpen = true },
                    onStandardProcess = { startUploadPage = 0; uploadOpen = true },
                    onFreeSave = { selected = 2 },
                    onOpenRecentTask = { processingOpen = true },
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                )
                selected == 2 -> WorksScreen(onBack = null, onOpenDetail = { detailOpen = true })
                else -> ProfileScreen()
            }
        }
    }
    }
}
