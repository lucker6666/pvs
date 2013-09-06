package helpers;

import java.io.IOException;
import java.util.Properties;

/**
 * Created with IntelliJ IDEA.
 * User: sneha
 * Date: 05/11/2012
 * Time: 12:14
 * To change this template use File | Settings | File Templates.
 */
public class GetConfigProperties {

    public Properties getProperties(){
        Properties p = new Properties();
        try {
            p.load(getClass().getClassLoader().getResourceAsStream(("configuration.properties")));
        } catch (IOException e) {
            System.out.println(e.toString());
        }
        return p;
    }
}
