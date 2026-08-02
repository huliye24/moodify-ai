package com.moodify.app.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBackIos
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.*
import kotlinx.coroutines.launch

private val DemoShareCode = "CWC-XZ7M-42KP"
private val ShareLink = "moodify://cwc/$DemoShareCode"

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CwcCenterScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    var shareSheet by remember { mutableStateOf(false) }
    var qrSheet by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    fun copyText(text: String, label: String) {
        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("CWC", text))
        scope.launch { snackbarHostState.showSnackbar("$label 已复制") }
    }

    fun openShareSheet() {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, "Moodify 创作者通行证")
            putExtra(Intent.EXTRA_TEXT, "泫榛 邀请你加入 Moodify。你的创作者通行证：$DemoShareCode\n$ShareLink")
        }
        context.startActivity(Intent.createChooser(intent, "分享创作者通行证"))
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MoodifyBackground,
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回") }
                Text("创作者通行证", Modifier.weight(1f), color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                IconButton(onClick = {}) { Icon(Icons.Outlined.HelpOutline, "说明") }
            }
            Spacer(Modifier.height(14.dp))
            BrandCard()
            Spacer(Modifier.height(14.dp))
            ShareCodeCard()
            Spacer(Modifier.height(14.dp))
            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text("我的可赠送通行证", color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    Row(Modifier.padding(top = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text("3", color = MoodifyPurple, fontSize = 32.sp, fontWeight = FontWeight.Bold)
                        Text(" 张", color = MoodifyMuted, fontSize = 13.sp)
                        Spacer(Modifier.weight(1f))
                        Button(onClick = { shareSheet = true }, colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(18.dp), modifier = Modifier.height(46.dp)) {
                            Icon(Icons.Outlined.CardGiftcard, null, modifier = Modifier.size(18.dp)); Spacer(Modifier.width(6.dp)); Text("赠送一张通行证", color = Color.White)
                        }
                    }
                }
            }
            Spacer(Modifier.height(14.dp))
            InviteRecords()
            Spacer(Modifier.height(12.dp))
            TextButton(onClick = {}) { Text("查看 CWC 规则", color = MoodifyPurple, modifier = Modifier.fillMaxWidth(), textAlign = androidx.compose.ui.text.style.TextAlign.Center) }
            Spacer(Modifier.height(20.dp))
        }
    }

    if (shareSheet) {
        ShareBottomSheet(
            onDismiss = { shareSheet = false },
            onWechat = { shareSheet = false; openShareSheet() },
            onCopyLink = { shareSheet = false; copyText(ShareLink, "通行证链接") },
            onCopyCode = { shareSheet = false; copyText(DemoShareCode, "通行码") },
            onPoster = { shareSheet = false; qrSheet = true },
        )
    }

    if (qrSheet) {
        AlertDialog(
            onDismissRequest = { qrSheet = false },
            shape = RoundedCornerShape(24.dp),
            title = { Text("通行证二维码", color = MoodifyNavy, fontWeight = FontWeight.Bold) },
            text = {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    QrPlaceholder()
                    Spacer(Modifier.height(10.dp))
                    Text(DemoShareCode, color = MoodifyPurple, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text("MVP 占位图，后续接入 ZXing 生成", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 4.dp))
                }
            },
            confirmButton = {
                Button(onClick = { qrSheet = false; copyText(DemoShareCode, "通行码") }, colors = ButtonDefaults.buttonColors(containerColor = MoodifyBlue), shape = RoundedCornerShape(14.dp)) { Text("复制通行码", color = Color.White) }
            },
            dismissButton = {
                TextButton(onClick = { qrSheet = false }) { Text("关闭", color = MoodifyMuted) }
            },
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ShareBottomSheet(onDismiss: () -> Unit, onWechat: () -> Unit, onCopyLink: () -> Unit, onCopyCode: () -> Unit, onPoster: () -> Unit) {
    ModalBottomSheet(onDismissRequest = onDismiss, containerColor = Color.White, shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)) {
        Column(Modifier.padding(horizontal = 20.dp).padding(bottom = 28.dp)) {
            Text("分享创作者通行证", color = MoodifyNavy, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text("你的通行码：$DemoShareCode", color = MoodifyMuted, fontSize = 12.sp)
            Spacer(Modifier.height(18.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                ShareOption(Icons.Outlined.Chat, "微信发送", Modifier.weight(1f), onWechat)
                ShareOption(Icons.Outlined.Link, "复制链接", Modifier.weight(1f), onCopyLink)
                ShareOption(Icons.Outlined.CopyAll, "复制通行码", Modifier.weight(1f), onCopyCode)
                ShareOption(Icons.Outlined.Image, "生成海报", Modifier.weight(1f), onPoster)
            }
        }
    }
}

@Composable
private fun ShareOption(icon: ImageVector, title: String, modifier: Modifier, click: () -> Unit) {
    Card(onClick = click, modifier = modifier, shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color(0xFFF6F7FF))) {
        Column(Modifier.fillMaxWidth().padding(vertical = 14.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Box(Modifier.size(42.dp).background(Brush.linearGradient(listOf(MoodifyPurple, MoodifyBlue)), RoundedCornerShape(12.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = Color.White, modifier = Modifier.size(22.dp)) }
            Text(title, color = MoodifyNavy, fontSize = 11.sp, modifier = Modifier.padding(top = 8.dp))
        }
    }
}

@Composable
private fun BrandCard() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) {
        Row(Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFF312780), Color(0xFF7651D8), Color(0xFFDB8CE9))), RoundedCornerShape(20.dp)).padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.ConfirmationNumber, null, tint = Color.White, modifier = Modifier.size(40.dp))
            Column(Modifier.padding(start = 13.dp).weight(1f)) {
                Text("把一个位置，留给值得被听见的人", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("每一张通行证，都是一次创作者与世界的正式握手", color = Color.White.copy(.8f), fontSize = 11.sp, modifier = Modifier.padding(top = 5.dp))
            }
        }
    }
}

@Composable
private fun ShareCodeCard() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("分享码", color = MoodifyMuted, fontSize = 12.sp)
                Spacer(Modifier.weight(1f))
                Surface(color = Color(0xFFE8F8EE), shape = RoundedCornerShape(9.dp)) { Text("可使用", color = Color(0xFF31A35E), fontSize = 10.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp)) }
            }
            Text(DemoShareCode, color = MoodifyPurple, fontSize = 22.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 10.dp))
            Row(Modifier.padding(top = 8.dp)) {
                InfoChip("赠送者", "泫榛")
                Spacer(Modifier.width(8.dp))
                InfoChip("到期时间", "2027-12-31")
            }
        }
    }
}

@Composable
private fun InfoChip(label: String, value: String) {
    Surface(color = Color(0xFFF6F7FF), shape = RoundedCornerShape(10.dp)) {
        Row(Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(label, color = MoodifyMuted, fontSize = 10.sp)
            Text("  $value", color = MoodifyNavy, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun InviteRecords() {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) {
        Column(Modifier.padding(14.dp)) {
            Row { Text("邀请记录", Modifier.weight(1f), color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.Bold); Text("查看全部  ›", color = MoodifyMuted, fontSize = 11.sp) }
            Spacer(Modifier.height(6.dp))
            RecordRow("CWC-A2B4-88QP", "已发送", Color(0xFFE9F0FF), MoodifyBlue)
            RecordRow("CWC-5F7D-23MN", "已激活", Color(0xFFE8F8EE), Color(0xFF31A35E))
            RecordRow("CWC-9K1L-77XY", "已过期", Color(0xFFF1F3F8), MoodifyMuted)
        }
    }
}

@Composable
private fun RecordRow(code: String, status: String, bg: Color, tint: Color) {
    Row(Modifier.fillMaxWidth().padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(Icons.Outlined.ConfirmationNumber, null, tint = MoodifyPurple, modifier = Modifier.size(20.dp))
        Text(code, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 10.dp).weight(1f))
        Surface(color = bg, shape = RoundedCornerShape(8.dp)) { Text(status, color = tint, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)) }
    }
}

@Composable
private fun QrPlaceholder() {
    Box(Modifier.size(180.dp).background(Color(0xFFF6F7FF), RoundedCornerShape(18.dp)), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Outlined.QrCode2, null, tint = MoodifyPurple, modifier = Modifier.size(56.dp))
            Text("二维码占位", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 6.dp))
        }
    }
}
