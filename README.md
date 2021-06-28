windmills
=========

This project is an attempt to create a library that will make it easy to construct managed messaging patterns based on 0mq.



Documentation
--------------

For the latest documentation, visit http://neoinsanity.github.io/windmills/

====================
Project Development
====================

If you are interested in developing **Windmills** code, utilize the helper 
scripts in the *windmills/bin* directory. Just follow the instruction below 
for setting up the 

Get the Source First!
----------------------

The latest stable release source of **Windmills** can be found on the
at https://github.com/neoinsanity/windmills. 

Run the Dev Environment Setup
------------------------------

Prior to running the dev setup scripts:

    1. Ensure that *python3* is installed. You can check by using the command:
    
        python3 --version
    
    2. Ensure that you have *virtualenv* installed. You can check by using the
     command:
     
        virtualenv --version
    
Keep in mind that all scripts to be executed are assumed to be from the 
project `root` directory. This is the directory with the *setup.py* file.

Once you have the pre-requisites out of the way, we can run the development 
configuration scripts.


Prep the development environment with the command:

  > bin/dev_setup.sh

This command will setup the virtualenv for the project in the  directory 
*/venv*. It will also install the **Windmills** in a develop mode,  with the
creation of a development egg file.

The Development Environment Usage
==================================

In this section will be demonstrated the dev tools available for a session of
source development. This features enabling the dev environment, executing the
unit test with coverage, and building the docs.

Enable the Development Environment
-----------------------------------

This command MUST be executed at the beginning of each developer session. It 
will ensure that the dev tools are available, and that the virtual 
environment is active.

The command is given below, note that it is sourced to set virtualenv:

  > . bin/enable_dev.sh
  
or

  > source bin/enable_dev.sh
  
Enabling the dev environment adds the *bin* directory scripts to environment 
*PATH*. This allows for the commands below to be typed at the prompt from the
project <root>. 

Running Tests and Code Coverage
--------------------------------

To run the unit tests:

  > run_tests.sh

To view the code coverage report, open the file 
`root`/BUILD/CONVERAGE_REPORT/index.html.

Building Documentation
-----------------------

To run the documentation generation:

  > doc_build.sh

To view the documentation, open the file `root`/BUILD/doc/index.html.