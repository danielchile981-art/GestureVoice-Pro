package com.gesturevoice.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Night = Color(0xFF0B0F1A)
val Card = Color(0xFF131A2B)
val Cyan = Color(0xFF00E5FF)
val Violet = Color(0xFF7C4DFF)
val Pink = Color(0xFFFF2E93)
val Muted = Color(0xFFA8B2C7)
private val dark = darkColorScheme(primary = Cyan, secondary = Violet, background = Night, surface = Card, onBackground = Color.White, onSurface = Color.White)
private val light = lightColorScheme(primary = Color(0xFF006A77), secondary = Violet, background = Color(0xFFF3F7FF), surface = Color.White)
@Composable fun GestureTheme(mode: String = "dark", content: @Composable () -> Unit) {
    val useDark = mode == "dark" || (mode == "auto" && isSystemInDarkTheme())
    MaterialTheme(colorScheme = if (useDark) dark else light, typography = Typography(), content = content)
}
