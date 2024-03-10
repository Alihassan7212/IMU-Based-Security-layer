import android.content.Context
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.swipe.myapplication.components.Calibrator
import com.swipe.myapplication.components.SplashScreen

@Composable
fun routes(context : Context) {

    val navController = rememberNavController()
    
    NavHost(navController = navController, startDestination = "calibrator"  ){
        composable("splash"){
            SplashScreen(navController)
        }
        composable("calibrator"){
            Calibrator(context)
        }
    }

}