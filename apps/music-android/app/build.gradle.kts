plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.moodify.music"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.moodify.music"
        minSdk = 26
        targetSdk = 36
        versionCode = 3
        versionName = "2.0.1"
    }
    buildTypes {
        release { isMinifyEnabled = false }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    testOptions {
        unitTests.isIncludeAndroidResources = true
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.06.01")
    implementation(composeBom)
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.1")
    implementation("androidx.media3:media3-exoplayer:1.10.1")
    implementation("androidx.media3:media3-session:1.10.1")   // P09: MediaSessionService for background/lock-screen
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0") // P09: StateFlow
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0") // P09: Dispatchers.Main
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0") // P09: runTest
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
    testImplementation("org.robolectric:robolectric:4.14.1")
}
