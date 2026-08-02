package com.moodify.app.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AccountCircle
import androidx.compose.material.icons.outlined.GraphicEq
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.MusicNote
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
import com.moodify.app.ui.screens.PublishWorkScreen
import com.moodify.app.ui.screens.SearchScreen
import com.moodify.app.ui.screens.WorkDetailScreen
import com.moodify.app.ui.screens.WorksScreen
import kotlinx.coroutines.launch

private data class MainDestination(val label: String, val icon: ImageVector)

@Composable
fun MoodifyApp() {
    val destinations = listOf(
        MainDestination("首页", Icons.Outlined.Home),
        MainDestination("处理", Icons.Outlined.GraphicEq),
        MainDestination("作品", Icons.Outlined.MusicNote),
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
    val drawerState = androidx.compose.material3.rememberDrawerState(androidx.compose.material3.DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()

    androidx.compose.material3.ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = !processingOpen && !detailOpen && !publishOpen && !searchOpen && !creatorCenterOpen && !notificationOpen && !copyrightCenterOpen && !dataCenterOpen && !collaborationOpen && !uploadOpen,
        drawerContent = {
            MoodifyDrawerContent(selected) { index ->
                creatorCenterOpen = index == 4
                copyrightCenterOpen = index == 5
                dataCenterOpen = index == 6
                collaborationOpen = index == 7
                selected = if (index >= 4) 3 else index
                processingOpen = index == 1
                detailOpen = false
                publishOpen = false
                searchOpen = false
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
                            selected = index
                            processingOpen = index == 1
                            detailOpen = false
                            publishOpen = false
                            searchOpen = false
                            creatorCenterOpen = false
                            notificationOpen = false
                            copyrightCenterOpen = false
                            dataCenterOpen = false
                            collaborationOpen = false
                            uploadOpen = false
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
                uploadOpen -> UploadFlowScreen(onExit = { uploadOpen = false }, onProcess = { uploadOpen = false; processingOpen = true; selected = 1 }, onPublish = { uploadOpen = false; detailOpen = true; selected = 2 }, onLibrary = { uploadOpen = false; selected = 2 })
                collaborationOpen -> CollaborationHubScreen(onExit = { collaborationOpen = false; selected = 3 })
                dataCenterOpen -> DataCenterScreen(onBack = { dataCenterOpen = false; selected = 3 })
                copyrightCenterOpen -> CopyrightCenterScreen(onBack = { copyrightCenterOpen = false; selected = 3 }, onContinuePublish = { copyrightCenterOpen = false; detailOpen = true; selected = 2 })
                notificationOpen -> NotificationCenterScreen(onBack = { notificationOpen = false })
                creatorCenterOpen -> CreatorCenterScreen(onBack = { creatorCenterOpen = false; selected = 3 }, onUpload = { creatorCenterOpen = false; uploadOpen = true })
                searchOpen -> SearchScreen(onCancel = { searchOpen = false })
                publishOpen -> PublishWorkScreen(onBack = { publishOpen = false }, onPublished = { publishOpen = false })
                detailOpen -> WorkDetailScreen(onBack = { detailOpen = false }, onProcessAgain = {
                    detailOpen = false
                    processingOpen = true
                    selected = 1
                }, onPublish = { publishOpen = true })
                processingOpen -> ProcessingScreen(onBackHome = {
                    processingOpen = false
                    detailOpen = true
                    selected = 2
                })
                selected == 0 -> HomeScreen(onStartProcessing = {
                    uploadOpen = true
                }, onOpenDrawer = { scope.launch { drawerState.open() } }, onOpenSearch = { searchOpen = true }, onOpenNotifications = { notificationOpen = true })
                selected == 2 -> WorksScreen(onOpenDetail = { detailOpen = true })
                else -> ProfileScreen()
            }
        }
    }
    }
}
