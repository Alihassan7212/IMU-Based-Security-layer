//package com.swipe.myapplication
//
//import android.hardware.Sensor
//import android.hardware.SensorEvent
//import android.hardware.SensorEventListener
//
//val iterationData = mutableListOf<Input>()
//
//class MySensorEventListener : SensorEventListener {
//    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
//        // Not needed for this example
//    }
//
//    override fun onSensorChanged(event: SensorEvent?) {
//        // Check if the sensor event is not null and is an accelerometer sensor event
//        if (event?.sensor?.type == Sensor.TYPE_ACCELEROMETER) {
//            // Extract accelerometer values
//            val xForce = event.values[0]
//            val yForce = event.values[1]
//            val zForce = event.values[2]
//
//            // Do something with the accelerometer values
//            // For example, you can store them in your data structure
//            val data = Input(xForce, yForce, zForce)
//            iterationData.add(data)
//
//            // Optionally, you can perform any other actions based on the sensor data
//        }
//    }
//}