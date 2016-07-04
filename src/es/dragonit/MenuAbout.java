/*****************************************************************************
 *  Attractive, for Android.
 *  GNU GPLv3
 *  by David Gonzalez, 2016 (davidglt@hotmail.com)
 *****************************************************************************/

package es.dragonit;

import android.app.Activity;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager.NameNotFoundException;
import android.os.Bundle;
import android.widget.RelativeLayout;
import android.widget.TextView;

public class MenuAbout extends Activity {

	@ Override
	public void onCreate (Bundle savedlnstanceState) {
		super.onCreate(savedlnstanceState);
		
		PackageInfo pinfo = null;
		try {
			pinfo = getPackageManager().getPackageInfo(getPackageName(), 0);
		} catch (NameNotFoundException e) {
		}
		//int versionNumber = pinfo.versionCode;
		String versionName = pinfo.versionName;
		
		RelativeLayout relativeLayout = new RelativeLayout(this);
		RelativeLayout.LayoutParams lParams = new RelativeLayout.LayoutParams(
		                RelativeLayout.LayoutParams.FILL_PARENT,
		                RelativeLayout.LayoutParams.FILL_PARENT);
		
		TextView text = new TextView(this);
        text.setText(getResources().getString(R.string.msg_codename) + "\n" +
        		getResources().getString(R.string.msg_version) + versionName + "\n" +
        		"\n" +
        		getResources().getString(R.string.msg_soporte) + "\n" +
        		getResources().getString(R.string.msg_soporte_email) + "\n" + "\n" +
        		getResources().getString(R.string.msg_license) + "\n" +
        		getResources().getString(R.string.url_github) + "\n" +
        		getResources().getString(R.string.msg_copyright));
        
        // finally add your TextView to the RelativeLayout
        relativeLayout.addView(text);

        // and set your layout like main content
        setContentView(relativeLayout, lParams);
	}
}
