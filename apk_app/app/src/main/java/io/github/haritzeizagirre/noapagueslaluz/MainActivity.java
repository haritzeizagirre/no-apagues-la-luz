package io.github.haritzeizagirre.noapagueslaluz;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;

/**
 * NO APAGUES LA LUZ — app independiente.
 *
 * El juego entero (pygbag/WASM + Python + assets + wheel de pygame-ce) viaja
 * DENTRO del APK:
 *  - https://appassets.androidplatform.net/...  -> assets/ (WebViewAssetLoader)
 *  - https://pygame-web.github.io/cdn/...       -> assets/cdn/ (interceptor)
 *
 * Asi el runtime de pygbag, que tiene URLs del CDN oficial incrustadas, queda
 * servido en local: no hace falta navegador, ni internet, ni ninguna web.
 */
public class MainActivity extends Activity {

    private static final String CDN_HOST = "pygame-web.github.io";
    private static final String ASSET_HOST = "appassets.androidplatform.net";
    private WebView web;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideSystemUi();

        final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web = new WebView(this);
        WebView.setWebContentsDebuggingEnabled(true);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                // el aapt descomprime y renombra los assets .gz: el runtime pide
                // web_src.tar.gz pero en el paquete va como web_src.gz.bin
                if (url.getHost() != null && url.getHost().equals(ASSET_HOST)
                        && "/web_src.tar.gz".equals(url.getPath())) {
                    return serveAsset("web_src.gz.bin", "application/gzip");
                }
                WebResourceResponse local = assetLoader.shouldInterceptRequest(url);
                if (local != null) return local;
                if (CDN_HOST.equals(url.getHost())) {
                    return serveFromAssets(url.getPath());
                }
                return null;
            }
        });

        setContentView(web);
        web.loadUrl("https://appassets.androidplatform.net/index.html");
    }

    /** Sirve un archivo concreto de los assets con cabeceras CORS. */
    private WebResourceResponse serveAsset(String assetPath, String mime) {
        HashMap<String, String> cors = new HashMap<String, String>();
        cors.put("Access-Control-Allow-Origin", "*");
        cors.put("Access-Control-Allow-Methods", "GET, OPTIONS");
        cors.put("Access-Control-Allow-Headers", "*");
        try {
            InputStream is = getAssets().open(assetPath);
            return new WebResourceResponse(mime, null, 200, "OK", cors, is);
        } catch (IOException e) {
            return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", cors,
                    new ByteArrayInputStream(new byte[0]));
        }
    }

    /** Sirve una ruta del CDN oficial (/cdn/...) desde los assets locales. */
    private WebResourceResponse serveFromAssets(String path) {
        HashMap<String, String> cors = new HashMap<String, String>();
        cors.put("Access-Control-Allow-Origin", "*");
        cors.put("Access-Control-Allow-Methods", "GET, OPTIONS");
        cors.put("Access-Control-Allow-Headers", "*");
        try {
            if (path != null && path.startsWith("/cdn/")) {
                String assetPath = path.substring(1); // "cdn/..."
                InputStream is = getAssets().open(assetPath);
                return new WebResourceResponse(guessMime(assetPath), null, 200, "OK", cors, is);
            }
        } catch (IOException ignored) {
            // no esta en el paquete: respuesta vacia 404
        }
        return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", cors,
                new ByteArrayInputStream(new byte[0]));
    }

    private static String guessMime(String path) {
        if (path.endsWith(".js") || path.endsWith(".mjs")) return "text/javascript";
        if (path.endsWith(".json")) return "application/json";
        if (path.endsWith(".wasm")) return "application/wasm";
        if (path.endsWith(".css")) return "text/css";
        if (path.endsWith(".html")) return "text/html";
        if (path.endsWith(".ogg")) return "audio/ogg";
        if (path.endsWith(".whl")) return "application/octet-stream";
        if (path.endsWith(".data")) return "application/octet-stream";
        if (path.endsWith(".py")) return "text/x-python";
        return "application/octet-stream";
    }

    private void hideSystemUi() {
        View d = getWindow().getDecorView();
        d.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemUi();
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
