package com.moodify.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.*

private data class DrawerItem(val icon: ImageVector, val label: String, val destination: Int? = null, val badge: String? = null)

@Composable
fun MoodifyDrawerContent(selected: Int, onDestination: (Int) -> Unit) {
    ModalDrawerSheet(modifier = Modifier.fillMaxWidth(.82f), drawerContainerColor = Color(0xFFFCFCFF), drawerShape = RoundedCornerShape(topEnd = 28.dp, bottomEnd = 28.dp)) {
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
            Spacer(Modifier.height(26.dp)); ProfileCard(); Spacer(Modifier.height(22.dp))
            listOf(
                DrawerItem(Icons.Outlined.MusicNote, "发现音乐", 0), DrawerItem(Icons.Outlined.VideoLibrary, "我的作品", 1), DrawerItem(Icons.Outlined.FactCheck, "处理任务", 2, "1"), DrawerItem(Icons.Outlined.CloudQueue, "云端空间")
            ).forEach { DrawerRow(it, selected, onDestination) }
            HorizontalDivider(Modifier.padding(vertical = 12.dp), color = MoodifyOutline)
            listOf(
                DrawerItem(Icons.Outlined.PersonOutline, "创作者中心", 4, "•"), DrawerItem(Icons.Outlined.BarChart, "数据中心", 5), DrawerItem(Icons.Outlined.VerifiedUser, "版权与发布", 6, "•"), DrawerItem(Icons.Outlined.Handshake, "合作计划", 7)
            ).forEach { DrawerRow(it, selected, onDestination) }
            HorizontalDivider(Modifier.padding(vertical = 12.dp), color = MoodifyOutline)
            listOf(DrawerItem(Icons.Outlined.Settings, "设置", 8), DrawerItem(Icons.Outlined.HeadsetMic, "帮助与反馈", 9), DrawerItem(Icons.Outlined.Info, "关于 Moodify", 10)).forEach { DrawerRow(it, selected, onDestination) }
            Spacer(Modifier.height(16.dp)); StorageCard(); Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable private fun ProfileCard() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) { Row(Modifier.background(Brush.linearGradient(listOf(Color(0xFFE8F1FF), Color(0xFFE9DEFF), Color(0xFFE1F8FF))), RoundedCornerShape(22.dp)).padding(18.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(70.dp).background(Color(0xFFC9C5FF), CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color(0xFF252069), modifier = Modifier.size(48.dp)) }; Column(Modifier.padding(start = 14.dp).weight(1f)) { Row(verticalAlignment = Alignment.CenterVertically) { Text("泫榛", color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.width(9.dp)); Surface(color = MoodifyPurple, shape = RoundedCornerShape(7.dp)) { Text("Pro", color = Color.White, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)) } }; Text("@moodify_xzhen", color = MoodifyMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 5.dp)); Text("24 作品 · 356 获赞", color = MoodifyNavy, fontSize = 12.sp, modifier = Modifier.padding(top = 9.dp)) }; Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted) } } }

@Composable private fun DrawerRow(item: DrawerItem, selected: Int, onDestination: (Int) -> Unit) { val active = item.destination == selected; Surface(onClick = { item.destination?.let(onDestination) }, modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp), color = if (active) Color(0xFFF0EDFF) else Color.Transparent, shape = RoundedCornerShape(16.dp)) { Row(Modifier.height(56.dp), verticalAlignment = Alignment.CenterVertically) { if (active) Box(Modifier.width(5.dp).fillMaxHeight(.72f).background(MoodifyPurple, RoundedCornerShape(4.dp))) else Spacer(Modifier.width(5.dp)); Icon(item.icon, null, tint = if (active) MoodifyPurple else MoodifyMuted, modifier = Modifier.padding(start = 18.dp).size(25.dp)); Text(item.label, Modifier.padding(start = 18.dp).weight(1f), color = if (active) MoodifyPurple else MoodifyNavy, fontSize = 17.sp, fontWeight = if (active) FontWeight.SemiBold else FontWeight.Normal); item.badge?.let { if (it == "•") Text("●", color = Color(0xFFFF4D5E), fontSize = 10.sp) else Surface(color = Color(0xFFF0EDFF), shape = CircleShape) { Text(it, color = MoodifyPurple, modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp)) } }; Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted, modifier = Modifier.padding(horizontal = 12.dp).size(20.dp)) } } }

@Composable private fun StorageCard() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Column(Modifier.padding(14.dp)) { Text("已使用 3.2 / 10 GB", color = MoodifyMuted, fontSize = 12.sp); Spacer(Modifier.height(10.dp)); LinearProgressIndicator(progress = { .32f }, modifier = Modifier.fillMaxWidth().height(7.dp), color = MoodifyPurple, trackColor = MoodifyOutline) } } }
