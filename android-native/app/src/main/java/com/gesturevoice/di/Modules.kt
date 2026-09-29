package com.gesturevoice.di

import android.content.Context
import androidx.room.Room
import com.gesturevoice.data.GestureDao
import com.gesturevoice.data.GestureDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Singleton

@Module @InstallIn(SingletonComponent::class)
object Modules {
    @Provides @Singleton fun database(@ApplicationContext context: Context): GestureDatabase =
        Room.databaseBuilder(context, GestureDatabase::class.java, "gestures.db").build()
    @Provides fun dao(database: GestureDatabase): GestureDao = database.dao()
}
