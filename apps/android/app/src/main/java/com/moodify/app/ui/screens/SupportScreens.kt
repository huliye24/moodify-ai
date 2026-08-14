package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.res.stringResource
import android.widget.Toast
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.R
import com.moodify.app.data.LocaleKit
import com.moodify.app.data.LocaleStore
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.theme.*

@Composable
fun AboutScreen(onBack: () -> Unit) = SupportPage("关于 Moodify", onBack, Icons.Outlined.Info) {
    Hero("成全每一种值得被听见的才华", "面向 AI 音乐创作者的作品生产、发布、成长与资产化平台")
    Section("Moodify 是什么") {
        InfoRow(Icons.Outlined.GraphicEq, "处理 AI 音乐", "标准化、优化与商业适配，让作品更专业、更可用。")
        InfoRow(Icons.Outlined.VerifiedUser, "管理作品资产", "归档、确权与收益管理，构建创作者的数字资产。")
        InfoRow(Icons.Outlined.Groups, "连接创作者与机构", "匹配需求、促进合作，让才华获得更多机会。")
    }
    Section("我们的理念") { Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) { Mini(Icons.Outlined.FavoriteBorder,"成全",Modifier.weight(1f)); Mini(Icons.Outlined.PersonOutline,"创作者优先",Modifier.weight(1f)); Mini(Icons.Outlined.MusicNote,"音乐资产化",Modifier.weight(1f)) } }
    Section("核心能力") { InfoRow(Icons.Outlined.GraphicEq,"音乐处理","AI 标准化处理"); InfoRow(Icons.Outlined.Copyright,"版权归档","确权与保护"); InfoRow(Icons.Outlined.Send,"发布分发","多平台分发"); InfoRow(Icons.Outlined.Handshake,"交易合作","合作与收益") }
    Section("联系与支持") { SimpleRow(Icons.Outlined.Language,"官方网站","www.moodify.ai"); SimpleRow(Icons.Outlined.HelpOutline,"帮助与反馈",""); SimpleRow(Icons.Outlined.BusinessCenter,"商务合作","") }
    Text("版权所有 © Moodify Studio", color = MoodifyMuted, fontSize = 11.sp, modifier = Modifier.align(Alignment.CenterHorizontally))
    GradientButton("了解更多", onClick = {})
}

@Composable
fun HelpFeedbackScreen(onBack: () -> Unit) = SupportPage("帮助与反馈", onBack, Icons.Outlined.HeadsetMic) {
    Hero("遇到问题？我们会帮助你", "关于产品、发布、版权与交易，我们全力为你提供支持")
    OutlinedTextField("", {}, Modifier.fillMaxWidth(), placeholder = { Text("搜索问题 / 功能 / 订单") }, leadingIcon = { Icon(Icons.Outlined.Search,null) }, shape = RoundedCornerShape(18.dp))
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Section("1. 常见问题", Modifier.weight(1f)) { listOf("上传失败怎么办","如何发布作品","如何申请原创证明","交易如何托管","如何从微信导入").forEach { SimpleRow(Icons.Outlined.HelpOutline,it,"") } }
        Section("2. 联系我们", Modifier.weight(1f)) { InfoRow(Icons.Outlined.HeadsetMic,"在线客服","7×24 小时在线解答"); InfoRow(Icons.Outlined.Email,"邮件支持","support@moodify.ai"); InfoRow(Icons.Outlined.Handshake,"商务合作","合作与商业洽谈") }
    }
    Section("3. 反馈问题") { Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) { listOf("Bug","功能建议","交易问题","版权问题").forEach { AssistChip(onClick = {}, label = { Text(it, fontSize = 10.sp) }) } }; OutlinedTextField("",{},Modifier.fillMaxWidth().height(110.dp),placeholder={Text("请描述你遇到的问题，越详细越有助于我们解决")}) }
    Section("4. 支持与政策") { SimpleRow(Icons.Outlined.Description,"用户协议",""); SimpleRow(Icons.Outlined.Copyright,"隐私政策",""); SimpleRow(Icons.Outlined.Article,"服务说明","") }
    GradientButton("提交反馈", onClick = {})
}

@Composable
fun SettingsScreen(onBack: () -> Unit, onAbout: () -> Unit) = SupportPage("设置", onBack, Icons.Outlined.Settings) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var showResetDialog by remember { mutableStateOf(false) }
    Section(null) { InfoRow(Icons.Outlined.Person,"泫榛","@moodify_xzhen · Pro") }
    Section("账号与安全") { SimpleRow(Icons.Outlined.PhoneAndroid,"手机号/邮箱","138****8888"); SimpleRow(Icons.Outlined.Lock,"密码与登录",""); SimpleRow(Icons.Outlined.Badge,"实名认证","已认证"); SimpleRow(Icons.Outlined.Devices,"设备管理","3 台设备") }
    var notices by remember { mutableStateOf(listOf(true,true,true,true)) }
    Section("通知设置") { listOf("处理完成通知","交易消息","评论与点赞","系统通知").forEachIndexed { i,t -> ToggleRow(t,notices[i]) { v -> notices = notices.toMutableList().also { it[i]=v } } } }
    Section("隐私与权限") { SimpleRow(Icons.Outlined.PersonOutline,"主页可见性","所有人可见"); SimpleRow(Icons.Outlined.Public,"作品公开设置","公开"); SimpleRow(Icons.Outlined.Download,"下载权限","仅自己"); SimpleRow(Icons.Outlined.Block,"黑名单管理","") }
    Section("偏好设置") { SimpleRow(Icons.Outlined.MusicNote,"默认导出格式","MP3"); ToggleRow("自动生成封面",true){}; ToggleRow("后台处理",true){}; LanguageRow(); ToggleRow("深色模式",false){} }
    Section("存储与数据") { SimpleRow(Icons.Outlined.Cloud,"云端空间","8.24 GB / 50 GB"); SimpleRow(Icons.Outlined.DeleteOutline,"清理缓存","128 MB"); SimpleRow(Icons.Outlined.Sync,"数据同步","刚刚") }
    Section("演示") {
        Card(onClick = { showResetDialog = true }, modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = Color.White)) {
            SimpleRow(Icons.Outlined.Refresh,"重置演示会话","清除激活/作品/配对，回到开场故事")
        }
    }
    Card(onClick=onAbout,modifier=Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=Color.White)){SimpleRow(Icons.Outlined.Info,"关于 Moodify","")}
    if (showResetDialog) {
        AlertDialog(
            onDismissRequest = { showResetDialog = false },
            title = { Text(stringResource(R.string.support_reset_title)) },
            text = { Text(stringResource(R.string.support_reset_text)) },
            confirmButton = {
                TextButton(onClick = {
                    com.moodify.app.data.WorkLibrary(context).clear()
                    com.moodify.app.data.TokenStore(context).clear()
                    com.moodify.app.data.BaseUrlStore(context).baseUrl = com.moodify.app.data.BaseUrlPolicy.DEFAULT
                    showResetDialog = false
                }) { Text(stringResource(R.string.support_reset_confirm), color = Blocking) }
            },
            dismissButton = { TextButton(onClick = { showResetDialog = false }) { Text(stringResource(R.string.common_cancel), color = MoodifyMuted) } },
        )
    }
}

@Composable private fun LanguageRow() {
    var pickerOpen by remember { mutableStateOf(false) }
    val context = androidx.compose.ui.platform.LocalContext.current
    val currentName = LocaleStore.currentTag()?.let { LocaleKit.metaFor(it).nativeName }
        ?: stringResource(R.string.settings_follow_system)
    SimpleRow(Icons.Outlined.Language, stringResource(R.string.settings_language), currentName) { pickerOpen = true }
    if (pickerOpen) {
        val options = listOf(null as String? to stringResource(R.string.settings_follow_system)) +
            LocaleKit.SUPPORTED.map { it.code to it.nativeName }
        val selectedTag = LocaleStore.currentTag()
        AlertDialog(
            onDismissRequest = { pickerOpen = false },
            title = { Text(stringResource(R.string.settings_language)) },
            text = {
                Column {
                    options.forEach { (tag, name) ->
                        Row(
                            Modifier.fillMaxWidth().height(48.dp).clickable {
                                if (tag == null) LocaleStore.resetToSystem() else LocaleStore.set(tag)
                                pickerOpen = false
                                Toast.makeText(
                                    context,
                                    context.getString(R.string.settings_language_changed, name),
                                    Toast.LENGTH_SHORT,
                                ).show()
                            },
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            RadioButton(selected = selectedTag == tag, onClick = null)
                            Text(name, color = MoodifyNavy, fontSize = 14.sp, modifier = Modifier.padding(start = 8.dp))
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { pickerOpen = false }) { Text(stringResource(R.string.common_done), color = MoodifyPurple) } },
        )
    }
}

@Composable private fun SupportPage(title:String,onBack:()->Unit,end:ImageVector,content:@Composable ColumnScope.()->Unit){Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)){Spacer(Modifier.height(10.dp));Row(verticalAlignment=Alignment.CenterVertically){IconButton(onClick=onBack){Icon(Icons.AutoMirrored.Outlined.ArrowBackIos,"返回")};Text(title,Modifier.weight(1f),color=MoodifyNavy,fontSize=21.sp,fontWeight=FontWeight.Bold,textAlign=androidx.compose.ui.text.style.TextAlign.Center);IconButton(onClick={}){Icon(end,null)}};Spacer(Modifier.height(10.dp));content();Spacer(Modifier.height(24.dp))}}
@Composable private fun Hero(title:String,sub:String){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Column(Modifier.fillMaxWidth().padding(24.dp),horizontalAlignment=Alignment.CenterHorizontally){Row(verticalAlignment=Alignment.CenterVertically){MoodifyMark(Modifier.size(62.dp,42.dp));Text("Moodify",fontSize=29.sp,fontWeight=FontWeight.Bold,color=MoodifyNavy)};Text(title,fontSize=18.sp,fontWeight=FontWeight.Bold,color=MoodifyNavy,modifier=Modifier.padding(top=14.dp));Text(sub,fontSize=11.sp,color=MoodifyMuted,modifier=Modifier.padding(top=7.dp))}};Spacer(Modifier.height(12.dp))}
@Composable private fun Section(title:String?,modifier:Modifier=Modifier,content:@Composable ColumnScope.()->Unit){Card(modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White)){Column(Modifier.padding(14.dp)){title?.let{Text(it,color=MoodifyNavy,fontSize=15.sp,fontWeight=FontWeight.Bold,modifier=Modifier.padding(bottom=8.dp))};content()}};Spacer(Modifier.height(12.dp))}
@Composable private fun InfoRow(icon:ImageVector,title:String,sub:String){Row(Modifier.fillMaxWidth().padding(vertical=8.dp),verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(40.dp).background(Color(0xFFF4F2FF),RoundedCornerShape(11.dp)),contentAlignment=Alignment.Center){Icon(icon,null,tint=MoodifyPurple)};Column(Modifier.padding(start=12.dp).weight(1f)){Text(title,color=MoodifyNavy,fontSize=13.sp,fontWeight=FontWeight.SemiBold);Text(sub,color=MoodifyMuted,fontSize=9.sp)}}}
@Composable private fun SimpleRow(icon:ImageVector,title:String,value:String,onClick:(()->Unit)?=null){val row: @Composable ()->Unit={Row(Modifier.fillMaxWidth().height(43.dp),verticalAlignment=Alignment.CenterVertically){Icon(icon,null,tint=MoodifyPurple,modifier=Modifier.size(20.dp));Text(title,Modifier.padding(start=12.dp).weight(1f),color=MoodifyNavy,fontSize=12.sp);Text(value,color=MoodifyMuted,fontSize=10.sp);Icon(Icons.Outlined.ChevronRight,null,tint=MoodifyMuted,modifier=Modifier.size(18.dp))}};if(onClick==null)row()else Surface(onClick=onClick,modifier=Modifier.fillMaxWidth(),color=Color.Transparent,shape=RoundedCornerShape(12.dp)){row()}}
@Composable private fun ToggleRow(title:String,value:Boolean,onChange:(Boolean)->Unit){Row(Modifier.fillMaxWidth().height(43.dp),verticalAlignment=Alignment.CenterVertically){Text(title,Modifier.weight(1f),color=MoodifyNavy,fontSize=12.sp);Switch(value,onChange)}}
@Composable private fun Mini(icon:ImageVector,title:String,modifier:Modifier){Card(modifier,colors=CardDefaults.cardColors(containerColor=Color(0xFFFCFCFF))){Column(Modifier.padding(12.dp),horizontalAlignment=Alignment.CenterHorizontally){Icon(icon,null,tint=MoodifyPurple);Text(title,color=MoodifyNavy,fontSize=10.sp,modifier=Modifier.padding(top=6.dp))}}}
