/*****************************************************************************
 *  Attractive, for Android.
 *  GNU GPLv3
 *  by David Gonzalez, 2016 (davidglt@hotmail.com)
 *****************************************************************************/

package es.dragonit;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import es.dragonit.R;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.AssetManager;
import android.hardware.Camera;
import android.os.Bundle;
import android.os.Environment;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.view.Menu;
import android.view.MenuItem;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.ImageView;

public class Attractive extends Activity 
{
	private FrameLayout mainLayout;
	private CameraPreview camPreview;
	private ImageView MyCameraPreview = null;
	private ViewGroup secondaryLayout;
 	protected static WakeLock wakeLock = null;
	private int PreviewSizeWidth = 640;
 	private int PreviewSizeHeight = 480;
 	private int currentCameraId = Camera.CameraInfo.CAMERA_FACING_FRONT;
 	
   @Override
    public void onCreate(Bundle savedInstanceState) 
    {
        super.onCreate(savedInstanceState);
        
        // No sleep
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wakeLock = pm.newWakeLock(PowerManager.FULL_WAKE_LOCK, "DoNotSleep");

        // Copy needed files to SD
        CopyAssets();
        
        // Set this APK Full screen
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,  
				 			WindowManager.LayoutParams.FLAG_FULLSCREEN); 
        setContentView(R.layout.main);
                
        //
        // Create my camera preview 
        //
        
        // Get the width and height of the screen
        // int screenWidth = getWindowManager().getDefaultDisplay().getWidth();
        int screenHeight = getWindowManager().getDefaultDisplay().getHeight();
        
        MyCameraPreview = new ImageView(this);
        
        SurfaceView camView = (SurfaceView) findViewById(R.id.surfaceView);
        final SurfaceHolder camHolder = camView.getHolder();
     	camPreview = new CameraPreview(PreviewSizeWidth, PreviewSizeHeight, MyCameraPreview, currentCameraId);
           
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
    
    /** Called when the menubar is being created by Android. */
    public boolean onCreateOptionsMenu(Menu menu) {
    	// Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.attractive, menu);
        return true;
    }

    /** Called whenever the user pressed a menu item in the menubar. */
    public boolean onOptionsItemSelected(MenuItem item) {
    	
    	switch (item.getItemId()) {
    		case R.id.mMenuSwitchCamera:
    			//swap the id of the camera to be used
 	    		if(currentCameraId == Camera.CameraInfo.CAMERA_FACING_BACK) {
 	    			currentCameraId = Camera.CameraInfo.CAMERA_FACING_FRONT;
 	    		}
 	    		else {
 	    			currentCameraId = Camera.CameraInfo.CAMERA_FACING_BACK;
 	    		}
 	    		SurfaceView camView = (SurfaceView) findViewById(R.id.surfaceView);
 	    		final SurfaceHolder camHolder = camView.getHolder();
 	    
 	    		camPreview.switchCamera(camHolder, currentCameraId);
    			return true;
    			
        	case R.id.mMenuAbout:
        		launchAbout(mainLayout);
        		return true;
        		
        	case R.id.mMenuFinish:
        		finish();
        		return true;
        		
        	default:
        		return super.onOptionsItemSelected(item);
    	}
    }
      
    /** About to. */
    public void launchAbout (View view) {
    	Intent i = new Intent (this, MenuAbout.class);
    	startActivity (i);
    }
}