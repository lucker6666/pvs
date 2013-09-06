package helpers;

import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.DriverCommand;
import org.openqa.selenium.remote.RemoteWebDriver;

import java.net.URL;


/**
 * This extends RemoteWebDriver class and implements TakesScreenshot interface 
 * by adding getScreenshotAs method ,that retrieves screenshot from remote node
 * encode as BASE64 string.
 *    
 * Author: Luke Inman-Semerau <luke.seme...@gmail.com>
 * For more info please refer to:
 * http://groups.google.com/group/selenium-users/browse_thread/thread/34b1d79613eb003b#msg_7f945d3e0abb7797
 * 
 * @author Luke Inman-Semerau
*/
/*     
#	Author			: Luke Inman-Semerau
#	Created Date	: 24 May 2011
#	REVISION HISTORY
#	DATE			CHANGED BY				DESCRIPTION
#	04Jul2011		Janusz Kowalczyk		Initial Creation   
*/ 
public class ScreenShotRemoteWebDriver extends RemoteWebDriver implements
		TakesScreenshot
{
	public ScreenShotRemoteWebDriver(URL url, DesiredCapabilities capabilities)
	{
		super(url, capabilities);
	}

	/**
	 * Retrieves screenshot from remote node
	 * 
	 * @return png encoded into requested format. Output format can be: BASE64, BYTES, FILE
	*/
	public <X> X getScreenshotAs(OutputType<X> target) throws WebDriverException
	{
		/*
		Command command = new Command(getSessionId(), null);
		getCommandExecutor().execute(command);
		*/
		if ((Boolean) getCapabilities().getCapability(CapabilityType.TAKES_SCREENSHOT))
			{
				return target.convertFromBase64Png(
						execute(DriverCommand.SCREENSHOT)
						.getValue().toString()
						);
			}
		return null;
	}
}
