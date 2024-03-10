package com.swipe.myapplication.components

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowRight
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.swipe.myapplication.repository.SharedPreferencesManager


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun signup(navController: NavController, context:Context) {
    // Remembering the state for TextField value
    val (textValue, setTextValue) = remember { mutableStateOf("") }

    Surface {
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
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(text = "Enter Email", color = Color.White)
                // Passing the state and its setter to the TextField
                TextField(value = textValue, onValueChange = setTextValue)
            }

            // Floating button with arrow
            ExtendedFloatingActionButton(
                text = {Text(text = "Next")},
                onClick = { if(textValue.isNotEmpty()){
                    try{


                        SharedPreferencesManager.saveUser(context,textValue)



                        navController.navigate("calibrator")

                    }
                    catch (e: Exception){

                    }


                }
                                                      },
                icon = { Icons.Default.KeyboardArrowRight },
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(16.dp)
            )
        }
    }
}

@Preview
@Composable
fun preview() {
    //signup()
}