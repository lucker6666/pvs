package helpers;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

/**
 * Created with IntelliJ IDEA.
 * User: sneha
 * Date: 30/10/2012
 * Time: 15:54
 * To change this template use File | Settings | File Templates.
 */
public class BrowserDrivers {
    private WebDriver driver;
    private String browser;
    private DesiredCapabilities caps;

    public BrowserDrivers(String browser) {
        this.browser = browser;
        this.caps = this.getCap(this.browser);
        this.getDriver(caps);
    }


    public DesiredCapabilities getCap(String browser) {
        DesiredCapabilities capability = null;

        if (browser.equalsIgnoreCase("firefox")) {
            System.out.println("firefox");
            capability = DesiredCapabilities.firefox();
            capability.setBrowserName("firefox");
            capability.setPlatform(org.openqa.selenium.Platform.ANY);
//capability.setVersion("");
        }

        if (browser.equalsIgnoreCase("chrome")) {
            System.out.println("chrome");
            capability = DesiredCapabilities.chrome();
            capability.setBrowserName("chrome");
            capability.setPlatform(org.openqa.selenium.Platform.ANY);
	    //capability.setCapability("chrome.binary", "/usr/bin/google-chrome");
//capability.setVersion("");
        }

        if (browser.equalsIgnoreCase("iexplorer")) {
            System.out.println("internetExplorer");
            capability = DesiredCapabilities.internetExplorer();
            capability.setBrowserName("internet explorer");
            capability.setPlatform(Platform.WINDOWS);
//            capability.setVersion("9");
            capability.setCapability("webdriver.ie.driver","/Users/sneha/Downloads/Selenium/IEDriverServer.exe ");
//capability.setVersion("");
        }
        return capability;
    }

    private void getDriver(DesiredCapabilities caps) {
        try {
            this.driver = new ScreenShotRemoteWebDriver(new URL("http://10.92.16.180:4444/wd/hub"), caps);
        } catch (MalformedURLException e) {
            System.out.print("There was a problem with the URL: " + e.toString());
        }
    }

    public WebDriver get() {
        return this.driver;
    }




    /**
     * Saves a screenshot encoded in BASE64 string to a PNG file.
     * Works with any kind of webdriver except HTMLUnit (cause it works as a head-less browser)
     *
     */

    public void takeAScreenshot()
    {
        String destFilename = "/Users/sneha/svn/PyVBox_sel/testSS-"+System.currentTimeMillis()+".png";

        System.err.println("SCREEN SHOT FILENAME: " + destFilename);

        // check if implementation of current remote webdriver can take screenshots
        // works with every webdriver except HTMLUnit (cause it works as a head-less browser
        if (this.driver instanceof ScreenShotRemoteWebDriver)
        {
            // retrieve screenshot encoded in BASE64
            //
            String base64EncodedScreenshot = (String) ((ScreenShotRemoteWebDriver) this.driver).getScreenshotAs(OutputType.BASE64);
            // decode encoded string into byte[]
            Base64 b64 = new Base64();
            byte[] screenshot = b64.decode(base64EncodedScreenshot);

            // save it to a png file
            try
            {
                File f = new File(destFilename);
                FileUtils.writeByteArrayToFile(f, screenshot);
            }
            catch (IOException e)
            {
            
                e.printStackTrace();
            }
        }

    }
}

