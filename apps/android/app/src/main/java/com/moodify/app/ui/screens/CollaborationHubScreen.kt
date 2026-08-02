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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.ui.components.GradientButton
import com.moodify.app.ui.theme.*

@Composable
fun CollaborationHubScreen(onExit: () -> Unit) {
    var page by remember { mutableIntStateOf(0) }
    when (page) { 0 -> Marketplace(onExit, { page = 1 }, { page = 2 }); 1 -> PublishCollaboration({ page = 0 }); else -> CollaborationDetail({ page = 0 }) }
}

@Composable private fun Marketplace(onExit: () -> Unit, onPublish: () -> Unit, onDetail: () -> Unit) {
    var type by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
        Spacer(Modifier.height(12.dp)); Top("合作广场", onExit, Icons.Outlined.FilterList); Spacer(Modifier.height(12.dp))
        OutlinedTextField("", {}, Modifier.fillMaxWidth(), placeholder = { Text("搜索合作机会 / 服务 / 创作者 / 机构") }, leadingIcon = { Icon(Icons.Outlined.Search, null) }, shape = RoundedCornerShape(14.dp), singleLine = true)
        Spacer(Modifier.height(12.dp)); Row(Modifier.fillMaxWidth().background(Color.White, RoundedCornerShape(14.dp))) { listOf("全部","B2B","B2C","C2C").forEachIndexed { i,s -> Surface(onClick={type=i},modifier=Modifier.weight(1f),color=if(type==i)MoodifyPurple else Color.Transparent,shape=RoundedCornerShape(13.dp)){Text(s,color=if(type==i)Color.White else MoodifyNavy,textAlign=androidx.compose.ui.text.style.TextAlign.Center,modifier=Modifier.padding(12.dp))} } }
        Row(Modifier.padding(vertical=14.dp),horizontalArrangement=Arrangement.spacedBy(8.dp)){Filter("最新发布");Filter("预算");Filter("地区")}
        MarketCard("寻找 AI 音乐定制合作","Dreamscape Studio","我们是一家内容创作公司，寻找 AI 音乐定制合作伙伴，共同打造高质量背景音乐。","B2B","预算：¥10,000 – ¥50,000","全球",Color(0xFF5431B9),onDetail)
        MarketCard("寻找作词作曲 / 编曲伙伴","Melody_小雨","独立音乐人，寻找长期合作的词曲或编曲伙伴，风格不限，一起创作好作品。","C2C","分成比例：50%","不限地区",Color(0xFFE9DBFF),onDetail)
        MarketCard("AI 音乐封面设计需求","Moodify 官方","为我们的 AI 音乐作品设计系列封面，要求风格统一、视觉高级。","B2C","预算：¥2,000 – ¥5,000","中国大陆",Color(0xFF97B8F6),onDetail)
        MarketCard("电子音乐混音 / 母带处理","NeonWave","需要专业的混音 / 母带处理，让作品达到更好的听感和响度标准。","B2C","预算：¥800 – ¥2,000","不限地区",Color(0xFF151A4A),onDetail)
        Spacer(Modifier.height(10.dp)); Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){GradientMini(Icons.Outlined.Send,"发布需求",Modifier.weight(1f),onPublish);GradientMini(Icons.Outlined.MusicNote,"发布服务",Modifier.weight(1f),onPublish);OutlinedButton(onClick={},modifier=Modifier.weight(1f).height(58.dp),shape=RoundedCornerShape(16.dp)){Column(horizontalAlignment=Alignment.CenterHorizontally){Icon(Icons.Outlined.Person,null);Text("我的合作",fontSize=10.sp)}}};Spacer(Modifier.height(20.dp))
    }
}

@Composable private fun PublishCollaboration(back: () -> Unit) {
    var tab by remember { mutableIntStateOf(0) }; var title by remember { mutableStateOf("") }; var detail by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)){
        Spacer(Modifier.height(12.dp));Row(verticalAlignment=Alignment.CenterVertically){IconButton(onClick=back){Icon(Icons.AutoMirrored.Outlined.ArrowBackIos,"返回")};Text("发布合作",Modifier.weight(1f),color=MoodifyNavy,fontSize=22.sp,fontWeight=FontWeight.Bold,textAlign=androidx.compose.ui.text.style.TextAlign.Center);TextButton(onClick=back){Text("存为草稿",color=MoodifyPurple)}}
        Row(Modifier.fillMaxWidth().background(Color.White,RoundedCornerShape(13.dp))){listOf("发布需求","发布服务","发布项目").forEachIndexed{i,s->Surface(onClick={tab=i},modifier=Modifier.weight(1f),color=if(tab==i)MoodifyPurple else Color.Transparent,shape=RoundedCornerShape(13.dp)){Text(s,color=if(tab==i)Color.White else MoodifyNavy,textAlign=androidx.compose.ui.text.style.TextAlign.Center,modifier=Modifier.padding(12.dp))}}}
        Spacer(Modifier.height(14.dp));FormSection{FormField("* 标题",title,"请输入合作标题，简明扼要"){title=it};ChoiceLine("* 合作类型",listOf("B2B","B2C","C2C"));ChoiceLine("* 身份",listOf("创作者","工作室","品牌方","机构"));ArrowLine("* 预算或分成","例如：预算 ¥5000 / 分成 20%");ArrowLine("* 地区","请选择地区")}
        Spacer(Modifier.height(12.dp));FormSection{Text("* 详细描述",color=MoodifyNavy,fontSize=13.sp,fontWeight=FontWeight.Bold);OutlinedTextField(detail,{if(it.length<=1000)detail=it},Modifier.fillMaxWidth().height(130.dp),placeholder={Text("请详细描述合作内容、目标、期望与要求等信息…",fontSize=11.sp)},supportingText={Text("${detail.length}/1000",Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.End)},shape=RoundedCornerShape(13.dp))}
        Spacer(Modifier.height(12.dp));FormSection{Text("标签",color=MoodifyNavy,fontWeight=FontWeight.Bold);Row(Modifier.padding(top=9.dp),horizontalArrangement=Arrangement.spacedBy(6.dp)){listOf("AI人声","编曲","混音","封面","发行").forEach{Tag(it)}}}
        Spacer(Modifier.height(12.dp));FormSection{Text("附件 / 参考作品",color=MoodifyNavy,fontWeight=FontWeight.Bold);Text("支持音频、图片、文档等，最多上传 5 个文件",color=MoodifyMuted,fontSize=9.sp);OutlinedCard(onClick={},modifier=Modifier.fillMaxWidth().padding(top=10.dp),shape=RoundedCornerShape(13.dp)){Row(Modifier.fillMaxWidth().padding(22.dp),horizontalArrangement=Arrangement.Center){Icon(Icons.Outlined.CloudUpload,null,tint=MoodifyPurple);Text("  点击上传或拖拽文件到此处",color=MoodifyMuted,fontSize=11.sp)}}}
        Spacer(Modifier.height(12.dp));FormSection{Text("合作设置",color=MoodifyNavy,fontWeight=FontWeight.Bold);ArrowLine("是否长期合作","可协商");ArrowLine("是否公开联系方式","公开");ArrowLine("截止时间","请选择截止时间")}
        Spacer(Modifier.height(18.dp));GradientButton("立即发布",back);TextButton(onClick={}){Text("预览合作页  ›",color=MoodifyPurple,modifier=Modifier.fillMaxWidth(),textAlign=androidx.compose.ui.text.style.TextAlign.Center)};Spacer(Modifier.height(20.dp))
    }
}

@Composable private fun CollaborationDetail(back: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal=18.dp)){
        Spacer(Modifier.height(12.dp));Top("合作详情",back,Icons.Outlined.StarBorder);Spacer(Modifier.height(12.dp))
        FormSection{Row{Box(Modifier.size(72.dp).background(Brush.linearGradient(listOf(MoodifyPurple,MoodifyBlue)),RoundedCornerShape(13.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.MusicNote,null,tint=Color.White,modifier=Modifier.size(38.dp))};Column(Modifier.padding(start=14.dp).weight(1f)){Row{Text("寻找 AI 音乐定制合作",color=MoodifyNavy,fontSize=19.sp,fontWeight=FontWeight.Bold);Tag("B2B")};Text("Echo Studio ✦",color=MoodifyNavy,fontSize=12.sp);Text("上海 · 中国",color=MoodifyMuted,fontSize=10.sp)};Surface(color=Color(0xFFE7F8ED),shape=RoundedCornerShape(12.dp)){Text("进行中",color=MoodifyGreen,fontSize=9.sp,modifier=Modifier.padding(8.dp))}};Text("◷ 发布于 2024-05-18 10:30       ◇ 预算 · ¥5,000–20,000",color=MoodifyMuted,fontSize=10.sp,modifier=Modifier.padding(top=15.dp));HorizontalDivider(Modifier.padding(vertical=12.dp),color=MoodifyOutline);Text("我们正在为多个品牌与数字内容项目寻找具备 AI 音乐创作经验的音乐人或团队，需要根据项目需求定制不同风格的背景音乐与主题音乐。",color=MoodifyNavy,fontSize=11.sp,lineHeight=19.sp)}
        Spacer(Modifier.height(12.dp));DetailSection("项目要求"){Req(Icons.Outlined.Tune,"风格方向","电子 / 氛围 / Lo-Fi / 未来感");Req(Icons.Outlined.Schedule,"时长要求","单曲 1–3 分钟，可循环或分段");Req(Icons.Outlined.Description,"交付内容","WAV 高质量文件 / 分轨文件 / 商用授权书");Req(Icons.Outlined.VerifiedUser,"版权及使用","需提供商用授权，允许用于品牌推广与线上发布")}
        Spacer(Modifier.height(12.dp));DetailSection("合作方式"){Row(horizontalArrangement=Arrangement.spacedBy(7.dp)){Tag("♫ 定制制作");Tag("◷ 阶段付款");Tag("♧ 可长期合作");Tag("✓ 支持签约")}}
        Spacer(Modifier.height(12.dp));DetailSection("发布方信息"){Row(verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(58.dp).background(Color(0xFF271B56),CircleShape),contentAlignment=Alignment.Center){Text("ECHO",color=Color.White,fontSize=10.sp,fontWeight=FontWeight.Bold)};Column(Modifier.padding(start=12.dp).weight(1f)){Text("Echo Studio ✦  企业认证",color=MoodifyNavy,fontSize=13.sp,fontWeight=FontWeight.Bold);Text("专注品牌音乐与内容配乐",color=MoodifyMuted,fontSize=10.sp);Text("已发布 18 个合作项目  |  合作成功率 96%",color=MoodifyMuted,fontSize=9.sp)};OutlinedButton(onClick={}){Text("查看主页",fontSize=9.sp)}}}
        Spacer(Modifier.height(12.dp));DetailSection("申请步骤"){Row(horizontalArrangement=Arrangement.SpaceAround){Step("1","查看需求","确认是否符合");Step("2","提交方案","填写方案与报价");Step("3","等待回复","3 个工作日内联系")}}
        Spacer(Modifier.height(12.dp));DetailSection("相关作品 / 参考风格"){Row(horizontalArrangement=Arrangement.spacedBy(10.dp)){Reference("Future Glow","电子 / 氛围",Modifier.weight(1f));Reference("Night Drive","Lo-Fi / Chill",Modifier.weight(1f))}}
        Spacer(Modifier.height(16.dp));Row(horizontalArrangement=Arrangement.spacedBy(10.dp)){OutlinedButton(onClick={},modifier=Modifier.weight(1f).height(52.dp),shape=RoundedCornerShape(16.dp)){Icon(Icons.Outlined.ChatBubbleOutline,null);Text("  联系对方")};Button(onClick={},modifier=Modifier.weight(1f).height(52.dp),shape=RoundedCornerShape(16.dp),colors=ButtonDefaults.buttonColors(containerColor=MoodifyPurple)){Text("立即申请合作")}};Spacer(Modifier.height(22.dp))
    }
}

@Composable private fun MarketCard(title:String,author:String,body:String,type:String,budget:String,region:String,color:Color,click:()->Unit){Card(onClick=click,modifier=Modifier.fillMaxWidth().padding(bottom=12.dp),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White),elevation=CardDefaults.cardElevation(3.dp)){Row(Modifier.padding(14.dp)){Box(Modifier.size(92.dp).background(color,RoundedCornerShape(13.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.GraphicEq,null,tint=Color.White,modifier=Modifier.size(42.dp))};Column(Modifier.padding(start=14.dp).weight(1f)){Row{Text(title,color=MoodifyNavy,fontSize=16.sp,fontWeight=FontWeight.Bold);Tag(type)};Text("$author ✦",color=MoodifyNavy,fontSize=11.sp,modifier=Modifier.padding(top=6.dp));Text(body,color=MoodifyNavy,fontSize=10.sp,lineHeight=16.sp,modifier=Modifier.padding(top=7.dp));Text("$budget     ⌖ $region",color=MoodifyPurple,fontSize=9.sp,modifier=Modifier.padding(top=8.dp))};Icon(Icons.Outlined.BookmarkBorder,null,tint=MoodifyMuted)}}}
@Composable private fun Top(title:String,back:()->Unit,action:ImageVector){Row(verticalAlignment=Alignment.CenterVertically){IconButton(onClick=back){Icon(Icons.AutoMirrored.Outlined.ArrowBackIos,"返回")};Text(title,Modifier.weight(1f),color=MoodifyNavy,fontSize=22.sp,fontWeight=FontWeight.Bold,textAlign=androidx.compose.ui.text.style.TextAlign.Center);IconButton(onClick={}){Icon(action,null)}}}
@Composable private fun Filter(text:String){OutlinedButton(onClick={},shape=RoundedCornerShape(18.dp),contentPadding=PaddingValues(horizontal=13.dp)){Text("$text⌄",fontSize=10.sp)}}
@Composable private fun GradientMini(icon:ImageVector,text:String,modifier:Modifier,click:()->Unit){Button(onClick=click,modifier=modifier.height(58.dp),shape=RoundedCornerShape(16.dp),colors=ButtonDefaults.buttonColors(containerColor=MoodifyPurple)){Column(horizontalAlignment=Alignment.CenterHorizontally){Icon(icon,null);Text(text,fontSize=10.sp)}}}
@Composable private fun FormSection(content:@Composable ColumnScope.()->Unit){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=Color.White),elevation=CardDefaults.cardElevation(3.dp)){Column(Modifier.padding(15.dp),content=content)}}
@Composable private fun FormField(label:String,value:String,hint:String,change:(String)->Unit){Row(verticalAlignment=Alignment.CenterVertically){Text(label,Modifier.width(110.dp),color=MoodifyNavy,fontSize=12.sp,fontWeight=FontWeight.Bold);OutlinedTextField(value,change,Modifier.weight(1f),placeholder={Text(hint,fontSize=10.sp)},singleLine=true)}}
@Composable private fun ChoiceLine(label:String,items:List<String>){Row(Modifier.padding(vertical=8.dp),verticalAlignment=Alignment.CenterVertically){Text(label,Modifier.width(110.dp),color=MoodifyNavy,fontSize=12.sp,fontWeight=FontWeight.Bold);Row(horizontalArrangement=Arrangement.spacedBy(7.dp)){items.forEach{Tag(it)}}}}
@Composable private fun ArrowLine(label:String,value:String){Row(Modifier.fillMaxWidth().padding(vertical=12.dp),verticalAlignment=Alignment.CenterVertically){Text(label,Modifier.width(150.dp),color=MoodifyNavy,fontSize=12.sp,fontWeight=FontWeight.Bold);Text(value,Modifier.weight(1f),color=MoodifyMuted,fontSize=10.sp);Icon(Icons.Outlined.ChevronRight,null,tint=MoodifyMuted)}}
@Composable private fun Tag(text:String){Surface(color=MoodifyLavender,shape=RoundedCornerShape(7.dp),modifier=Modifier.padding(start=6.dp)){Text(text,color=MoodifyPurple,fontSize=9.sp,modifier=Modifier.padding(horizontal=8.dp,vertical=5.dp))}}
@Composable private fun DetailSection(title:String,content:@Composable ColumnScope.()->Unit){FormSection{Text(title,color=MoodifyNavy,fontSize=16.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(9.dp));content()}}
@Composable private fun Req(icon:ImageVector,title:String,value:String){Row(Modifier.padding(vertical=8.dp),verticalAlignment=Alignment.CenterVertically){Icon(icon,null,tint=MoodifyPurple);Text(title,Modifier.padding(start=10.dp).width(86.dp),color=MoodifyNavy,fontSize=11.sp);Text(value,Modifier.weight(1f),color=MoodifyNavy,fontSize=10.sp);Icon(Icons.Outlined.ChevronRight,null,tint=MoodifyMuted)}}
@Composable private fun Step(n:String,title:String,sub:String){Row(verticalAlignment=Alignment.Top){Box(Modifier.size(30.dp).background(MoodifyPurple,CircleShape),contentAlignment=Alignment.Center){Text(n,color=Color.White)};Column(Modifier.padding(start=7.dp)){Text(title,color=MoodifyNavy,fontSize=10.sp,fontWeight=FontWeight.Bold);Text(sub,color=MoodifyMuted,fontSize=8.sp)}}}
@Composable private fun Reference(title:String,style:String,modifier:Modifier){OutlinedCard(onClick={},modifier=modifier,shape=RoundedCornerShape(13.dp)){Row(Modifier.padding(8.dp)){Box(Modifier.size(62.dp).background(Brush.linearGradient(listOf(MoodifyPurple,MoodifyBlue)),RoundedCornerShape(9.dp)),contentAlignment=Alignment.Center){Icon(Icons.Outlined.PlayCircle,null,tint=Color.White)};Column(Modifier.padding(start=9.dp)){Text(title,color=MoodifyNavy,fontSize=11.sp,fontWeight=FontWeight.Bold);Text(style,color=MoodifyMuted,fontSize=9.sp);Tag("氛围")}}}}
