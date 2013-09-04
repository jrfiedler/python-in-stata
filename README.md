
 [ ]  name of the projects and all sub-modules and libraries (sometimes they are named different and very confusing to new users)
 [ ]  descriptions of all the project, and all sub-modules and libraries
 [x]  5-line code snippet on how its used (if it's a library)
 [x]  copyright and licensing information (or "Read LICENSE")
 [x]  instruction to grab the documentation
 [x]  instructions to install, configure, and to run the programs
 [x]  instruction to grab the latest code and detailed instructions to build it (or quick overview and "Read INSTALL")
 [x]  list of authors or "Read AUTHORS"
 [ ]  instructions to submit bugs, feature requests, submit patches, join mailing list, get announcements, or join the user or dev community in other forms
 [x]  other contact info (email address, website, company name, address, etc)
 [o]  a brief history if it's a replacement or a fork of something else
 [o]  legal notices (crypto stuff)

	
Python in Stata
===============

This package includes a Stata C plugin and helper files for embedding the Python programming language within Stata. In short, the plugin gives Stata users the ability to use Python to interact with Stata data values, matrices, macros, and numeric scalars. The plugin can be used interactively inside the Stata GUI, or can be used to execute Python files. Python files can be used separately or in combination with Stata .ado or .do files.

Documentation
-------------

The main source of documentation is python_plugin.tex.

Use with caution
----------------
	
The code in this package is experimental. Save your data before using the plugin. There is currently one known limitation/bug which can crash Stata. There may be other, unknown bugs that can crash Stata, too.
	
Known limitations
-----------
	
1. Dropping a Stata program that uses the Python plugin and then re-running it can crash Stata, depending on what Python modules are used in the program, and whether it's the only Stata program that uses the plugin. For many Python modules this is not a problem. Nor does it seem to be a problem to drop and re-run python.ado, even if it's the only program using the plugin.
			
    **Remedy:** It's not clear what is causing this problem, but there seems to be a simple solution. If wanting to drop a program that uses the plugin, make sure that another program also uses it--for example, use python.ado at least once--or declare the plugin in Stata directly, with ``program python_plugin, plugin''.
			
2. The interactive Python interpreter within Stata is limited to single-line inputs. Unfortunately there is no remedy for this at the moment. With some creativity, though, quite a bit of Python code can be packed into a single line, or combinations of single-line inputs. If more than one line of input is needed in a single statement, you can write the code in a Python .py file, and run the file using the file option of python.ado or import it in an interactive session.
			
3. The Stata GUI's Break button does not interrupt the plugin. There is not recourse for infinite loops in the plugin besides closing Stata.
			
4. The plugin does not have continuous access to user input. Python code requiring continuous control over stdin, such as the input() function, will not work.
			
5. Calling ``sys.exit()'' in a Python file will close Stata. In the inetractive interpretor, ``sys.exit()'' may be safely used to exit the plugin, but in a Python file ``sys.exit()'' will close Stata.

Installation
------------

The file INSTALL includes installation instructions for Windows and Mac OS X.

Usage
-----

If the plugin is installed correctly, typing ``python'' should open an interactive session of Python.

The functionality of the plugin comes mainly in the form of "st_" functions that are meant to be analogs of Mata's "st_" functions. For example,

...
. sysuse auto
(1978 Automobile Data)

. list make-head in 1

     +----------------------------------------------+
     | make          price   mpg   rep78   headroom |
     |----------------------------------------------|
  1. | AMC Concord   4,099    22       3        2.5 |
     +----------------------------------------------+

. scalar s = 1234.5

. python
-------------------------------- python (type exit() to exit) ---
. st_numscalar("s")
1234.5

. st_isstrvar(0)
True

. _st_sdata(0, 0)
'AMC Concord'

. st_isnumvar(1)
True

. _st_data(0, 1)
4099.0

. exit()
-----------------------------------------------------------------
...

For more examples and a complete description of the package's functionality, see python_plugin.tex.


License
---------
Copyright (c) 2013, James Fiedler (MIT License)
