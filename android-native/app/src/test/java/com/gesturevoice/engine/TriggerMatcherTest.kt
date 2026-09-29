package com.gesturevoice.engine

import org.junit.Assert.*
import org.junit.Test

class TriggerMatcherTest {
    @Test fun accentsAndPunctuation() { assertTrue(TriggerMatcher.matches("Abrir,  CÂMERA!", "abrir camera")) }
    @Test fun avoidPartialActivation() { assertFalse(TriggerMatcher.matches("abrir câmera agora", "abrir camera")) }
    @Test fun rejectEmptyTrigger() { assertFalse(TriggerMatcher.matches("", "")) }
}
