package es.dragonit;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import es.dragonit.R;
import android.app.Activity;
import android.content.Context;
import android.content.res.AssetManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;

public class Attractive extends Activity 
{
	private CameraPreview camPreview;
	private ImageView MyCameraPreview = null;
	private ViewGroup secondaryLayout;
 	protected static WakeLock wakeLock = null;
	private int PreviewSizeWidth = 640;
 	private int PreviewSizeHeight = 480;
 	
   @Override
    public void onCreate(Bundle savedInstanceState) 
    {
        super.onCreate(savedInstanceState);
        
        // No sleep
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wakeLock = pm.newWakeLock(PowerManager.FULL_WAKE_LOCK, "DoNotSleep");

        // copy needed files to SD
        CopyAssets();
        
        //Set this APK Full screen
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,  
				 			WindowManager.LayoutParams.FLAG_FULLSCREEN);
        //Set this APK no title
        requestWindowFeature(Window.FEATURE_NO_TITLE);  
        setContentView(R.layout.main);
                
        //
        // Create my camera preview 
        //
        
        // Get the width and height of the screen
        // int screenWidth = getWindowManager().getDefaultDisplay().getWidth();
        int screenHeight = getWindowManager().getDefaultDisplay().getHeight();
        
        MyCameraPreview = new ImageView(this);
        
        SurfaceView camView = (SurfaceView) findViewById(R.id.surfaceView);
        SurfaceHolder camHolder = camView.getHolder();
        
        camPreview = new CameraPreview(PreviewSizeWidth, PreviewSizeHeight, MyCameraPreview);
        
        camHolder.setFixedSize((screenHeight-10)/2, (screenHeight-10)*2/3);
        camHolder.addCallback(camPreview);
        camHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
        
        secondaryLayout = (ViewGroup) findViewById(R.id.linearLayout2);
        secondaryLayout.addView(MyCameraPreview, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT));
    }
    protected void onPause()
	{
		super.onPause();
		wakeLock.release();
	}
    
   	protected void onResume() {
   		super.onResume();
   		wakeLock.acquire();
	}
    
    private void CopyAssets() {
    	String source;
    	String dest;
        String extStorageDirectory = Environment.getExternalStorageDirectory().toString();

        File haarcascadesDirectory = new File(extStorageDirectory + "/attractive/haarcascades/");
        File modelsDirectory = new File(extStorageDirectory + "/attractive/models/");

        haarcascadesDirectory.mkdirs();
        modelsDirectory.mkdirs();
        
        // haarcascade_frontalface_alt.xml
        source = "haarcascade_frontalface_alt.xml";
        dest = extStorageDirectory + "/attractive/haarcascades/" + source;
        cp(source, dest);
        
        // haarcascade_eye.xml
        source = "haarcascade_eye.xml";
        dest = extStorageDirectory + "/attractive/haarcascades/" + source;
        cp(source, dest);

        // haarcascade_mcs_nose.xml
        source = "haarcascade_mcs_nose.xml";
        dest = extStorageDirectory + "/attractive/haarcascades/" + source;
        cp(source, dest);

        // haarcascade_mcs_mouth.xml
        source = "haarcascade_mcs_mouth.xml";
        dest = extStorageDirectory + "/attractive/haarcascades/" + source;
        cp(source, dest);
        
     	// svm_male_model.dat
        source = "svm_Male.dat";
        dest = extStorageDirectory + "/attractive/models/" + source;
        cp(source, dest);
        
     	// svm_male_model.dat
        source = "svm_Attractive.dat";
        dest = extStorageDirectory + "/attractive/models/" + source;
        cp(source, dest);
    }
    
    private void cp(String source, String dest) {
    	AssetManager assetManager = getAssets();
    	InputStream in = null;
        OutputStream out = null;
        try {
        	in = assetManager.open(source);
            out = new FileOutputStream(dest);
            copyFile(in, out);
            in.close();
            in = null;
            out.flush();
            out.close();
            out = null;
        } catch(Exception e) {
        }
    }
    
    private void copyFile(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[1024];
        int read;
        while((read = in.read(buffer)) != -1){
          out.write(buffer, 0, read);
        }
    }
}