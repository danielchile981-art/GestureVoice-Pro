package com.gesturevoice.service

import android.Manifest
import android.app.*
import android.content.*
import android.content.pm.PackageManager
import android.os.*
import android.speech.*
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.gesturevoice.R
import com.gesturevoice.data.GestureRepository
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import javax.inject.Inject

/** Somente modelo local do sistema: se indisponível, a escuta não é iniciada. */
@AndroidEntryPoint class ListeningService : Service(), RecognitionListener {
    @Inject lateinit var repository: GestureRepository
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val handler = Handler(Looper.getMainLooper())
    private var recognizer: SpeechRecognizer? = null
    private var running = false
    private var lastFire = 0L
    private val channel = "gesturevoice_listening"
    override fun onBind(intent: Intent?): IBinder? = null
    override fun onCreate() {
        super.onCreate()
        (getSystemService(NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(
            NotificationChannel(channel, getString(R.string.notification_channel), NotificationManager.IMPORTANCE_LOW))
    }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == "STOP") { stopSelf(); return START_NOT_STICKY }
        if (running) return START_NOT_STICKY
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED ||
            Build.VERSION.SDK_INT < 31 || !SpeechRecognizer.isOnDeviceRecognitionAvailable(this)) {
            stopSelf(); return START_NOT_STICKY
        }
        val stop = PendingIntent.getService(this, 1, Intent(this, ListeningService::class.java).setAction("STOP"), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        val notification = NotificationCompat.Builder(this, channel).setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("GestureVoice · ouvindo no dispositivo")
            .setContentText("Toque em Parar para desligar o microfone")
            .setOngoing(true).addAction(0, "Parar", stop).build()
        if (Build.VERSION.SDK_INT >= 29) startForeground(71, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        else startForeground(71, notification)
        running = true
        recognizer = SpeechRecognizer.createOnDeviceSpeechRecognizer(this).also { it.setRecognitionListener(this) }
        listen()
        return START_NOT_STICKY
    }
    private fun listen() {
        if (!running) return
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "pt-BR")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
        }
        try { recognizer?.startListening(intent) } catch (_: RuntimeException) { handler.postDelayed({ listen() }, 1000) }
    }
    override fun onResults(results: Bundle?) {
        val phrases = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION).orEmpty()
        val now = SystemClock.elapsedRealtime()
        if (now - lastFire >= 1500) scope.launch {
            val target = phrases.firstNotNullOfOrNull { repository.find(it) }
            if (target != null && GestureAccessibility.current != null) {
                lastFire = SystemClock.elapsedRealtime()
                GestureAccessibility.current?.play(repository.points(target)) { ok ->
                    if (ok) scope.launch { repository.executed(target) }
                }
            }
        }
        handler.postDelayed({ listen() }, 400)
    }
    override fun onError(error: Int) {
        val delay = if (error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) 5000L else 700L
        handler.postDelayed({ listen() }, delay)
    }
    override fun onReadyForSpeech(params: Bundle?) = Unit
    override fun onBeginningOfSpeech() = Unit
    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit
    override fun onEndOfSpeech() = Unit
    override fun onPartialResults(partialResults: Bundle?) = Unit
    override fun onEvent(eventType: Int, params: Bundle?) = Unit
    override fun onDestroy() {
        running = false; handler.removeCallbacksAndMessages(null)
        recognizer?.cancel(); recognizer?.destroy(); scope.cancel()
        super.onDestroy()
    }
}
