package com.gesturevoice.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.os.Handler
import android.os.Looper
import android.view.WindowManager
import android.content.Context
import android.view.accessibility.AccessibilityEvent
import com.gesturevoice.engine.Point
import kotlin.math.max

class GestureAccessibility : AccessibilityService() {
    companion object { @Volatile var current: GestureAccessibility? = null; private set }
    override fun onServiceConnected() { super.onServiceConnected(); current = this }
    override fun onDestroy() { current = null; super.onDestroy() }
    override fun onAccessibilityEvent(event: AccessibilityEvent?) = Unit
    override fun onInterrupt() = Unit
    fun play(points: List<Point>, completion: (Boolean) -> Unit) {
        if (points.size < 2) { completion(false); return }
        val manager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val metrics = resources.displayMetrics
        val width = metrics.widthPixels.toFloat(); val height = metrics.heightPixels.toFloat()
        val path = Path().apply {
            moveTo(points.first().x.coerceIn(0f, 1f) * width, points.first().y.coerceIn(0f, 1f) * height)
            points.drop(1).forEach { lineTo(it.x.coerceIn(0f, 1f) * width, it.y.coerceIn(0f, 1f) * height) }
        }
        val duration = max(100L, (points.last().t - points.first().t).coerceAtMost(5000L))
        val description = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(path, 0, duration)).build()
        dispatchGesture(description, object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) = completion(true)
            override fun onCancelled(gestureDescription: GestureDescription?) = completion(false)
        }, Handler(Looper.getMainLooper()))
    }
}
