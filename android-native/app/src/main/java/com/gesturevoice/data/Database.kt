package com.gesturevoice.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "gestures")
data class GestureEntity(
    @PrimaryKey val id: String,
    val name: String,
    val encryptedPoints: String,
    val color: Long = 0xFF00E5FF,
    val width: Float = 8f,
    val favorite: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)
@Entity(tableName = "triggers", indices = [Index("gestureId")], foreignKeys = [ForeignKey(entity = GestureEntity::class, parentColumns = ["id"], childColumns = ["gestureId"], onDelete = ForeignKey.CASCADE)])
data class TriggerEntity(@PrimaryKey val id: String, val gestureId: String, val phrase: String, val kind: String = "voice")
@Entity(tableName = "history", indices = [Index("gestureId")])
data class HistoryEntity(@PrimaryKey(autoGenerate = true) val id: Long = 0, val gestureId: String, val at: Long = System.currentTimeMillis())
@Dao interface GestureDao {
    @Query("SELECT * FROM gestures ORDER BY createdAt DESC") fun observe(): Flow<List<GestureEntity>>
    @Query("SELECT * FROM gestures") suspend fun all(): List<GestureEntity>
    @Query("SELECT * FROM gestures WHERE id=:id LIMIT 1") suspend fun get(id: String): GestureEntity?
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun save(entity: GestureEntity)
    @Query("DELETE FROM gestures WHERE id=:id") suspend fun delete(id: String)
    @Query("SELECT * FROM triggers") fun observeTriggers(): Flow<List<TriggerEntity>>
    @Query("SELECT * FROM triggers") suspend fun triggers(): List<TriggerEntity>
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun addTrigger(trigger: TriggerEntity)
    @Query("DELETE FROM triggers WHERE id=:id") suspend fun removeTrigger(id: String)
    @Insert suspend fun addHistory(history: HistoryEntity)
    @Query("SELECT * FROM history ORDER BY at DESC") fun observeHistory(): Flow<List<HistoryEntity>>
}
@Database(entities = [GestureEntity::class, TriggerEntity::class, HistoryEntity::class], version = 1, exportSchema = false)
abstract class GestureDatabase : RoomDatabase() { abstract fun dao(): GestureDao }
