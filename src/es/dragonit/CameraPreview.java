/*****************************************************************************
 *  Attractive, for Android.
 *  GNU GPLv3
 *  by David Gonzalez, 2016 (davidglt@hotmail.com)
 *****************************************************************************/

package es.dragonit;

import java.io.IOException;

import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.util.Log;
import android.view.SurfaceHolder;
import android.widget.ImageView;
import android.graphics.Bitmap;
import android.graphics.ImageFormat;
import android.hardware.Camera;
import android.hardware.Camera.CameraInfo;
import android.hardware.Camera.Parameters;

public class CameraPreview implements SurfaceHolder.Callback, Camera.PreviewCallback
{
	private static Camera mCamera = null;
	private ImageView MyCameraPreview = null;
	private Bitmap bitmap = null;
	private Bitmap lastok_bitmap = null;
	private int[] pixels = null;
	private byte[] FrameData = null;
	private int imageFormat;
	private int PreviewSizeWidth;
 	private int PreviewSizeHeight;
 	private boolean bProcessing = false;
 	Integer previewFormat = 17; 
	
 	Handler mHandler = new Handler(Looper.getMainLooper());
 	
	public CameraPreview(int PreviewlayoutWidth, int PreviewlayoutHeight,
    		ImageView CameraPreview)
    {
		PreviewSizeWidth = PreviewlayoutWidth;
    	PreviewSizeHeight = PreviewlayoutHeight;
    	MyCameraPreview = CameraPreview;
    	bitmap = Bitmap.createBitmap(PreviewSizeWidth, PreviewSizeHeight, Bitmap.Config.ARGB_8888);
    	pixels = new int[PreviewSizeWidth * PreviewSizeHeight];
    }

	@Override
	public void onPreviewFrame(byte[] arg0, Camera arg1) 
	{
		//We only accept the NV21(YUV420) format.
		if (imageFormat == ImageFormat.NV21)
		{
			if ( !bProcessing )
			{
				FrameData = arg0;
				mHandler.post(DoImageProcessing);
			}
        }
	}

	@Override
	public void surfaceChanged(SurfaceHolder arg0, int arg1, int arg2, int arg3) 
	{
	    Parameters parameters;
		
	    parameters = mCamera.getParameters();
		// Set the camera preview size
		parameters.setPreviewSize(PreviewSizeWidth, PreviewSizeHeight);
		parameters.setPreviewFormat(previewFormat);
		imageFormat = parameters.getPreviewFormat();
		mCamera.setParameters(parameters);
		mCamera.startPreview();
	}

	@Override
	public void surfaceCreated(SurfaceHolder arg0) 
	{
		//mCamera = Camera.open(CameraInfo.CAMERA_FACING_FRONT);
		// Open in a thread, not in UI
		startCamera();
		try
		{
			// If did not set the SurfaceHolder, the preview area will be black.
			mCamera.setPreviewDisplay(arg0);
			mCamera.setPreviewCallback(this);
		} 
		catch (IOException e)
		{
			mCamera.release();
			mCamera = null;
		}
	}

	@Override
	public void surfaceDestroyed(SurfaceHolder arg0) 
	{
    	mCamera.setPreviewCallback(null);
		mCamera.stopPreview();
		mCamera.release();
		mCamera = null;
	}

	//
	// Native JNI 
	//
    public native boolean ImageProcessing(int width, int height, 
    		byte[] NV21FrameData, int [] pixels);
    static 
    {
    	System.loadLibrary("opencv_java");
    	System.loadLibrary("nonfree");
        System.loadLibrary("ImageProcessing");
    }
    
    private Runnable DoImageProcessing = new Runnable() 
    {
        public void run() 
        {
        	bProcessing = true;
			boolean faceok = ImageProcessing(PreviewSizeWidth, PreviewSizeHeight, FrameData, pixels);
			if (faceok) {
				Log.i("es.dragonit", "Showing last matched");
				bitmap.setPixels(pixels, 0, PreviewSizeWidth, 0, 0, PreviewSizeWidth, PreviewSizeHeight);
				lastok_bitmap = bitmap;
				MyCameraPreview.setImageBitmap(bitmap);
			}
			else {
				MyCameraPreview.setImageBitmap(lastok_bitmap);
			}
			bProcessing = false;
        }
    };
    
    private void startCamera() {
        if (mThread == null) {
            mThread = new CameraHandlerThread();
        }

        synchronized (mThread) {
            mThread.openCamera();
        }
    }
    private CameraHandlerThread mThread = null;
    private static class CameraHandlerThread extends HandlerThread {
        Handler mHandler = null;

        CameraHandlerThread() {
            super("CameraHandlerThread");
            start();
            mHandler = new Handler(getLooper());
        }

        synchronized void notifyCameraOpened() {
            notify();
        }

        void openCamera() {
            mHandler.post(new Runnable() {
                @Override
                public void run() {
                	mCamera = Camera.open(CameraInfo.CAMERA_FACING_FRONT);
                    notifyCameraOpened();
                }
            });
            try {
                wait();
            }
            catch (InterruptedException e) {
            }
        }
    }

   }
