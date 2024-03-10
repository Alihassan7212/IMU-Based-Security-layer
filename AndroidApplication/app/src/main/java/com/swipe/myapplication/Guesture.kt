package com.swipe.myapplication

import android.os.Build
import org.bson.codecs.pojo.annotations.BsonId
import java.util.Random
import java.util.UUID

data class Gesture(
    val _id: UUID? = UUID.randomUUID(),
    val id: String = Build.MODEL,
    val x: Float,
    val y: Float,
    val z: Float,
    val x1: Float,
    val y1: Float,
    val z1: Float,
    val time: Double
)