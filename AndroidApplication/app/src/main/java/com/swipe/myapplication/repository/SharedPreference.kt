package com.swipe.myapplication.repository

import android.content.Context
import android.content.SharedPreferences
import java.util.UUID

object SharedPreferencesManager {
    private const val PREF_NAME = "MyAppPreferences"
    private const val UUID_NAME = "User_ID"
    private const val KEY_EMAIL = "email"

    fun saveUser(context: Context, email: String) {
        val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        val editor: SharedPreferences.Editor = sharedPreferences.edit()
        editor.putString(KEY_EMAIL, email)
        editor.putString(UUID_NAME,UUID.randomUUID().toString())
        editor.apply()
    }

    fun getEmail(context: Context): String? {
        val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return sharedPreferences.getString(KEY_EMAIL, null)
    }

    fun getUUID(context: Context):String?{
        val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return sharedPreferences.getString(UUID_NAME, null)
    }

    fun clearEmail(context: Context) {
        val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        val editor: SharedPreferences.Editor = sharedPreferences.edit()
        editor.remove(KEY_EMAIL)
        editor.apply()
    }
}