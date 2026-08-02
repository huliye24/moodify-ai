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
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun CwcIntroScreen(onBack: () -> Unit, onStart: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回") }
            Text("什么是 CWC", Modifier.weight(1f), color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            Surface(color = MoodifyLavender, shape = RoundedCornerShape(10.dp)) { Text("CWC", color = MoodifyPurple, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)) }
        }
        Spacer(Modifier.height(14.dp))
        HeroCard()
        Spacer(Modifier.height(14.dp))
        GroupCard("你可以把它理解为") {
            BenefitLine(Icons.Outlined.CardGiftcard, "一份礼物", "由创作者、品牌或机构赠送")
            BenefitLine(Icons.Outlined.ConfirmationNumber, "一张通行证", "进入 Moodify 的唯一邀请凭证")
            BenefitLine(Icons.Outlined.WorkspacePremium, "一份权益包", "入驻即获得创作者基础权益")
        }
        Spacer(Modifier.height(12.dp))
        GroupCard("激活后获得") {
            BenefitLine(Icons.Outlined.CloudUpload, "首个作品免费入驻", "免费入驻与建档服务")
            BenefitLine(Icons.Outlined.Inventory2, "基础作品建档", "作品库与版权档案")
            BenefitLine(Icons.Outlined.PersonAdd, "创作者主页开启", "创建你的公开主页")
            BenefitLine(Icons.Outlined.LocalOffer, "标准处理 8 折券", "1 张标准处理优惠券")
        }
        Spacer(Modifier.height(12.dp))
        GroupCard("使用步骤") {
            StepLine(1, "收到 CWC", "来自创作者、品牌或机构的赠送")
            StepLine(2, "验证激活", "输入通行码并创建账户")
            StepLine(3, "导入作品", "进入处理中心开始创作")
            StepLine(4, "开始成长", "建档、发布与合作")
        }
        Spacer(Modifier.height(18.dp))
        GradientButton("开始使用 CWC", onStart)
        TextButton(onClick = {}) { Text("查看 CWC 规则", color = MoodifyPurple, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun HeroCard() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) {
        Row(Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFFF6F3FF), Color(0xFFEAF2FF))), RoundedCornerShape(22.dp)).padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) { MoodifyMark(Modifier.size(40.dp, 28.dp)); Text("Moodify", color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold) }
                Text("CWC 创作者通行证", color = MoodifyNavy, fontSize = 19.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 10.dp))
                Text("一份进入 Moodify 的创作者礼物与通行凭证", color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 6.dp))
            }
            Box(Modifier.size(86.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(22.dp)), contentAlignment = Alignment.Center) {
                Icon(Icons.Outlined.ConfirmationNumber, null, tint = Color.White, modifier = Modifier.size(44.dp))
            }
        }
    }
}

@Composable
private fun GroupCard(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
        Column(Modifier.padding(14.dp)) {
            Text(title, color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            content()
        }
    }
}

@Composable
private fun BenefitLine(icon: androidx.compose.ui.graphics.vector.ImageVector, title: String, sub: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(38.dp).background(Color(0xFFF4F2FF), RoundedCornerShape(11.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(21.dp)) }
        Text(title, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 12.dp))
        Spacer(Modifier.weight(1f))
        Text(sub, color = MoodifyMuted, fontSize = 10.sp)
    }
}

@Composable
private fun StepLine(step: Int, title: String, sub: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(34.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) { Text("$step", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
        Text(title, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 12.dp))
        Spacer(Modifier.weight(1f))
        Text(sub, color = MoodifyMuted, fontSize = 10.sp)
    }
}
