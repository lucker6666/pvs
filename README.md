# PVS
PVS stands for Python-VirtualBox-Selenium.
This tool will allow to to manage VBox VMs for running tests with Selenium Grid
1. Provide the required browsers in the form of list of maps ex. [{"firefox":"20"},{"chrome":"20"}]
2. The tool finds the VMs which have the required browsers installed and starts those VMs
3. Starts the selenium-grid hub and registers the browsers in VMs as nodes to the hub
4. Starts Selenium tests
5. Shut down VMs after tests



## Installation notes
It's recommended to use:
* [virtualenv](https://pypi.python.org/pypi/virtualenv)
* python 2.7.3

[sudo] pip install virtualenv
virtualenv pvs
pip install Flask

#VBoxManage
VBoxManage is the command-line interface to control and manage the virtualbox from the host machine
http://www.virtualbox.org/manual/ch08.html

#Flask
Flask is a micro-framework for python which has a built-in development server. Flask is used in the tool to start a simple http server and also to bind the funcitons to URLs.
http://flask.pocoo.org/docs/

#Maven-URL-Poller-Plugin
Maven plugin used to poll the URLs until the correct status code is returned back. Configure it to poll for a certain number of times if the correct status code is not received and the interval between the polls