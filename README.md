# PVS
PVS stands for Python-VirtualBox-Selenium. 
This tool allows you to manage VirtualBox VMs with a simple HTTP server that 
allows to run ie. Selenium Grid tests.

To make this happen we are using:
* [Flask](http://flask.pocoo.org/docs/) as the HTTP server  
* [VBoxManage](http://www.virtualbox.org/manual/ch08.html) as the command-line interface to VirtualBox  
* [Maven-URL-Poller-Plugin](http://code.google.com/p/maven-urlpoller-plugin/) to poll PVS server from Maven.

In just few words PVS uses Flask to translates URL queries into the VBoxManage commands.  

## Basic scenario
Basic scenario looks like this:

1. Configure your VMs with all the browsers you need
2. Add appropriate JSON description to those VMs
3. In your pom.xml provide a list of required browsers and their versions ex. [{"firefox":"20"},{"chrome":"20"}]
4. Then using maven-urlpoller-plugin send a query to the PVS server to find out which VMs have the required browsers installed 
5. If all the browser requirements are met, PVS will start matching VMs
6. PVS will Start the selenium-grid hub and all the nodes will register themselves to that hub
7. Maven will start Selenium tests
8. PVS will shut down all the VMs after all tests are finished


## Prerequisites

* [Virtual Box](https://www.virtualbox.org/)
* python 2.7.3
* [pip](https://pypi.python.org/pypi/pip)
* [virtualenv](https://pypi.python.org/pypi/virtualenv)
* [Flask](http://flask.pocoo.org/docs/)

Installation steps:
```bash
# install pip
sudo apt-get install python-pip
# install virtualenv
sudo pip install virtualenv  
# craete new virtual env
virtualenv pvs  
# acticate that env
source pvs/bin/activate
# install Flask
pip install Flask  
```

## Few words on:

### VBoxManage
[VBoxManage](http://www.virtualbox.org/manual/ch08.html) is the command-line interface to control and manage the virtualbox from the host machine

### Flask
[Flask](http://flask.pocoo.org/docs/) is a micro-framework for python which has a built-in development server. Flask is used in the tool to start a simple http server and also to bind the funcitons to URLs.

### Maven-URL-Poller-Plugin
Used to poll URL for certain number of times until it gets required status code or times out
http://code.google.com/p/maven-urlpoller-plugin/


## Example configuration:

### Add JSON description to VMs
Open VM setting and in the description field add a simple JSON that defines a list 
of installed browsers and their respective versions.  
PVS will use these details to match requested browser(s).

```json
{
    "box": {
        "OS": "linux",
        "OS_lang": "en-GB",
        "Browsers": {
            "CHROME": {
                "version": "21",
                "lang": "en",
                "plugins": null
            },
            "firefox": {
                "version": "21",
                "lang": "en",
                "plugins": null
            }
        }
    }
}
```

### Configuring Maven
Configure Maven to execute Flask URLs. Use maven-url-poller-plugin dependency to poll the URLs until the required response is obtained.

maven-url-poller-plugin dependency:
```xml
<dependencies>
        <dependency>
            <groupId>net.kennychua</groupId>
            <artifactId>maven-urlpoller-plugin</artifactId>
            <version>1.0.3</version>
        </dependency>
    </dependencies>
```

Executing flask URL using poller plugin:
```xml
<plugin>
    <groupId>net.kennychua</groupId>
    <artifactId>maven-urlpoller-plugin</artifactId>

     <executions>
        <!-- Verifying if the Flask server has been started. This endpoint returns welcome page -->
        <execution>
                <id>Flask Welcome</id>
            <configuration>
               <pollUrl>${pvb-url}/</pollUrl>
               <statusCode>200</statusCode>
               <secondsBetweenPolls>10</secondsBetweenPolls>
               <repeatFor>5</repeatFor>
               <failOnFailure>false</failOnFailure>
            </configuration> 
            <phase>initialize</phase>
            <goals>
                <goal>poll</goal>
            </goals>
        </execution>
        '
        '
    </executions>
</plugin>
```

### Starting Flask Server
To start the flask server, run the Python script in a Python interpreter:
```python
python py-vbox-helpers.py 
```
which should start the server and return the host address and port it is running on:
```
* Running on http://0.0.0.0:5000/
* Restarting with reloader
```
When the URL : http://0.0.0.0:5000/pvb/ is opened in a browser, Python virtual box welcome screen should be found.

Steps included in py-vbox-helpers.py to start the Flask server:
1. Imported flask class
2. route() to tell flask to run particular python functions for respective URLs
3. run() function to start the Flask server

### Running Maven project
The project can be run from maven using
```
mvn install
```
The Flask endpoints, as configured in pom.xml, are executed in order and wait for the expected status code. The project can be run manually by executing the Flask endpoints manually in a browser.

This project contains more of parsing data hence, the code might be a bit confusing and has many loops. 

To perform the following steps in order, start the flask server and use flask endpoints.

2. Provide the required browsers in the form of list of maps ex. [{"firefox":"20"},{"chrome":"20"}]
3. The tool parses the JSON in the description of all the VMs to check whether the requested browsers with expected version are present. If yes, get the list of VMs which match the criteria
4. Start the matched VMs if they are not already running. Start the VM which is dedicated to start Selenium hub
5. The started VMs register themselves to hub as selenium nodes
6. Parse the selenium grid console page to check whether all the browsers were registered as nodes
7. Run selenium tests
8. Shut down VMs

The project is also configured to run from maven using "mvn install". Here, maven-url-poller-plugin polls the Flask server and waits until the desired http status code is received. 
Example configuration: 
 
```xml
<configuration>
	<pollUrl>${pvb-url}/</pollUrl>
        <statusCode>200</statusCode>
        <secondsBetweenPolls>10</secondsBetweenPolls>
        <repeatFor>5</repeatFor>
        <failOnFailure>false</failOnFailure>
</configuration>
```

Provide the URL to be executed and the expected status code. Provide the interval between the polls and the number of times the request is made upon failure to get expected status code. 

### TO DO

1. Use static IPs for the Vms
2. Parameterize IPs used in the project
3. We have modified maven-url-poller-plugin to log a bit more information. Decide whether to use it as an updated maven plugin
4. Collate reports from different VMs in to one consolidated report


