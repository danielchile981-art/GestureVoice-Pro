package com.gesturevoice.data

import com.gesturevoice.engine.GestureMath
import com.gesturevoice.engine.Point
import com.gesturevoice.engine.TriggerMatcher
import java.util.UUID
import javax.inject.Inject

class GestureRepository @Inject constructor(val dao: GestureDao, private val cipher: CipherStore) {
    val gestures = dao.observe()
    val triggers = dao.observeTriggers()
    val history = dao.observeHistory()
    suspend fun create(name: String, points: List<Point>, color: Long, width: Float): String {
        require(name.isNotBlank() && points.size >= 2)
        val id = UUID.randomUUID().toString()
        dao.save(GestureEntity(id, name.trim(), cipher.encrypt(GestureMath.clamp(GestureMath.smooth(points))), color, width))
        return id
    }
    suspend fun points(id: String): List<Point> = dao.get(id)?.let { cipher.decrypt(it.encryptedPoints) }.orEmpty()
    suspend fun bind(gestureId: String, phrase: String) {
        require(phrase.isNotBlank())
        dao.addTrigger(TriggerEntity(UUID.randomUUID().toString(), gestureId, phrase.trim().lowercase()))
    }
    suspend fun find(heard: String): String? = dao.triggers().firstOrNull { it.kind == "voice" && TriggerMatcher.matches(heard, it.phrase) }?.gestureId
    suspend fun executed(id: String) = dao.addHistory(HistoryEntity(gestureId = id))
    suspend fun remove(id: String) = dao.delete(id)
}
