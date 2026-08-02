package com.moodify.app.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Box
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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
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
        MainDestination("首页", Icons.Outlined.Home),
        MainDestination("处理", Icons.Outlined.GraphicEq),
        MainDestination("我的", Icons.Outlined.PersonOutline),
    )
    var selected by remember { mutableIntStateOf(0) }
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
    var worksOpen by remember { mutableStateOf(false) }
    var settingsOpen by remember { mutableStateOf(false) }
    var helpOpen by remember { mutableStateOf(false) }
    var aboutOpen by remember { mutableStateOf(false) }
    var startUploadPage by remember { mutableIntStateOf(0) }
    val drawerState = androidx.compose.material3.rememberDrawerState(androidx.compose.material3.DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()

    val backEnabled = processingOpen || detailOpen || publishOpen || searchOpen ||
        creatorCenterOpen || notificationOpen || copyrightCenterOpen || dataCenterOpen ||
        collaborationOpen || uploadOpen || worksOpen || settingsOpen || helpOpen || aboutOpen
    BackHandler(enabled = backEnabled) {
        when {
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
    }

    androidx.compose.material3.ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = !processingOpen && !detailOpen && !publishOpen && !searchOpen && !creatorCenterOpen && !notificationOpen && !copyrightCenterOpen && !dataCenterOpen && !collaborationOpen && !uploadOpen && !worksOpen && !settingsOpen && !helpOpen && !aboutOpen,
        drawerContent = {
            val drawerHighlight = when {
                worksOpen -> 1
                selected == 1 -> 2
                else -> selected
            }
            MoodifyDrawerContent(drawerHighlight) { index ->
                when (index) {
                    0 -> { closeOverlays(); selected = 0 }
                    1 -> { closeOverlays(); worksOpen = true }
                    2 -> { closeOverlays(); selected = 1 }
                    4 -> { closeOverlays(); creatorCenterOpen = true; selected = 2 }
                    5 -> { closeOverlays(); dataCenterOpen = true; selected = 2 }
                    6 -> { closeOverlays(); copyrightCenterOpen = true; selected = 2 }
                    7 -> { closeOverlays(); collaborationOpen = true; selected = 2 }
                    8 -> { closeOverlays(); settingsOpen = true; selected = 2 }
                    9 -> { closeOverlays(); helpOpen = true; selected = 2 }
                    10 -> { closeOverlays(); aboutOpen = true; selected = 2 }
                }
                scope.launch { drawerState.close() }
            }
        },
    ) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
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
        },
    ) { padding ->
        Box(Modifier.padding(padding)) {
            when {
                settingsOpen -> SettingsScreen(onBack = { settingsOpen = false }, onAbout = { settingsOpen = false; aboutOpen = true })
                helpOpen -> HelpFeedbackScreen(onBack = { helpOpen = false })
                aboutOpen -> AboutScreen(onBack = { aboutOpen = false })
                uploadOpen -> UploadFlowScreen(startPage = startUploadPage, onExit = { uploadOpen = false }, onProcess = { uploadOpen = false; processingOpen = true }, onPublish = { uploadOpen = false; publishOpen = true }, onLibrary = { uploadOpen = false; worksOpen = true })
                worksOpen -> WorksScreen(onBack = { worksOpen = false }, onOpenDetail = { worksOpen = false; detailOpen = true })
                collaborationOpen -> CollaborationHubScreen(onExit = { collaborationOpen = false; selected = 2 })
                dataCenterOpen -> DataCenterScreen(onBack = { dataCenterOpen = false; selected = 2 })
                copyrightCenterOpen -> CopyrightCenterScreen(onBack = { copyrightCenterOpen = false; selected = 2 }, onContinuePublish = { copyrightCenterOpen = false; detailOpen = true })
                notificationOpen -> NotificationCenterScreen(onBack = { notificationOpen = false })
                creatorCenterOpen -> CreatorCenterScreen(onBack = { creatorCenterOpen = false; selected = 2 }, onUpload = { creatorCenterOpen = false; uploadOpen = true })
                searchOpen -> SearchScreen(onCancel = { searchOpen = false })
                publishOpen -> PublishWorkScreen(onBack = { publishOpen = false }, onPublished = { publishOpen = false })
                detailOpen -> WorkDetailScreen(onBack = { detailOpen = false }, onProcessAgain = { detailOpen = false; processingOpen = true }, onPublish = { publishOpen = true })
                processingOpen -> ProcessingScreen(onBackHome = { processingOpen = false; worksOpen = true })
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
                else -> ProfileScreen()
            }
        }
    }
    }
}
