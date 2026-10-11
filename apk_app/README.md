# NO APAGUES LA LUZ — app Android independiente

APK autónomo: el juego entero (runtime pygbag/WASM + Python + assets + wheel de
pygame-ce) viaja **dentro** del APK y se sirve a un WebView local
(`WebViewAssetLoader`). No abre el navegador, no necesita internet y funciona
offline. La TWA (Bubblewrap) quedó descartada porque siempre usa Chrome por debajo.

## Compilar

```bash
# 1) build web (si no está hecho)
.venv/Scripts/python.exe tools/build_web.py --build

# 2) sincronizar assets al proyecto Android
.venv/Scripts/python.exe tools/sync_apk_assets.py

# 3) compilar el APK
cd apk_app
JAVA_HOME="/c/Program Files/Android/Android Studio/jbr" ./gradlew assembleRelease
# -> app/build/outputs/apk/release/app-release.apk
```

Requiere JDK 21 (el de Android Studio vale) y el SDK de Android
(`local.properties` con `sdk.dir=...`).

## Firma

Los secretos van en `keystore.properties` (ignorado por git; ver
`keystore.properties.example`). Sin ese archivo el APK sale sin firmar.

## Cómo funciona (trampas resueltas, ver docs/WEB-MOVIL.md)

- `assets/` = sitio + `cdn/` (runtime descargado del CDN público) + `web_src.gz.bin`.
- `MainActivity` sirve `https://appassets.androidplatform.net/...` desde assets.
- El runtime lleva URLs del CDN oficial incrustadas → se interceptan en
  `shouldInterceptRequest` y se sirven del paquete local **con CORS**.
- El aapt de Android descomprime/renombra los assets `.gz` → el archivo va como
  `web_src.gz.bin` y se sirve para la ruta `/web_src.tar.gz`.
