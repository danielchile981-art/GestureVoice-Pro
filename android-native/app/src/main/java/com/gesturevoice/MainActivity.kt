package com.gesturevoice

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.gesturevoice.data.*
import com.gesturevoice.engine.Point
import com.gesturevoice.service.GestureAccessibility
import com.gesturevoice.service.ListeningService
import com.gesturevoice.ui.theme.*
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint class MainActivity : ComponentActivity() {
    @Inject lateinit var repository: GestureRepository
    @Inject lateinit var preferences: Preferences
    private val audioPermission = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted -> if (granted) startListening() else toast("O microfone é necessário para ouvir gatilhos") }
    private val notificationPermission = registerForActivityResult(ActivityResultContracts.RequestPermission()) { }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { val theme by preferences.mode.collectAsState(initial = "dark"); GestureTheme(theme) { App() } }
    }
    private fun toast(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    private fun startListening() {
        if (Build.VERSION.SDK_INT < 31 || !android.speech.SpeechRecognizer.isOnDeviceRecognitionAvailable(this)) {
            toast("Reconhecimento local requer Android 12+ e modelo de voz instalado"); return
        }
        if (GestureAccessibility.current == null) { toast("Ative GestureVoice em Acessibilidade antes de ouvir"); return }
        if (Build.VERSION.SDK_INT >= 33) notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        ContextCompat.startForegroundService(this, Intent(this, ListeningService::class.java))
        toast("Escuta local iniciada")
    }
    private fun requestListen() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == android.content.pm.PackageManager.PERMISSION_GRANTED) startListening()
        else audioPermission.launch(Manifest.permission.RECORD_AUDIO)
    }
    @Composable private fun App() {
        val gestures by repository.gestures.collectAsState(initial = emptyList())
        val triggers by repository.triggers.collectAsState(initial = emptyList())
        val history by repository.history.collectAsState(initial = emptyList())
        val accepted by preferences.accepted.collectAsState(initial = false)
        val currentMode by preferences.mode.collectAsState(initial = "dark")
        var page by remember { mutableStateOf("Home") }
        var selected by remember { mutableStateOf<String?>(null) }
        var showConsent by remember { mutableStateOf(false) }
        if (!accepted || showConsent) {
            AlertDialog(onDismissRequest = { if (accepted) showConsent = false }, title = { Text("Controle de gestos e privacidade") },
                text = { Text("GestureVoice usa o microfone durante a escuta ativa e o serviço de Acessibilidade para reproduzir os gestos que você salvou na tela de outros apps. O áudio é processado pelo reconhecedor local do dispositivo e não é armazenado pelo GestureVoice. Você pode desligar a escuta pela notificação. Ative Acessibilidade manualmente nas configurações; ela poderá observar eventos da interface enquanto estiver ligada.") },
                confirmButton = { TextButton(onClick = { lifecycleScope.launch { preferences.setConsent(true) }; showConsent = false }) { Text("Entendi e continuar") } },
                dismissButton = { if (accepted) TextButton(onClick = { showConsent = false }) { Text("Cancelar") } })
        }
        Scaffold(containerColor = MaterialTheme.colorScheme.background, topBar = {
            Row(Modifier.fillMaxWidth().padding(start = 22.dp, end = 16.dp, top = 18.dp, bottom = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Gesture, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(30.dp))
                Spacer(Modifier.width(10.dp)); Text("GESTUREVOICE", fontSize = 18.sp, fontWeight = FontWeight.Black, modifier = Modifier.weight(1f))
                IconButton(onClick = { page = "Configurações" }) { Icon(Icons.Default.Settings, "Configurações") }
            }
        }, bottomBar = {
            NavigationBar(containerColor = MaterialTheme.colorScheme.surface) {
                listOf(Triple("Home", Icons.Default.Home, "Início"), Triple("Biblioteca", Icons.Default.GridView, "Gestos"), Triple("Gatilhos", Icons.Default.Mic, "Gatilhos"), Triple("Estatísticas", Icons.Default.BarChart, "Dados")).forEach { (destination, icon, label) ->
                    NavigationBarItem(selected = page == destination, onClick = { page = destination }, icon = { Icon(icon, label) }, label = { Text(label) })
                }
            }
        }) { padding ->
            Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 16.dp)) {
                AnimatedContent(targetState = page, label = "navigation") { current -> when (current) {
                    "Home" -> Home(gestures.size, triggers.size, { page = "Criar" }, { page = "Biblioteca" }, { page = "Gatilhos" }, { showConsent = true }, { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }, { requestListen() }, { stopService(Intent(this@MainActivity, ListeningService::class.java)); toast("Escuta encerrada") })
                    "Criar" -> CreateGesture(onSave = { name, points, color, width -> lifecycleScope.launch { selected = repository.create(name, points, color.value.toLong(), width); toast("Gesto salvo"); page = "Gatilhos" } }, onBack = { page = "Home" })
                    "Biblioteca" -> Library(gestures, { selected = it; page = "Gatilhos" }, { lifecycleScope.launch { repository.remove(it) } })
                    "Gatilhos" -> Triggers(gestures, triggers, selected, { id, phrase -> lifecycleScope.launch { repository.bind(id, phrase); toast("Gatilho salvo") } }, { id -> lifecycleScope.launch { repository.dao.removeTrigger(id) } })
                    "Estatísticas" -> Stats(gestures, history)
                    "Configurações" -> SettingsScreen(currentMode, { lifecycleScope.launch { preferences.setTheme(it) } }, { page = "Home" }, { showConsent = true })
                } }
            }
        }
    }
}

@Composable private fun Heading(title: String, caption: String) {
    Text(title, fontSize = 30.sp, fontWeight = FontWeight.Bold, lineHeight = 35.sp)
    Spacer(Modifier.height(6.dp)); Text(caption, color = Muted, fontSize = 14.sp)
    Spacer(Modifier.height(24.dp))
}
@Composable private fun Tile(title: String, body: String, icon: androidx.compose.ui.graphics.vector.ImageVector, action: () -> Unit) {
    Card(onClick = action, modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp), shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(28.dp)); Spacer(Modifier.width(16.dp))
            Column { Text(title, fontWeight = FontWeight.Bold, fontSize = 18.sp); Spacer(Modifier.height(3.dp)); Text(body, color = Muted, fontSize = 13.sp) }
        }
    }
}
@Composable private fun Home(count: Int, triggerCount: Int, create: () -> Unit, library: () -> Unit, triggers: () -> Unit, disclosure: () -> Unit, accessibility: () -> Unit, listen: () -> Unit, stop: () -> Unit) {
    Heading("Seu controle, sua voz.", "Seus gestos. Sua voz. Seu controle.")
    Card(colors = CardDefaults.cardColors(containerColor = Violet), shape = RoundedCornerShape(24.dp), modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(24.dp)) { Icon(Icons.Default.AutoAwesome, null, modifier = Modifier.size(32.dp)); Spacer(Modifier.height(16.dp)); Text("Transforme uma palavra em um gesto", fontSize = 23.sp, fontWeight = FontWeight.Bold); Text("$count gestos · $triggerCount gatilhos", color = Color.White.copy(alpha = .8f)); Spacer(Modifier.height(18.dp)); Button(onClick = create) { Text("+ Criar gesto") } }
    }
    Spacer(Modifier.height(24.dp)); Tile("Biblioteca", "Veja, selecione e apague gestos", Icons.Default.GridView, library)
    Tile("Gatilhos de voz", "Associe palavras aos gestos", Icons.Default.Mic, triggers)
    Tile("Permissões e privacidade", "Entenda o acesso necessário", Icons.Default.Security, disclosure)
    OutlinedButton(onClick = accessibility, modifier = Modifier.fillMaxWidth()) { Text("Ativar serviço de Acessibilidade") }
    Spacer(Modifier.height(10.dp)); Button(onClick = listen, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.PlayArrow, null); Spacer(Modifier.width(8.dp)); Text("ATIVAR ESCUTA") }
    TextButton(onClick = stop, modifier = Modifier.fillMaxWidth()) { Text("Parar escuta") }
    Text("A escuta local exige Android 12+ e modelo de fala instalado. O serviço inicia somente por sua ação.", fontSize = 12.sp, color = Muted)
}
@Composable private fun CreateGesture(onSave: (String, List<Point>, Color, Float) -> Unit, onBack: () -> Unit) {
    var name by remember { mutableStateOf("") }; val points = remember { mutableStateListOf<Point>() }
    var width by remember { mutableFloatStateOf(8f) }; var color by remember { mutableStateOf(Cyan) }
    var start by remember { mutableLongStateOf(0L) }
    Heading("Desenhe seu gesto", "Cada ponto será reproduzido na mesma posição relativa da tela.")
    OutlinedTextField(name, { name = it }, label = { Text("Nome do gesto") }, singleLine = true, modifier = Modifier.fillMaxWidth())
    Spacer(Modifier.height(16.dp))
    Box(Modifier.fillMaxWidth().height(400.dp).background(MaterialTheme.colorScheme.surface, RoundedCornerShape(20.dp)).border(1.dp, Cyan.copy(alpha = .25f), RoundedCornerShape(20.dp))) {
        Canvas(Modifier.fillMaxSize().pointerInput(Unit) {
            detectDragGestures(onDragStart = { pos -> points.clear(); start = android.os.SystemClock.elapsedRealtime(); points += Point((pos.x / size.width).coerceIn(0f,1f), (pos.y / size.height).coerceIn(0f,1f), 0) }, onDrag = { change, _ ->
                points += Point((change.position.x / size.width).coerceIn(0f,1f), (change.position.y / size.height).coerceIn(0f,1f), android.os.SystemClock.elapsedRealtime() - start); change.consume()
            })
        }) {
            val step = size.width / 10
            for (i in 1..9) drawLine(Cyan.copy(alpha = .07f), Offset(i * step, 0f), Offset(i * step, size.height), 1f)
            if (points.size > 1) {
                val path = Path().apply { moveTo(points.first().x * size.width, points.first().y * size.height); points.drop(1).forEach { lineTo(it.x * size.width, it.y * size.height) } }
                drawPath(path, color.copy(alpha = .18f), style = Stroke(width = width * 3, cap = StrokeCap.Round))
                drawPath(path, color, style = Stroke(width = width, cap = StrokeCap.Round))
            }
        }
        if (points.isEmpty()) Text("Desenhe aqui", color = Muted, modifier = Modifier.align(Alignment.Center))
    }
    Spacer(Modifier.height(15.dp)); Text("Cor do traço")
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { listOf(Cyan, Violet, Pink, Color(0xFF00FFA3)).forEach { choice -> Box(Modifier.padding(vertical = 8.dp).size(34.dp).background(choice, RoundedCornerShape(50)).clickable { color = choice }.then(if (color == choice) Modifier.border(2.dp, Color.White, RoundedCornerShape(50)) else Modifier)) } }
    Text("Espessura: ${width.toInt()} px"); Slider(value = width, onValueChange = { width = it }, valueRange = 2f..20f)
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { OutlinedButton(onClick = { points.clear() }) { Text("Limpar") }; Button(enabled = name.isNotBlank() && points.size >= 2, onClick = { onSave(name, points.toList(), color, width) }) { Text("Salvar gesto") }; TextButton(onClick = onBack) { Text("Voltar") } }
}
@Composable private fun Library(gestures: List<GestureEntity>, select: (String) -> Unit, delete: (String) -> Unit) {
    Heading("Biblioteca", "${gestures.size} gestos salvos")
    if (gestures.isEmpty()) { Text("Sua biblioteca está vazia. Crie um gesto para começar.", color = Muted); return }
    gestures.forEach { g -> Tile(g.name, "Toque para vincular um gatilho", Icons.Default.Gesture, { select(g.id) }); TextButton(onClick = { delete(g.id) }) { Text("Excluir ${g.name}", color = MaterialTheme.colorScheme.error) } }
}
@Composable private fun Triggers(gestures: List<GestureEntity>, triggers: List<TriggerEntity>, selected: String?, bind: (String, String) -> Unit, remove: (String) -> Unit) {
    var id by remember(selected) { mutableStateOf(selected ?: gestures.firstOrNull()?.id) }
    var phrase by remember { mutableStateOf("") }
    Heading("Gatilhos de voz", "Fale a palavra exata para acionar o gesto escolhido.")
    if (gestures.isEmpty()) { Text("Crie um gesto antes de vincular uma palavra.", color = Muted); return }
    gestures.forEach { g -> Row(verticalAlignment = Alignment.CenterVertically) { RadioButton(selected = id == g.id, onClick = { id = g.id }); Text(g.name) } }
    OutlinedTextField(phrase, { phrase = it }, label = { Text("Palavra ou frase, por exemplo: abrir menu") }, singleLine = true, modifier = Modifier.fillMaxWidth())
    Spacer(Modifier.height(12.dp)); Button(onClick = { id?.let { bind(it, phrase); phrase = "" } }, enabled = phrase.isNotBlank()) { Text("Vincular gatilho") }
    Spacer(Modifier.height(20.dp)); Text("Gatilhos salvos", fontWeight = FontWeight.Bold)
    triggers.forEach { t -> Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) { Text("“${t.phrase}” → ${gestures.firstOrNull { it.id == t.gestureId }?.name ?: "Removido"}", modifier = Modifier.weight(1f)); IconButton(onClick = { remove(t.id) }) { Icon(Icons.Default.Delete, "Excluir gatilho") } } }
}
@Composable private fun Stats(gestures: List<GestureEntity>, history: List<HistoryEntity>) {
    Heading("Estatísticas", "Atividade registrada somente neste aparelho")
    Tile("Total de execuções", "${history.size}", Icons.Default.Bolt, {})
    Tile("Gestos criados", "${gestures.size}", Icons.Default.Gesture, {})
    val top = history.groupingBy { it.gestureId }.eachCount().toList().sortedByDescending { it.second }.take(3)
    Text("Mais usados", fontWeight = FontWeight.Bold)
    top.forEach { (id, count) -> Text("${gestures.firstOrNull { it.id == id }?.name ?: "Gesto removido"}: $count", modifier = Modifier.padding(vertical = 8.dp)) }
    if (top.isEmpty()) Text("Os dados aparecem depois da primeira execução.", color = Muted)
}
@Composable private fun SettingsScreen(mode: String, setMode: (String) -> Unit, back: () -> Unit, disclosure: () -> Unit) {
    Heading("Configurações", "Controle a aparência e revise a privacidade")
    Text("Tema", fontWeight = FontWeight.Bold)
    listOf("dark" to "Escuro", "light" to "Claro", "auto" to "Automático").forEach { (value, label) -> Row(verticalAlignment = Alignment.CenterVertically) { RadioButton(mode == value, onClick = { setMode(value) }); Text(label) } }
    Spacer(Modifier.height(15.dp)); Tile("Privacidade e permissões", "Leia o aviso de uso", Icons.Default.Security, disclosure)
    Text("Os gestos são criptografados com chave do Android Keystore. O histórico fica neste dispositivo. Não há conta nem envio pelo app.", color = Muted, fontSize = 13.sp)
    TextButton(onClick = back) { Text("Voltar") }
}
