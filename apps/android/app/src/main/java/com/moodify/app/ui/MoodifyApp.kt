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
import com.moodify.app.ui.screens.CreatorCenterScreen
import com.moodify.app.ui.screens.NotificationCenterScreen
import com.moodify.app.ui.screens.CopyrightCenterScreen
import com.moodify.app.ui.screens.DataCenterScreen
import com.moodify.app.ui.screens.CollaborationHubScreen
import com.moodify.app.ui.screens.UploadFlowScreen
import com.moodify.app.ui.screens.ProfileScreen
import com.moodify.app.ui.screens.ProcessingScreen
import com.moodify.app.ui.screens.ProcessingHubScreen
import com.moodify.app.ui.screens.PublishWorkScreen
import com.moodify.app.data.CwcRepository
import com.moodify.app.model.AuthMode
import com.moodify.app.ui.components.MiniPlayer
import com.moodify.app.ui.components.MiniPlayerVisibility
import com.moodify.app.ui.screens.SearchScreen
import com.moodify.app.ui.screens.SettingsScreen
import com.moodify.app.ui.screens.HelpFeedbackScreen
import com.moodify.app.ui.screens.AboutScreen
import com.moodify.app.ui.screens.CwcIntroScreen
import com.moodify.app.ui.screens.CwcAuthScreen
import com.moodify.app.ui.screens.CwcGiftScreen
import com.moodify.app.ui.screens.CwcCenterScreen
import com.moodify.app.ui.screens.WorkDetailScreen
import com.moodify.app.ui.screens.WorksScreen
import kotlinx.coroutines.launch

private data class MainDestination(val label: String, val icon: ImageVector)

data class CwcAuthRequest(val mode: AuthMode, val prefilledCode: String? = null)

@Composable
fun MoodifyApp(pendingCwcCode: String? = null) {
    val destinations = listOf(
        MainDestination(stringResource(R.string.nav_home), Icons.Outlined.Home),
        MainDestination(stringResource(R.string.nav_process), Icons.Outlined.GraphicEq),
        MainDestination(stringResource(R.string.nav_profile), Icons.Outlined.PersonOutline),
    )
    var selected by rememberSaveable { mutableIntStateOf(0) }
    var processingOpen by remember { mutableStateOf(false) }
    var detailOpen by remember { mutableStateOf(false) }
    var publishOpen by remember { mutableStateOf(false) }
    var searchOpen by remember { mutableStateOf(false) }
    var creatorCenterOpen by remember { mutableStateOf(false) }
    var notificationOpen by remember { mutableStateOf(false) }
    var copyrightCenterOpen by remember { mutableStateOf(false) }
    var dataCenterOpen by remember { mutableStateOf(false) }
    var collaborationOpen by remember { mutableStateOf(false) }
    var uploadOpen by remember { mutableStateOf(false) }
    var worksOpen by rememberSaveable { mutableStateOf(false) }
    var settingsOpen by rememberSaveable { mutableStateOf(false) }
    var helpOpen by remember { mutableStateOf(false) }
    var aboutOpen by remember { mutableStateOf(false) }
    var startUploadPage by remember { mutableIntStateOf(0) }
    var processingUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var cwcIntroOpen by remember { mutableStateOf(false) }
    var cwcGiftOpen by remember { mutableStateOf(false) }
    var cwcCenterOpen by remember { mutableStateOf(false) }
    var cwcAuthRequest by remember { mutableStateOf<CwcAuthRequest?>(null) }
    var nowPlayingOpen by remember { mutableStateOf(false) }
    var miniPlayerVisibility by rememberSaveable { mutableStateOf(MiniPlayerVisibility.VISIBLE) }
    var startupChecked by remember { mutableStateOf(false) }
    val appContext = androidx.compose.ui.platform.LocalContext.current
    com.moodify.app.data.PlaybackManager.init(appContext)
    val cwcRepo = remember(appContext) { CwcRepository(appContext) }
    val giftCode = remember { pendingCwcCode ?: "CWC-XZ7M-42KP" }
    val drawerState = androidx.compose.material3.rememberDrawerState(androidx.compose.material3.DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()

    androidx.compose.runtime.LaunchedEffect(Unit) {
        when {
            pendingCwcCode != null -> cwcGiftOpen = true
            !cwcRepo.isActivated() -> cwcAuthRequest = CwcAuthRequest(AuthMode.Onboarding, null)
        }
        startupChecked = true
    }

    val backEnabled = nowPlayingOpen || processingOpen || detailOpen || publishOpen || searchOpen ||
        creatorCenterOpen || notificationOpen || copyrightCenterOpen || dataCenterOpen ||
        collaborationOpen || uploadOpen || worksOpen || settingsOpen || helpOpen || aboutOpen ||
        cwcIntroOpen || cwcGiftOpen || cwcCenterOpen || cwcAuthRequest != null
    BackHandler(enabled = backEnabled) {
        when {
            nowPlayingOpen -> nowPlayingOpen = false
            cwcAuthRequest != null -> cwcAuthRequest = null
            cwcGiftOpen -> cwcGiftOpen = false
            cwcIntroOpen -> cwcIntroOpen = false
            cwcCenterOpen -> cwcCenterOpen = false
            aboutOpen -> aboutOpen = false
            helpOpen -> helpOpen = false
            settingsOpen -> settingsOpen = false
            worksOpen -> worksOpen = false
            uploadOpen -> uploadOpen = false
            processingOpen -> processingOpen = false
            detailOpen -> detailOpen = false
            publishOpen -> publishOpen = false
            searchOpen -> searchOpen = false
            creatorCenterOpen -> creatorCenterOpen = false
            notificationOpen -> notificationOpen = false
            copyrightCenterOpen -> copyrightCenterOpen = false
            dataCenterOpen -> dataCenterOpen = false
            collaborationOpen -> collaborationOpen = false
        }
    }

    fun closeOverlays() {
        processingOpen = false
        detailOpen = false
        publishOpen = false
        searchOpen = false
        creatorCenterOpen = false
        notificationOpen = false
        copyrightCenterOpen = false
        dataCenterOpen = false
        collaborationOpen = false
        uploadOpen = false
        worksOpen = false
        settingsOpen = false
        helpOpen = false
        aboutOpen = false
        cwcIntroOpen = false
        cwcGiftOpen = false
        cwcCenterOpen = false
        cwcAuthRequest = null
    }

    androidx.compose.material3.ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = !processingOpen && !detailOpen && !publishOpen && !searchOpen && !creatorCenterOpen && !notificationOpen && !copyrightCenterOpen && !dataCenterOpen && !collaborationOpen && !uploadOpen && !worksOpen && !settingsOpen && !helpOpen && !aboutOpen && !cwcIntroOpen && !cwcGiftOpen && !cwcCenterOpen && cwcAuthRequest == null,
        drawerContent = {
            val drawerHighlight = when {
                worksOpen -> 0
                selected == 1 -> 1
                else -> -1
            }
            MoodifyDrawerContent(drawerHighlight) { index ->
                when (index) {
                    0 -> { closeOverlays(); worksOpen = true }
                    1 -> { closeOverlays(); selected = 1 }
                    2 -> { closeOverlays(); creatorCenterOpen = true; selected = 2 }
                    3 -> { closeOverlays(); dataCenterOpen = true; selected = 2 }
                    4 -> { closeOverlays(); copyrightCenterOpen = true; selected = 2 }
                    5 -> { closeOverlays(); collaborationOpen = true; selected = 2 }
                    6 -> { closeOverlays(); settingsOpen = true; selected = 2 }
                    7 -> { closeOverlays(); helpOpen = true; selected = 2 }
                    8 -> { closeOverlays(); aboutOpen = true; selected = 2 }
                }
                scope.launch { drawerState.close() }
            }
        },
    ) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            // CWC full-screen pages must not be covered by the 3-tab bar.
            if (cwcAuthRequest == null && !cwcGiftOpen && !cwcIntroOpen && !cwcCenterOpen && !nowPlayingOpen) {
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
                cwcAuthRequest != null -> CwcAuthScreen(
                    mode = cwcAuthRequest!!.mode,
                    prefilledCode = cwcAuthRequest!!.prefilledCode,
                    onBack = { cwcAuthRequest = null },
                    onShowIntro = { cwcIntroOpen = true },
                    onActivated = { cwcAuthRequest = null; selected = 1 },
                    onLoggedIn = { cwcAuthRequest = null; selected = 0 },
                )
                cwcGiftOpen -> CwcGiftScreen(code = giftCode, onBack = { cwcGiftOpen = false }, onAccept = { code -> cwcGiftOpen = false; cwcAuthRequest = CwcAuthRequest(AuthMode.Onboarding, code) })
                cwcIntroOpen -> CwcIntroScreen(onBack = { cwcIntroOpen = false }, onStart = { cwcIntroOpen = false; cwcAuthRequest = CwcAuthRequest(AuthMode.Onboarding, null) })
                cwcCenterOpen -> CwcCenterScreen(onBack = { cwcCenterOpen = false })
                !startupChecked -> { }
                settingsOpen -> SettingsScreen(onBack = { settingsOpen = false }, onAbout = { settingsOpen = false; aboutOpen = true })
                helpOpen -> HelpFeedbackScreen(onBack = { helpOpen = false })
                aboutOpen -> AboutScreen(onBack = { aboutOpen = false })
                uploadOpen -> UploadFlowScreen(startPage = startUploadPage, onExit = { uploadOpen = false }, onProcess = { uris -> processingUris = uris; uploadOpen = false; processingOpen = true }, onLibrary = { uploadOpen = false; worksOpen = true })
                worksOpen -> WorksScreen(onBack = { worksOpen = false }, onOpenDetail = { worksOpen = false; detailOpen = true })
                collaborationOpen -> CollaborationHubScreen(onExit = { collaborationOpen = false; selected = 2 })
                dataCenterOpen -> DataCenterScreen(onBack = { dataCenterOpen = false; selected = 2 })
                copyrightCenterOpen -> CopyrightCenterScreen(onBack = { copyrightCenterOpen = false; selected = 2 }, onContinuePublish = { copyrightCenterOpen = false; detailOpen = true })
                notificationOpen -> NotificationCenterScreen(onBack = { notificationOpen = false })
                creatorCenterOpen -> CreatorCenterScreen(onBack = { creatorCenterOpen = false; selected = 2 }, onUpload = { creatorCenterOpen = false; uploadOpen = true }, onOpenCwcCenter = { cwcCenterOpen = true })
                searchOpen -> SearchScreen(onCancel = { searchOpen = false })
                publishOpen -> PublishWorkScreen(onBack = { publishOpen = false }, onPublished = { publishOpen = false })
                detailOpen -> WorkDetailScreen(work = remember { com.moodify.app.data.WorkLibrary(appContext).all().firstOrNull() }.let { it }, onBack = { detailOpen = false }, onProcessAgain = { detailOpen = false; processingOpen = true }, onPublish = { publishOpen = true })
                processingOpen -> ProcessingScreen(uri = processingUris.firstOrNull(), onBackHome = { processingOpen = false; worksOpen = true }, onDone = { processingOpen = false; worksOpen = true })
                selected == 0 -> HomeScreen(onOpenDrawer = { scope.launch { drawerState.open() } }, onOpenSearch = { searchOpen = true }, onOpenNotifications = { notificationOpen = true })
                selected == 1 -> ProcessingHubScreen(
                    onPickAudio = { startUploadPage = 0; uploadOpen = true },
                    onWechatImport = { startUploadPage = 1; uploadOpen = true },
                    onCloudImport = { startUploadPage = 0; uploadOpen = true },
                    onStandardProcess = { startUploadPage = 0; uploadOpen = true },
                    onFreeSave = { worksOpen = true },
                    onOpenRecentTask = { processingOpen = true },
                    onOpenDrawer = { scope.launch { drawerState.open() } },
                )
                else -> ProfileScreen(onOpenCwcCenter = { cwcCenterOpen = true })
            }
        }
    }
    }
}
