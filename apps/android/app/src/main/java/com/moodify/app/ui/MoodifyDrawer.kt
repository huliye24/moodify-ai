package com.moodify.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.outlined.LibraryMusic
import androidx.compose.material.icons.outlined.PersonOutline
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

internal const val DESTINATION_PLAYER = -1
internal const val DESTINATION_PLAYLISTS = 0
internal const val DESTINATION_FAVOURITES = 1
internal const val DESTINATION_PROFILE = 2

private val DrawerNight = Color(0xFF000106)
private val DrawerText = Color(0xFFF4F2FA)
private val DrawerPurple = Color(0xFF8A42FF)

private data class DrawerItem(val icon: ImageVector, val label: String, val destination: Int)

@Composable
fun MoodifyDrawerContent(selected: Int, onDestination: (Int) -> Unit) {
    ModalDrawerSheet(
        modifier = Modifier.fillMaxWidth(.56f),
        drawerContainerColor = DrawerNight,
        drawerContentColor = DrawerText,
        drawerShape = androidx.compose.foundation.shape.RoundedCornerShape(0.dp),
    ) {
        Column(
            Modifier
                .fillMaxSize()
                .background(
                    Brush.radialGradient(
                        listOf(Color(0x552D0B91), Color.Transparent),
                        center = androidx.compose.ui.geometry.Offset(0f, 560f),
                        radius = 650f,
                    )
                )
                .padding(horizontal = 32.dp)
        ) {
            Spacer(Modifier.height(118.dp))
            listOf(
                DrawerItem(Icons.Outlined.LibraryMusic, "歌单", DESTINATION_PLAYLISTS),
                DrawerItem(Icons.Outlined.FavoriteBorder, "收藏", DESTINATION_FAVOURITES),
                DrawerItem(Icons.Outlined.PersonOutline, "个人主页", DESTINATION_PROFILE),
            ).forEachIndexed { index, item ->
                DrawerRow(item, selected, onDestination)
                if (index < 2) HorizontalDivider(color = Color(0x243E3879), thickness = 1.dp)
            }
            Spacer(Modifier.weight(1f))
        }
    }
}

@Composable
private fun DrawerRow(item: DrawerItem, selected: Int, onDestination: (Int) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .height(78.dp)
            .clickable { onDestination(item.destination) },
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            item.icon,
            contentDescription = item.label,
            tint = if (selected == item.destination) Color(0xFFBC8CFF) else DrawerPurple,
            modifier = Modifier.size(31.dp),
        )
        Text(item.label, color = DrawerText, fontSize = 19.sp, modifier = Modifier.padding(start = 28.dp))
    }
}
