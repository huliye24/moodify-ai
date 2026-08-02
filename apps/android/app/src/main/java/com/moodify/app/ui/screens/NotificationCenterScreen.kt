package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.*

private data class Notice(val icon: ImageVector, val title: String, val body: String, val detail: String = "", val time: String, val category: Int, val tint: Color, val read: Boolean = false)

@Composable
fun NotificationCenterScreen(onBack: () -> Unit) {
    var tab by remember { mutableIntStateOf(0) }; var allRead by remember { mutableStateOf(false) }
    val notices = listOf(
        Notice(Icons.Outlined.GraphicEq, "处理完成", "AI Demo Track 处理已完成，可立即试听与导出", time = "刚刚", category = 3, tint = MoodifyPurple),
        Notice(Icons.Outlined.Person, "新增粉丝", "Aurora 关注了你", "快去看看她的主页", "12 分钟前", 1, Color(0xFFB979D8)),
        Notice(Icons.Outlined.FavoriteBorder, "收到点赞", "你的作品 Dreamscape 获得了 128 个赞", time = "36 分钟前", category = 1, tint = Color(0xFFFF4D7A)),
        Notice(Icons.Outlined.ChatBubbleOutline, "收到评论", "Echo 评论了你的作品 Sunset Drive", "“氛围感很棒，封面也很好看”", "1 小时前", 1, MoodifyNavy),
        Notice(Icons.Outlined.StarBorder, "平台推荐", "作品 Midnight Walk 已被加入今日推荐", time = "今天", category = 2, tint = MoodifyPurple, read = true),
        Notice(Icons.Outlined.VerifiedUser, "版权通知", "原创证明申请审核通过", time = "昨天", category = 2, tint = Color(0xFF27BFAE), read = true),
        Notice(Icons.Outlined.Handshake, "合作邀请", "你收到一条新的合作计划邀请", time = "昨天", category = 2, tint = MoodifyBlue, read = true),
    )
    val visible = if (tab == 0) notices else notices.filter { it.category == tab }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(14.dp)); Row(verticalAlignment = Alignment.CenterVertically) { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回", tint = MoodifyNavy) }; Text("通知中心", Modifier.weight(1f), color = MoodifyNavy, fontSize = 22.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center); TextButton(onClick = { allRead = true }) { Text("全部已读", color = MoodifyBlue, fontSize = 14.sp) } }
        Spacer(Modifier.height(16.dp)); Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Row(Modifier.fillMaxWidth().padding(9.dp)) { listOf("全部", "互动", "系统", "处理").forEachIndexed { i, label -> Surface(onClick = { tab = i }, modifier = Modifier.weight(1f), color = if (tab == i) Color(0xFFF0EDFF) else Color.Transparent, shape = RoundedCornerShape(14.dp)) { Text(label, color = if (tab == i) MoodifyBlue else MoodifyMuted, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center, modifier = Modifier.padding(vertical = 12.dp)) } } } }
        Spacer(Modifier.height(18.dp)); visible.forEach { NotificationCard(it, allRead || it.read); Spacer(Modifier.height(12.dp)) }
        if (visible.isEmpty()) Column(Modifier.fillMaxWidth().padding(top = 80.dp), horizontalAlignment = Alignment.CenterHorizontally) { Icon(Icons.Outlined.NotificationsNone, null, tint = MoodifyOutline, modifier = Modifier.size(52.dp)); Text("暂无通知", color = MoodifyMuted, modifier = Modifier.padding(top = 12.dp)) }
        Spacer(Modifier.height(18.dp))
    }
}

@Composable private fun NotificationCard(notice: Notice, read: Boolean) { Card(onClick = {}, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) { Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(58.dp).background(notice.tint.copy(.09f), RoundedCornerShape(16.dp)), contentAlignment = Alignment.Center) { Icon(notice.icon, null, tint = notice.tint, modifier = Modifier.size(30.dp)) }; Column(Modifier.padding(start = 14.dp).weight(1f)) { Text(notice.title, color = MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold); Text(notice.body, color = MoodifyMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 5.dp)); if (notice.detail.isNotEmpty()) Text(notice.detail, color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp)) }; Column(horizontalAlignment = Alignment.End) { Text(notice.time, color = MoodifyMuted, fontSize = 10.sp); Spacer(Modifier.height(20.dp)); Box(Modifier.size(9.dp).background(if (read) Color(0xFFD4D8E3) else MoodifyPurple, CircleShape)) } } } }
