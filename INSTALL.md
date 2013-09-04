Intro
-----

The necessary files for this project, besides those that come with your Python installation, are
	
* stplugin.h (from http://www.stata.com/plugins/)
* stplugin.c (from http://www.stata.com/plugins/)
* python_plugin.c
* python.ado
* stata.py
* stata_missing.py
		
Windows, using Visual Studio Express
------------------------------------
	
Below are the steps I used for compiling the plugin using Visual Studio Express 2012 and Python version 3.3 on Windows 7. StataCorp has notes for compiling plugins for other versions of Visual Studio at http://www.stata.com/plugins/
	
0. You will need Stata, Python, and Visual Studio Express 2012 installed. You will also need the Stata plugin header file stplugin.h and C file stplugin.c from section 2 of http://www.stata.com/plugins/.

1. Open Visual Studio. From the main menu at the top, select **File > New Project**.
		
2. A window pops up. Under the menu on the left, expand the **Visual C++** item, then select **Win32**. In the center pane of the window choose **Win32 Project**. On the bottom, change the name and solution name, if desired, then click **OK**.
		
3. Another window pops up. Click on **Next**. On the next screen, under **Application type**, choose **DLL**. Below that, check the box for **empty project**. Click on **Finish**.
		
4. In the main application window, on the right hand side, find **Resource Files**. Right click, select **Add > Existing Item**. Add each of these (you might have to right click and choose **Add > Existing Item** multiple times):

    1. python_plugin.c
    2. stplugin.h
    3. stplugin.c
    4. python33.lib$ (for me this resides in C:/Python33/libs)
		
5. Under **Resource Files**, click on python_plugin.c so that it's highlighted. In the main menu bar (at the top of the Visual Studio) select **VIEW > Property Pages**.
		
    A new window pops up. On the left, select **C/C++ > General**. On the right, click in the field next to **Additional Include Directories**, and type in the directory for Python.h (for me it is C:/Python33/include). Press enter or click on **OK**.
		
6. At the top, find **Debug** *below* the main menu bar (not the **DEBUG** *in* the main menu bar), and change this to **Release**. 
		
    You might have to repeat this and the previous step if you make other changes to settings or do these steps out of order.
		
7. If you have an x64 machine, change the field next to **Debug** from **Win32** to **x64**. This will require several steps. First, click on the field to open the menu, and choose **Configuration Manager...**. A new window pops up. Under platform, select **New...**, then select x64. Click on **OK**, then **Close**.
	
8. In the main menu bar select **BUILD > Build Solution** or use the shortcut, F7. You should get a message in the Output window, below the main window, that says the project was successfully compiled.
	
		
9. Rename the compiled dll (if necessary) to python_plugin.plugin.
		
    Using the default settings, for me the compiled dll is found in
		
    C:/Users/<my username>/My Documents/Visual Studio 2012/
        Projects/<project name>/x64/Release
		
    (with <my username> and <project name> replaced).
		
    Put python_plugin.plugin and python.ado in Stata's ado path (in Stata use command ``adopath`` to see the ado path), and put stata.py and stata_missing.py in Python's path (in Python use ``import sys`` then ``sys.path`` to see directories in the path). 
		
    As an alternative to putting files in the ado path and/or the Python path, you can put some or all of these files into a common directory and ``cd`` to that directory in Stata before first calling the plugin. This works because the current working directory is always in the ado path, and the directory in which the Python plugin was first called will be in the Python path.
	
10. Open Stata and type python. If everything has worked, this should start an interactive session of Python within Stata. A horizontal line should appear, with text to indicate a Python interactive session has started, similar to when starting an interactive session of Mata. If error messages and results are not printed to the screen, check to make sure stata.py is somewhere that Python can find it.
	
	
Mac OS X
--------

(thanks to Kit Baum for working on this)

The plugin was successfully installed on Mac OS X with the following steps. First, make sure that Python3.3 is installed. An OS X installer can be found at http://www.python.org/getit/. After installing Python3.3, you might need change the definition of ``python`` to point to the python3.3 executable. You can do this by renaming the /usr/local/python to /usr/local/python2.7 (assuming Python2.7 is the default version) and then adding a symlink from /usr/local/python to /usr/local/bin/python3.3.

You will also need gcc. You can get gcc with Xcode (https://developer.} \lstinline{apple.com/xcode/), or the Command Line Tools for Xcode (see, for example, http://www.mkyong.com/mac/how-to-install-gcc-compiler-on-mac-os-x/).

Next, make sure python_plugin.c, stplugin.c, and stplugin.h reside in the same directory. To compile the plugin, start with the compiler command from http://www.stata.com/plugins/, modified for this plugin:

...
gcc -bundle -DSYSTEM=APPLEMAC stplugin.c 
  python_plugin.c -o python_plugin.plugin
...
	
Add to that compiler and linker flags for Python, which can be obtained as in http://docs.python.org/3.3/extending/embedding.html#compiling-and-linking-under-unix-like-systems.

After compiling, python_plugin.plugin and python.ado need to be put in Stata's ado path and stata.py and stata_missing.py need to be put in the Python path. Alternately, any or all of these files can be in the directory from which the ``python`` command is first invoked, because that directory should be in both the ado path and Python path.
