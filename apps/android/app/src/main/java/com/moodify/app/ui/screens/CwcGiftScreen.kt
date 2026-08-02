package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.theme.*

@Composable
fun CwcGiftScreen(
    code: String,
    onBack: () -> Unit,
    onAccept: (String) -> Unit,
) {
    val masked = code.maskCode()
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回") }
            Text("接受创作者通行证", Modifier.weight(1f), color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            Spacer(Modifier.width(48.dp))
        }
        Spacer(Modifier.height(14.dp))
        GiftTicket(masked)
        Spacer(Modifier.height(14.dp))
        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
            Column(Modifier.padding(14.dp)) {
                Text("激活后获得", color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(6.dp))
                GiftBenefit(Icons.Outlined.CloudUpload, "首作免费入驻")
                GiftBenefit(Icons.Outlined.Inventory2, "基础版权建档")
                GiftBenefit(Icons.Outlined.PersonAdd, "创作者主页开启")
                Row(Modifier.padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
                    Surface(color = Color(0xFFFFE0B2), shape = RoundedCornerShape(8.dp)) { Text("标准处理 8 折券", color = Color(0xFFB25E00), fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)) }
                    Spacer(Modifier.width(8.dp))
                    Text("1 张优惠券，不包含免费 DSP 处理", color = MoodifyMuted, fontSize = 10.sp)
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color(0xFFF7F9FF))) {
            Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.ModeComment, null, tint = MoodifyPurple, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(10.dp))
                Text("“欢迎来到 Moodify，用科技让每一份声音更接近感动。”", color = MoodifyNavy, fontSize = 12.sp)
            }
        }
        Spacer(Modifier.height(18.dp))
        GradientButton("接受并开始入驻", onClick = { onAccept(code) })
        TextButton(onClick = {}) { Text("查看通行说明", color = MoodifyPurple, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }
        Spacer(Modifier.height(20.dp))
    }
}

/** CWC-XZ7M-42KP → CWC-XZ7M-•••• — full code is only revealed in the auth page. */
private fun String.maskCode(): String {
    val parts = split("-")
    if (parts.size < 2) return this
    return parts.dropLast(1).joinToString("-") + "-••••"
}

@Composable
private fun GiftTicket(masked: String) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) {
        Column(Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFF312780), Color(0xFF7651D8))), RoundedCornerShape(24.dp)).padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Surface(color = Color.White.copy(.16f), shape = RoundedCornerShape(14.dp)) { Text("泫榛 向你赠送了一张创作者通行证", color = Color.White, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 12.dp, vertical = 7.dp)) }
            Spacer(Modifier.height(16.dp))
            Icon(Icons.Outlined.ConfirmationNumber, null, tint = Color.White, modifier = Modifier.size(44.dp))
            Spacer(Modifier.height(10.dp))
            Text("CWC 创作者通行证", color = Color.White, fontSize = 19.sp, fontWeight = FontWeight.Bold)
            Text("一份进入 Moodify 的创作者礼物与通行凭证", color = Color.White.copy(.8f), fontSize = 11.sp, modifier = Modifier.padding(top = 6.dp))
            Spacer(Modifier.height(18.dp))
            Surface(color = Color.White, shape = RoundedCornerShape(12.dp)) {
                Text(masked, color = MoodifyPurple, fontSize = 14.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 16.dp, vertical = 9.dp))
            }
            Spacer(Modifier.height(10.dp))
            Text("仅展示部分通行码，验证时自动填入完整码", color = Color.White.copy(.65f), fontSize = 10.sp)
        }
    }
}

@Composable
private fun GiftBenefit(icon: androidx.compose.ui.graphics.vector.ImageVector, title: String) {
    Row(Modifier.padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(38.dp).background(Color(0xFFF4F2FF), RoundedCornerShape(11.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(21.dp)) }
        Text(title, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 12.dp))
    }
}
