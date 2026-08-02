package com.moodify.app.ui.screens

import androidx.compose.foundation.Canvas
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
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.theme.*

@Composable
fun CreatorCenterScreen(onBack: () -> Unit, onUpload: () -> Unit, onOpenCwcCenter: () -> Unit = {}) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(12.dp)); Row(verticalAlignment = Alignment.CenterVertically) { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Outlined.ArrowBackIos, "返回") }; Text("创作者中心", Modifier.weight(1f), color = MoodifyNavy, fontSize = 22.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center); IconButton(onClick = {}) { Icon(Icons.Outlined.Settings, "设置") } }
        Spacer(Modifier.height(12.dp)); Header(); Spacer(Modifier.height(14.dp))
        CwcStatusCard(onOpenCwcCenter); Spacer(Modifier.height(14.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { Action(Icons.Outlined.CloudUpload, "上传作品", "分享你的 AI 音乐", Modifier.weight(1f), onUpload); Action(Icons.Outlined.Inventory2, "草稿箱", "管理未发布作品", Modifier.weight(1f)) {} }
        Spacer(Modifier.height(18.dp)); Title("创作概览"); Spacer(Modifier.height(9.dp)); Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { Overview(Icons.Outlined.Send, "待发布", "3", Modifier.weight(1f)); Overview(Icons.Outlined.GraphicEq, "处理中", "1", Modifier.weight(1f)); Overview(Icons.Outlined.Schedule, "审核中", "2", Modifier.weight(1f)); Overview(Icons.Outlined.VerifiedUser, "版权申请", "6", Modifier.weight(1f)) }
        Spacer(Modifier.height(18.dp)); Title("最近作品"); Spacer(Modifier.height(8.dp)); Works()
        Spacer(Modifier.height(18.dp)); Title("数据趋势"); Spacer(Modifier.height(8.dp)); Trend()
        Spacer(Modifier.height(18.dp)); Title("创作者服务", false); Spacer(Modifier.height(8.dp)); Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) { Service(Icons.Outlined.VerifiedUser, "版权与发布", "申请版权与发布管理", Modifier.weight(1f)); Service(Icons.Outlined.Groups, "合作计划", "与品牌合作变现", Modifier.weight(1f)); Service(Icons.Outlined.BarChart, "数据中心", "深度数据分析", Modifier.weight(1f)) }
        Spacer(Modifier.height(22.dp))
    }
}

@Composable private fun Header() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(4.dp)) { Column(Modifier.padding(18.dp)) { Row(verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(78.dp).background(Brush.linearGradient(listOf(Color(0xFFC8C4FF), Color(0xFFE8D7FF))), CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.Person, null, tint = Color(0xFF2A226B), modifier = Modifier.size(54.dp)) }; Column(Modifier.padding(start = 15.dp)) { Text("泫榛  ✦", color = MoodifyNavy, fontSize = 21.sp, fontWeight = FontWeight.Bold); Surface(color = MoodifyLavender, shape = RoundedCornerShape(7.dp)) { Text("AI音乐创作者", color = MoodifyPurple, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)) }; Text("上传、分享并管理你的 AI 音乐作品  ✎", color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.padding(top = 7.dp)) } }; Spacer(Modifier.height(18.dp)); Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) { Stat("作品", "24"); Div(); Stat("总播放", "128.6万"); Div(); Stat("粉丝", "1.2万"); Div(); Stat("本月新增", "328") } } } }
@Composable private fun Action(icon: ImageVector, title: String, subtitle: String, modifier: Modifier, click: () -> Unit) { Card(onClick = click, modifier = modifier.height(98.dp), shape = RoundedCornerShape(19.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) { Row(Modifier.fillMaxSize().background(Brush.horizontalGradient(listOf(MoodifyBlue, MoodifyPurple)), RoundedCornerShape(19.dp)).padding(14.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(45.dp).background(Color.White, RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) { Icon(icon, null, tint = MoodifyBlue) }; Column(Modifier.padding(start = 10.dp).weight(1f)) { Text(title, color = Color.White, fontSize = 15.sp, fontWeight = FontWeight.Bold); Text(subtitle, color = Color.White.copy(.8f), fontSize = 9.sp) }; Icon(Icons.Outlined.ChevronRight, null, tint = Color.White) } } }
@Composable private fun Overview(icon: ImageVector, label: String, value: String, modifier: Modifier) { Card(modifier, shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Column(Modifier.fillMaxWidth().padding(vertical = 13.dp), horizontalAlignment = Alignment.CenterHorizontally) { Icon(icon, null, tint = MoodifyPurple, modifier = Modifier.size(22.dp)); Text(label, color = MoodifyMuted, fontSize = 9.sp, modifier = Modifier.padding(top = 6.dp)); Text(value, color = MoodifyNavy, fontSize = 17.sp, fontWeight = FontWeight.Bold) } } }
@Composable private fun Works() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(19.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Column(Modifier.padding(horizontal = 12.dp)) { Work("AI Demo Track", "03:24 · 2025-07-30", "已发布", false); HorizontalDivider(color = MoodifyOutline); Work("Dreamscape", "04:18 · 更新于 2025-07-30", "草稿", true); HorizontalDivider(color = MoodifyOutline); Work("Sunset Drive", "03:57 · 更新于 2025-07-29", "处理中", false) } } }
@Composable private fun Work(name: String, date: String, status: String, green: Boolean) { Row(Modifier.fillMaxWidth().padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) { Box(Modifier.size(52.dp).background(Brush.linearGradient(if(green) listOf(Color(0xFF3AB59B), Color(0xFF17495F)) else listOf(Color(0xFF7240D8), Color(0xFF263796))), RoundedCornerShape(9.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.PlayArrow, null, tint = Color.White) }; Column(Modifier.padding(start = 10.dp).weight(1f)) { Row { Text(name, color = MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold); Text("  $status", color = MoodifyPurple, fontSize = 8.sp) }; Text(date, color = MoodifyMuted, fontSize = 9.sp); Text("▷ 12.4万   ♡ 2,341   ▢ 342", color = MoodifyMuted, fontSize = 8.sp) }; OutlinedButton(onClick = {}, contentPadding = PaddingValues(horizontal = 11.dp), shape = RoundedCornerShape(16.dp)) { Text(if(status=="草稿") "编辑" else "查看数据", fontSize = 8.sp) }; Icon(Icons.Outlined.MoreHoriz, null, tint = MoodifyMuted) } }
@Composable private fun Trend() { Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(3.dp)) { Row(Modifier.padding(14.dp)) { Column { Text("近7日播放", color = MoodifyMuted, fontSize = 10.sp); Text("24.8K", color = MoodifyNavy, fontSize = 20.sp, fontWeight = FontWeight.Bold); Text("较上周 ↑ 18.6%", color = MoodifyGreen, fontSize = 9.sp); Text("新增粉丝  128", color = MoodifyNavy, fontSize = 11.sp, modifier = Modifier.padding(top = 12.dp)) }; Chart(Modifier.padding(start = 12.dp).weight(1f).height(88.dp)) } } }
@Composable private fun Chart(modifier: Modifier) { Canvas(modifier) { val vs=listOf(.2f,.55f,.43f,.72f,.37f,.72f,.9f); val p=Path(); vs.forEachIndexed{i,v->val o=Offset(size.width*i/6,size.height*(1-v));if(i==0)p.moveTo(o.x,o.y)else p.lineTo(o.x,o.y);drawCircle(MoodifyPurple,3.dp.toPx(),o)};drawPath(p,MoodifyPurple,style=androidx.compose.ui.graphics.drawscope.Stroke(2.dp.toPx())) } }
@Composable private fun Service(icon: ImageVector, title: String, sub: String, modifier: Modifier) { Card(onClick = {}, modifier = modifier, shape = RoundedCornerShape(14.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) { Column(Modifier.padding(10.dp)) { Icon(icon, null, tint = MoodifyPurple); Text(title, color = MoodifyNavy, fontSize = 10.sp, fontWeight = FontWeight.Bold); Text(sub, color = MoodifyMuted, fontSize = 7.sp) } } }
@Composable private fun Title(text: String, action: Boolean = true) { Row { Text(text, Modifier.weight(1f), color = MoodifyNavy, fontSize = 18.sp, fontWeight = FontWeight.Bold); if(action) Text("查看全部  ›", color = MoodifyMuted, fontSize = 10.sp) } }
@Composable private fun Stat(label: String, value: String) { Column(horizontalAlignment = Alignment.CenterHorizontally) { Text(label, color = MoodifyMuted, fontSize = 9.sp); Text(value, color = MoodifyNavy, fontSize = 16.sp, fontWeight = FontWeight.Bold) } }
@Composable private fun Div() { Box(Modifier.width(1.dp).height(39.dp).background(MoodifyOutline)) }
@Composable private fun CwcStatusCard(onOpen: () -> Unit) { Card(onClick = onOpen, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color.Transparent)) { Row(Modifier.fillMaxWidth().background(Brush.horizontalGradient(listOf(Color(0xFFF0ECFF), Color(0xFFE8F3FF))), RoundedCornerShape(18.dp)).padding(14.dp), verticalAlignment = Alignment.CenterVertically) { Icon(Icons.Outlined.ConfirmationNumber, null, tint = MoodifyPurple, modifier = Modifier.size(26.dp)); Column(Modifier.padding(start = 12.dp).weight(1f)) { Text("创作者通行证", color = MoodifyNavy, fontSize = 14.sp, fontWeight = FontWeight.Bold); Text("CWC-XZ7M-42KP · 可使用 · 可赠送 3 张", color = MoodifyMuted, fontSize = 10.sp, modifier = Modifier.padding(top = 3.dp)) }; Icon(Icons.Outlined.ChevronRight, null, tint = MoodifyMuted) } } }
