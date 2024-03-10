import android.annotation.SuppressLint
import android.content.Context
import android.content.Context.VIBRATOR_SERVICE
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.util.Log
import androidx.core.content.ContextCompat.getSystemService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch


fun vibrateForDurationInBackground(context: Context, durationMillis: Long) {
    Log.d("Vibration", "Vibration requested for $durationMillis milliseconds")

        val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // Vibrate with a constant vibration for the specified duration
            vibrator.vibrate(VibrationEffect.createOneShot(durationMillis, VibrationEffect.EFFECT_HEAVY_CLICK))
        } else {
            // For older devices without VibrationEffect support
            @Suppress("DEPRECATION")
            Log.d("Vibration", "Vibration requested for $durationMillis milliseconds")
            vibrator.vibrate(durationMillis)
        }




}