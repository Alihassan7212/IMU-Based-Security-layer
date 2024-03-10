package com.swipe.myapplication.components

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat.getSystemService
import com.google.firebase.Firebase
import com.google.firebase.firestore.firestore
import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.ServerApi
import com.mongodb.ServerApiVersion
import com.mongodb.kotlin.client.coroutine.MongoClient
import com.mongodb.kotlin.client.coroutine.MongoCollection
import com.mongodb.kotlin.client.coroutine.MongoDatabase

import com.swipe.myapplication.Gesture
import com.swipe.myapplication.Input
import com.swipe.myapplication.R
import dev.ricknout.composesensors.accelerometer.getAccelerometerSensor
import dev.ricknout.composesensors.accelerometer.rememberAccelerometerSensorValueAsState
import dev.ricknout.composesensors.getSensor
import dev.ricknout.composesensors.getSensorManager
import dev.ricknout.composesensors.gyroscope.getGyroscopeSensor
import dev.ricknout.composesensors.gyroscope.rememberGyroscopeSensorValueAsState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.bson.Document
import vibrateForDurationInBackground
import java.util.UUID
@Composable
fun Calibrator(c: Context) {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color.Black
    ) {
        val coroutineScope = rememberCoroutineScope()
        var buttonText by remember { mutableStateOf("Start Calibrate") }
        var loopRunning by remember { mutableStateOf(false) }
        var counter by remember { mutableStateOf(0) }
        var sensorDataLists by remember { mutableStateOf<List<List<List<Input>>>>(emptyList()) }
        var value by remember { mutableStateOf(false) }
        var isReady by remember { mutableStateOf(false) }
        var isDone by remember { mutableStateOf(false) }
        var showBorder by remember { mutableStateOf(false) } // Control visibility of border

        val context = LocalContext.current

//        val accelerometerState by rememberAccelerometerSensorState(sensorDelay = SensorDelay.Fastest)
//        val gyroscopeState = rememberGyroscopeSensorState(sensorDelay = SensorDelay.Fastest)



        val sensorValue by rememberAccelerometerSensorValueAsState()


        val sensorV by rememberGyroscopeSensorValueAsState()



        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(Color.DarkGray, Color.Black),
                        startY = 0f,
                        endY = Float.POSITIVE_INFINITY
                    )
                ),
            contentAlignment = Alignment.Center
        ) {
            if (showBorder) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .border(10.dp, Color.Green, RectangleShape)
                ) {
                    // This box will have green border when showBorder is true
                }
            }

            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Image(
                    painter = painterResource(id = R.drawable.imgpick),
                    contentDescription = "Image for calibration",
                    modifier = Modifier
                        .size(500.dp) // Adjust the size of the image
                        .padding(20.dp)// Add padding around the image
                )

                Button(
                    onClick = {
                        if (counter < 7) {
                            coroutineScope.launch {
                                loopRunning = true
                                buttonText = "Processing"
                                val iterationData = mutableListOf<Input>()

                                val startTime = System.currentTimeMillis()
                                val duration = 1500 // Duration in milliseconds

                                showBorder = true // Show border before starting the loop

                                delay(1)
                                buttonText = "Lift Your Phone"
                                //vibrateForDurationInBackground(context, 5)

                                var step  = 0



                                while (step<1001) {
                                    var (x, y, z) = sensorValue.value
                                    var(x1,y1,z1) = sensorV.value


                                    var data = Input(
                                        x,
                                        y,z,x1,y1,z1
                                    )

                                    iterationData.add(data)

                                    step++
                                    delay(10)

                                }

                                showBorder = false // Hide border when loop exits

                                Log.i("COUNT", iterationData.size.toString())

                                    sensorDataLists = sensorDataLists + listOf(listOf(iterationData.toList())) // Adjusted here
                                counter++

                                delay(1)
                                buttonText = "Train counter $counter"

                                for (input in iterationData) {
                                    Log.i("DATA", input.toString())
                                }



                                if (counter == 7) {
                                    Log.i("FINAL DATA COUNT", sensorDataLists.size.toString())
                                    value = true
                                    loopRunning = false
                                    buttonText = "Start Loop"

                                    firebase(sensorDataLists)
                                }
                            }
                        }
                    },
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(text = buttonText)
                }

                if (value) {
                    done()
                }

                //Text(text = "Counter : $counter", modifier = Modifier.padding(8.dp), color = Color.White)
            }
        }
    }
}



//
//@Composable
//fun Calibrator(c: Context) {
//    Surface(
//        modifier = Modifier.fillMaxSize(),
//        color = Color.Black
//    ) {
//        val coroutineScope = rememberCoroutineScope()
//        var buttonText by remember { mutableStateOf("Start Calibrate") }
//        var loopRunning by remember { mutableStateOf(false) }
//        var counter by remember { mutableStateOf(0) }
//        var sensorDataLists by remember { mutableStateOf<List<List<Input>>>(emptyList()) }
//        var value by remember { mutableStateOf(false) }
//        var isReady by remember { mutableStateOf(false) }
//        var isDone by remember { mutableStateOf(false) }
//        var showBorder by remember { mutableStateOf(false) } // Control visibility of border
//
//        val sensorEventListener = remember {
//            object : SensorEventListener {
//                override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
//                    // Not needed for this example
//
//                }
//
//                override fun onSensorChanged(event: SensorEvent?) {
//                    event?.let {
//                         var previousAccelerometerData: Input? = null
//                         var previousGyroscopeData: Input? = null
//
//
//                        when (it.sensor.type) {
//                            Sensor.TYPE_ACCELEROMETER -> {
//                                val accelerometerData = Input(
//                                    x = event.values[0],
//                                    y = event.values[1],
//                                    z = event.values[2],
//                                    x1 = previousGyroscopeData?.x1 ?: 0f,
//                                    y2 = previousGyroscopeData?.y2 ?: 0f,
//                                    z3 = previousGyroscopeData?.z3 ?: 0f
//                                )
//                                previousAccelerometerData = accelerometerData
//                                addDataToList(accelerometerData)
//                            }
//
//                            Sensor.TYPE_GYROSCOPE -> {
//                                val gyroscopeData = Input(
//                                    x = previousAccelerometerData?.x ?: 0f,
//                                    y = previousAccelerometerData?.y ?: 0f,
//                                    z = previousAccelerometerData?.z ?: 0f,
//                                    x1 = event.values[0],
//                                    y2 = event.values[1],
//                                    z3 = event.values[2]
//                                )
//                                previousGyroscopeData = gyroscopeData
//                                addDataToList(gyroscopeData)
//                            }
//                        }
//                    }
//                }
//
//                private fun addDataToList(data: Input) {
//                    // Add the data to the sensorDataLists
//                    sensorDataLists += listOf(data)
//                }
//            }
//        }
//
//        Box(
//            modifier = Modifier.fillMaxSize().background(
//                brush = Brush.verticalGradient(
//                    colors = listOf(Color.DarkGray, Color.Black),
//                    startY = 0f,
//                    endY = Float.POSITIVE_INFINITY
//                )
//            ),
//            contentAlignment = Alignment.Center
//        ) {
//            if (showBorder) {
//                Box(
//                    modifier = Modifier
//                        .fillMaxSize()
//                        .border(10.dp, Color.Green, RectangleShape)
//                ) {
//                    // This box will have green border when showBorder is true
//                }
//            }
//
//            Column(
//                modifier = Modifier.align(Alignment.Center),
//                horizontalAlignment = Alignment.CenterHorizontally,
//                verticalArrangement = Arrangement.Center
//            ) {
//                // Your UI elements here
//
//                Button(
//                    onClick = {
//                        if (counter < 7) {
//                            coroutineScope.launch {
//                                loopRunning = true
//                                buttonText = "Processing"
//
//                                // Register the sensor listener
//                                val sensorManager = c.getSystemService(Context.SENSOR_SERVICE) as SensorManager
//                                val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
//                                sensorManager.registerListener(sensorEventListener, accelerometer, SensorManager.SENSOR_DELAY_NORMAL)
//
//                                // Your data collection logic here
//                                // You can use sensorDataLists to collect the sensor data
//
//                                // Unregister the sensor listener when done
//                                sensorManager.unregisterListener(sensorEventListener)
//
//                                // Update UI or perform any other actions as needed
//                            }
//                        }
//                    },
//                    modifier = Modifier.padding(16.dp)
//                ) {
//                    Text(text = buttonText)
//                }
//
//                // Other UI elements
//            }
//        }
//    }
//}
//
//


@Composable
fun done() {
    Text(text = "record tracked")
}


//const val uri = "mongodb+srv://londonencode:authuser@clusterauth.nfhvz21.mongodb.net/?retryWrites=true&w=majority&appName=ClusterAuth"



const val uri = "mongodb+://londonencode:authuser@clusterauth.nfhvz21.mongodb.net/?retryWrites=true&w=majority&appName=ClusterAuth"



//suspend fun main(inputs: List<List<Input>>){
//    val connectionString = uri
//
//
//
//
//    val mongoClientSettings = MongoClientSettings.builder()
//        .applyConnectionString(ConnectionString(connectionString))
//        .build()
//
//
//    MongoClient.create(mongoClientSettings).use { mongoClient ->
//        val database = mongoClient.getDatabase("value")
//        val collection = database.getCollection<Gesture>("gestures")
//
//        inputs.forEach { inputList ->
//            val gestures = inputList.map { input ->
//                Gesture(
//                    x = input.x,
//                    y = input.y,
//                    z = input.z,
//                    x1 = input.x1,
//                    y1 = input.y2,
//                    z1 = input.z3,
//                    time = input.time
//                )
//            }
//
//            collection.insertMany(gestures)
//        }
//    }
//}




//suspend fun insertDataToMongo(inputs: List<List<Input>>) {
//    val client = MongoClient.create(uri)
//    val database = client.getDatabase("value")
//
//    try {
//        val collection = database.getCollection<Gesture>("gestures")
//
//        inputs.forEach { inputList ->
//            val gestures = inputList.map { input ->
//                Gesture(
//                    x = input.x,
//                    y = input.y,
//                    z = input.z,
//                    x1 = input.x1,
//                    y1 = input.y2,
//                    z1 = input.z3,
//                    time = input.time
//                )
//            }
//
//            collection.insertMany(gestures) // Insert the list of gestures directly
//        }
//    } finally {
//        client.close()
//    }
//}
//


//
//fun insertData(inputs: List<List<Input>>) {
//    val settings = MongoClientSettings.builder()
//        .applyConnectionString(ConnectionString(connectionString))
//        .applyToClusterSettings { builder: ClusterSettings.Builder ->
//            builder.hosts(listOf(ServerAddress("clusterauth.nfhvz21.mongodb.net")))
//        }
//        .streamFactoryFactory(NettyStreamFactoryFactory.builder().build())
//        .build()
//
//    val client = MongoClients.create(settings)
//    val database = client.getDatabase("mydb")
//    val collection = database.getCollection("inputs")
//    for (inputList in inputs) {
//        val documents = mutableListOf<Document>()
//
//        for (input in inputList) {
//            val inputDocument = Document()
//                .append("x", input.x)
//                .append("y", input.y)
//                .append("z", input.z)
//                .append("x1", input.x1)
//                .append("y2", input.y2)
//                .append("z3", input.z3)
//                .append("time", input.time)
//            documents.add(inputDocument)
//        }
//
//        val modelDocument = Document("model", Build.MODEL)
//            .append("data", documents)
//        collection.insertOne(modelDocument)
//    }
//
//    client.close()
//}

fun firebase(it: List<List<List<Input>>>) {
    val db = Firebase.firestore

    // Generate UUID outside of the Firebase operation
    val model = UUID.randomUUID().toString()

    val data = hashMapOf<String, Any>()

    for ((index, outerListInput) in it.withIndex()) {
        val flattenedData = mutableListOf<Map<String, Any>>()
        for (middleListInput in outerListInput) {
            for (input in middleListInput) {
                val inputMap = mapOf(
                    "x" to input.x,
                    "y" to input.y,
                    "z" to input.z,
                    "x1" to input.x1,
                    "y2" to input.y2,
                    "z3" to input.z3,
                )
                flattenedData.add(inputMap)
            }
        }
        data["$index"] = flattenedData
    }

    db.collection("inputs")
        .document(model) // Using the UUID as the document ID
        .set(data)
        .addOnSuccessListener {
            Log.d("Firestore", "Document added with ID: $model")
        }
        .addOnFailureListener { e ->
            Log.e("Firestore", "Error adding document", e)
        }
}


//
//fun firebase(it: List<List<List<Input>>>) {
//    val db = Firebase.firestore
//    val model = UUID.randomUUID().toString()
//
//    val data = hashMapOf<String, Any>()
//
//    for ((index, outerListInput) in it.withIndex()) {
//        val flattenedData = mutableListOf<Map<String, Any>>()
//        for (middleListInput in outerListInput) {
//            for (input in middleListInput) {
//                val inputMap = mapOf(
//                    "x" to input.x,
//                    "y" to input.y,
//                    "z" to input.z,
//                    "x1" to input.x1,
//                    "y2" to input.y2,
//                    "z3" to input.z3,
//                    "time" to input.time
//                )
//                flattenedData.add(inputMap)
//            }
//        }
//        data["$index"] = flattenedData
//    }
//
//    db.collection("inputs")
//        .add(data)
//        .addOnSuccessListener { documentReference ->
//            Log.d("Firestore", "DocumentSnapshot added with ID: ${documentReference.id}")
//        }
//        .addOnFailureListener { e ->
//            Log.e("Firestore", "Error adding document", e)
//        }
//}




//@Composable
//@Preview
//fun preview(){
//    Calibrator()
//}

//                        while (counter > 0) {
//                            val iterationData = mutableListOf<List<Input>>()
//                            repeat(3) { iteration ->
//                                val sensorDataList: MutableList<Input> = mutableListOf()
//                                repeat(20) {
//                                    val data = Input(
//                                        accelerometerState.xForce,
//                                        accelerometerState.yForce,
//                                        accelerometerState.zForce,
//                                        gyroscopeState.xRotation,
//                                        gyroscopeState.yRotation,
//                                        gyroscopeState.zRotation,
//                                        System.currentTimeMillis().toFloat()
//                                    )
//                                    sensorDataList.add(data)
//                                    delay(50)
//                                }
//                                iterationData.add(sensorDataList)
//                            }
//
//                            sensorDataLists.value += iterationData
//                            counter--
//                        }



//@Composable
//fun Calibrator() {
//
//    val sensorDataList: MutableList<Input> = mutableListOf<Input>()
//    Surface {
//        Column(
//            modifier = Modifier.fillMaxSize(),
//            horizontalAlignment = Alignment.CenterHorizontally,
//            verticalArrangement = Arrangement.Center
//        ) {
//            val coroutineScope = rememberCoroutineScope()
//            var buttonText by remember { mutableStateOf("Start Loop") }
//            var loopRunning by remember { mutableStateOf(false) }
//
//            val accelerometerState = rememberAccelerometerSensorState()
//            val gyroscopeState = rememberGyroscopeSensorState()
//
//            Button(
//                onClick = {
//                    coroutineScope.launch {
//                        loopRunning = true
//                        buttonText = "Loop Running..."
//
//
//                        val startTime = System.currentTimeMillis()
//
//                        while (loopRunning) {
//                            val currentTime = System.currentTimeMillis()
//                            if (currentTime - startTime >= 3000L) break
//
//
//                            // Collect sensor data here
//                            Log.i("SensorData", "Accelerometer X: ${accelerometerState.xForce} Accelerometer Y: ${accelerometerState.yForce} Accelerometer Z: ${accelerometerState.zForce} Gyroscope X: ${gyroscopeState.xRotation} Gyroscope Y: ${gyroscopeState.yRotation} Gyroscope Z: ${gyroscopeState.zRotation} Timestamp: ${System.currentTimeMillis().toFloat()}")
////                            Log.i("SensorData", "Accelerometer Y: ${accelerometerState.yForce}")
////                            Log.i("SensorData", "Accelerometer Z: ${accelerometerState.zForce}")
////                            Log.i("SensorData", "Gyroscope X: ${gyroscopeState.xRotation}")
////                            Log.i("SensorData", "Gyroscope Y: ${gyroscopeState.yRotation}")
////                            Log.i("SensorData", "Gyroscope Z: ${gyroscopeState.zRotation}")
//                           // Log.i("SensorData", "Timestamp: ${System.currentTimeMillis().toFloat()}")
//
//                            val data = Input(
//                                accelerometerState.xForce,
//                                accelerometerState.yForce,
//                                accelerometerState.zForce,
//                                gyroscopeState.xRotation,
//                                gyroscopeState.yRotation,
//                                gyroscopeState.zRotation,
//                                System.currentTimeMillis().toFloat()
//                            )
//                            sensorDataList.add(data)
//
//
//
//
//                            // No delay for continuous tracking
//                            // Adjust loop termination condition as needed
//                        }
//
//
//                    }
//                },
//
//                modifier = Modifier.padding(16.dp)
//            ) {
//
//            }
//
//            if (loopRunning) {
//                CircularProgressIndicator()
//            }
//        }
//    }
//}
