package pageElements;

import helpers.BrowserDrivers;
import helpers.GetConfigProperties;
import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterClass;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Parameters;
import org.testng.log4testng.Logger;
import org.openqa.selenium.chrome.ChromeDriverService;

/**
 * Created with IntelliJ IDEA.
 * User: sneha
 * Date: 04/10/2012
 * Time: 16:28
 * To change this template use File | Settings | File Templates.
 */
public class Test {

    static Logger logger = Logger.getLogger(Test.class);
    private WebDriver driver;
    private BrowserDrivers b;

    //private WebElementsInteraction webEle = new WebElementsInteraction();
    //private FindElementsWithCommonPrefix find = new FindElementsWithCommonPrefix();

    private GetConfigProperties properties = new GetConfigProperties();
    private String PAGE_URL = properties.getProperties().getProperty("vizualizr_URL");

    private static ChromeDriverService service;


    @Parameters({"browser"})
    @BeforeClass
    public void setUp(String browser) {
        this.b = new BrowserDrivers(browser);
        this.driver = this.b.get();

	//Logger.getRootLogger().setLevel(Level.INFO);
    }

    @org.testng.annotations.Test
    public void test_fourth() {
        try
        {
        this.driver.get(PAGE_URL);
this.b.takeAScreenshot();
         //  HotVenuesPage hp = new HotVenuesPage(driver);
           //CookiePolicyPage cp = new CookiePolicyPage(driver);
        //HomePage hp = new HomePage(driver);
            //webEle.hover(driver, By.cssSelector(".p50607a67e4b064dd99f073fe"));
            //driver.findElement( By.cssSelector(".p50607a67e4b064dd99f073fe")).click();
        }
        catch(Exception e)
        {
        this.b.takeAScreenshot();
        }

    }

    @AfterClass
    public void tearDown() {
        //Close the browser

        //driver.close();
        driver.quit();

    }

   /*private Properties getProperties(){
       Properties p = new Properties();
       try {
           p.load(getClass().getClassLoader().getResourceAsStream(("configuration.properties")));
       } catch (IOException e) {
           System.out.println(e.toString());
       }
       return p;
   }   */


}




