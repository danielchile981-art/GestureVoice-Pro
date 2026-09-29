package com.gesturevoice.engine

import java.text.Normalizer
import java.util.Locale

object TriggerMatcher {
    fun normalize(text: String): String = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFD)
        .replace(Regex("\\p{M}+"), "").replace(Regex("[^a-z0-9 ]"), " ")
        .replace(Regex("\\s+"), " ").trim()
    fun matches(heard: String, phrase: String): Boolean = normalize(heard) == normalize(phrase) && normalize(phrase).isNotBlank()
}
