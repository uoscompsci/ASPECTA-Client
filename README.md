# ASPECTA-Client
The ASPECTA room configuration program and libraries that will help python clients communicate with the server.

###Dependencies
Make sure to install pip first as later ones depend on it for installation
* pip (```sudo apt-get install python-pip```)
* python-pygame (```sudo apt-get install python-pygame```)
* ujson (```sudo pip install ujson```)
* tkinter (```sudo apt-get install python-tk```)

###Recommended

These have been used for development and testing, so are recommended but not required.
* Eclipse (https://www.eclipse.org/downloads/ See eclipse notes below if eclipse won't run due to Java Runtime Environment issues)
* PyDev for Eclipse (see instructions below on how to download and install)

###Eclipse Notes

If elipse won't run after extraction you may need to run the following in a terminal:
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer
sudo apt-get install oracle-java7-set-default
```
If eclipse still doesn't start execute the following:
#####32-Bit Systems
```ln -s /usr/lib/jni/libswt-* ~/.swt/lib/linux/x86/```
#####64-Bit Systems
```ln -s /usr/lib/jni/libswt-* ~/.swt/lib/linux/x86_64/```

###Installing PyDev
#####Easy installation (For newer versions of Eclipse, attempt this first):

In the Eclipse menu go to "Help" -> "Install New Software" and use the source:

http://pydev.org/updates

To download PyDev 3.3.3. This will fail if the version of Eclipse is too old.

#####Manual Installation (For all versions of Eclipse):

Go to the PyDev website (http://pydev.org/manual_101_install.html) and download the zip file for Pydev 3.3.3

Navigate to ~/.eclipse/org.eclipse.platform_3.7.0_155965261/ (Eclipse version may be different) and create a folder called "dropins". Copy the contents of the downloaded zip file to this new folder.
