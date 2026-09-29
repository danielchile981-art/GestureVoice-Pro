package com.gesturevoice.data

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.map
import javax.inject.Inject

private val Context.store by preferencesDataStore("settings")
class Preferences @Inject constructor(@ApplicationContext private val context: Context) {
    private val theme = stringPreferencesKey("theme")
    private val consent = booleanPreferencesKey("consent")
    val mode = context.store.data.map { it[theme] ?: "dark" }
    val accepted = context.store.data.map { it[consent] ?: false }
    suspend fun setTheme(value: String) { context.store.edit { it[theme] = value } }
    suspend fun setConsent(value: Boolean) { context.store.edit { it[consent] = value } }
}
