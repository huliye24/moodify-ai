package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.connection.ConnectionCard
import com.moodify.app.ui.theme.*

@Composable
fun ProfileScreen(onOpenCwcCenter: () -> Unit = {}) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(20.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) { MoodifyMark(Modifier.size(48.dp, 34.dp)); Spacer(Modifier.width(8.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 27.sp, fontWeight = FontWeight.Bold) }
        Text("智能处理 · 声音更动人", Modifier.fillMaxWidth(), color = MoodifyMuted, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        Spacer(Modifier.height(18.dp)); ProfileHeader(); Spacer(Modifier.height(14.dp)); ConnectionCard(); Spacer(Modifier.height(14.dp)); ProCard(); Spacer(Modifier.height(14.dp)); RecentWorks(); Spacer(Modifier.height(14.dp)); QuickActions(onOpenCwcCenter); Spacer(Modifier.height(14.dp)); SettingsCard(); Spacer(Modifier.height(14.dp))
        Card(onClick = {}, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Text("退出登录", Modifier.fillMaxWidth().padding(15.dp), color = Color(0xFFFF3B45), fontSize = 15.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center) }
        Spacer(Modifier.height(22.dp))
    }
}

@Composable private fun ProfileHeader() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(5.dp)) {
        Column(Modifier.padding(18.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(82.dp).background(Brush.linearGradient(listOf(Color(0xFFC9C5FF), Color(0xFFEBD6FF))), CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color(0xFF29206D), modifier = Modifier.size(58.dp)) }
                Column(Modifier.padding(start = 15.dp).weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) { Text("泫榛", color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.width(9.dp)); Surface(color = MoodifyPurple, shape = RoundedCornerShape(7.dp)) { Text("Pro", color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp)) }; Spacer(Modifier.width(7.dp)); Surface(color = Color(0xFFE8F8EE), shape = RoundedCornerShape(7.dp)) { Text("✓ 认证创作者", color = Color(0xFF329D5D), fontSize = 10.sp, modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp)) } }
                    Text("ID：moodify_xzhen", color = MoodifyMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 5.dp)); Text("用科技让每一份声音，更接近感动。", color = MoodifyMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 7.dp)); Text("⌖ 深圳，中国", color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 5.dp))
                }
                Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted)
            }
            Spacer(Modifier.height(18.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { ProfileStat(Icons.Outlined.LibraryMusic, "作品数", "24"); ProfileDivider(); ProfileStat(Icons.Outlined.GraphicEq, "处理中时长", "12h 36m"); ProfileDivider(); ProfileStat(Icons.Outlined.FileDownload, "导出次数", "128"); ProfileDivider(); ProfileStat(Icons.Outlined.FavoriteBorder, "获得喜欢", "356", Color(0xFFFF4767)) }
        }
    }
}

@Composable private fun ProCard() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) { Row(Modifier.fillMaxWidth().background(Brush.horizontalGradient(listOf(Color(0xFF17274B), Color(0xFF08183D))), RoundedCornerShape(20.dp)).padding(18.dp), verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.EmojiEvents, null, tint = Color(0xFFFFDD66), modifier = Modifier.size(34.dp)); Column(Modifier.padding(start = 13.dp).weight(1f)) { Text("Moodify Pro", color = Color(0xFFFFEE75), fontSize = 18.sp, fontWeight = FontWeight.Bold); Text("有效期至 2026-07-30", color = Color.White.copy(.8f), fontSize = 11.sp) }; Surface(color = Color.White, shape = RoundedCornerShape(22.dp)) { Text("查看权益  ›", color = MoodifyBlue, fontSize = 13.sp, modifier = Modifier.padding(horizontal = 16.dp, vertical = 11.dp)) } } } }

@Composable private fun RecentWorks() { ProfileSection("最近作品", "全部作品  ›") { ProfileWork("AI Demo Track", "03:24 · 处理完成 · 2025-07-30 14:20", false, listOf(Color(0xFF7B2BDB), Color(0xFF263BB4))); HorizontalDivider(color = MoodifyOutline); ProfileWork("Dreamscape", "04:18 · 处理中 68% · 2025-07-30 11:15", true, listOf(Color(0xFF3C48ED), Color(0xFF863CD2))) } }
@Composable private fun ProfileWork(title: String, subtitle: String, processing: Boolean, colors: List<Color>) { Row(Modifier.fillMaxWidth().padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(58.dp).background(Brush.linearGradient(colors), RoundedCornerShape(11.dp)), contentAlignment = Alignment.Center) { Icon(if (processing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, null, tint = Color.White) }; Column(Modifier.padding(start = 12.dp).weight(1f)) { Row(verticalAlignment = Alignment.CenterVertically) { Text(title, color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.SemiBold); Spacer(Modifier.width(8.dp)); Surface(color = if (processing) Color(0xFFE9F0FF) else Color(0xFFE8F8EE), shape = RoundedCornerShape(6.dp)) { Text(if (processing) "处理中" else "已完成", color = if (processing) MoodifyBlue else Color(0xFF31A35E), fontSize = 9.sp, modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)) } }; Text(subtitle, color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 4.dp)); Text(if (processing) "◉ 继续处理     ▣ 查看详情     •••" else "☷ 查看详情     ⇩ 导出     ♧ 分享", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 8.dp)) }; OutlinedIconButton(onClick = {}, modifier = Modifier.size(38.dp), border = androidx.compose.foundation.BorderStroke(1.dp, MoodifyOutline)) { Icon(if (processing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, null, tint = MoodifyBlue) } } }

@Composable private fun QuickActions(onOpenCwcCenter: () -> Unit) { ProfileSection("快捷功能") { Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { QuickItem(Icons.Outlined.ConfirmationNumber, "创作者通行证", "CWC", onOpenCwcCenter); QuickItem(Icons.Outlined.ReceiptLong, "我的订单"); QuickItem(Icons.Outlined.CloudQueue, "云端空间", "3.2 GB / 10 GB"); QuickItem(Icons.Outlined.VerifiedUser, "版权证明"); QuickItem(Icons.Outlined.HeadsetMic, "帮助反馈") } } }
@Composable private fun SettingsCard() { ProfileSection("设置与账户") { SettingsRow(Icons.Outlined.PersonOutline, "个人资料", "编辑头像、昵称、简介"); HorizontalDivider(color = MoodifyOutline); SettingsRow(Icons.Outlined.AdminPanelSettings, "账号与安全", "修改密码、绑定手机、登录设备"); HorizontalDivider(color = MoodifyOutline); SettingsRow(Icons.Outlined.Settings, "通用设置", "通知、语言、主题等") } }

@Composable private fun ProfileSection(title: String, action: String = "", content: @Composable ColumnScope.() -> Unit) { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(21.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) { Column(Modifier.padding(14.dp)) { Row { Text(title, Modifier.weight(1f), color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold); if (action.isNotEmpty()) Text(action, color = MoodifyMuted, fontSize = 11.sp) }; Spacer(Modifier.height(6.dp)); content() } } }
@Composable private fun ProfileStat(icon: ImageVector, label: String, value: String, tint: Color = MoodifyBlue) { Column(horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = tint, modifier = Modifier.size(22.dp)); Text(label, color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp)); Text(value, color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 3.dp)) } }
@Composable private fun ProfileDivider() { Box(Modifier.width(1.dp).height(52.dp).background(MoodifyOutline)) }
@Composable private fun QuickItem(icon: ImageVector, title: String, subtitle: String = "", click: () -> Unit = {}) { Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.clickable(interactionSource = remember { androidx.compose.foundation.interaction.MutableInteractionSource() }, indication = null) { click() }) { Box(Modifier.size(45.dp).background(Color(0xFFF6F7FF), RoundedCornerShape(13.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(25.dp)) }; Text(title, color = MoodifyNavy, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp)); if (subtitle.isNotEmpty()) Text(subtitle, color = MoodifyMuted, fontSize = 8.sp) } }
@Composable private fun SettingsRow(icon: ImageVector, title: String, subtitle: String) { Row(Modifier.fillMaxWidth().padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) { Icon(icon, null, tint = MoodifyBlue, modifier = Modifier.size(20.dp)); Text(title, color = MoodifyNavy, fontSize = 14.sp, modifier = Modifier.padding(start = 12.dp)); Text(subtitle, color = MoodifyMuted, fontSize = 9.sp, modifier = Modifier.padding(start = 12.dp).weight(1f)); Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted, modifier = Modifier.size(18.dp)) } }
