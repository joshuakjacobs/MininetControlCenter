# MininetControlCenter
Extension application for Mininet. Designed for the MEng thesis "Software Defined Networking Emulation" - April 2015, University of Bristol

The prerequisites for the project application, named the “Mininet Control Center”, are as follows:

      •	Mininet (version 2.2.0) with LXDE desktop environment
      •	Hypervisor software (VirtualBox or VMware Fusion)
      •	Ryu
      •	OpenvSwitch (version 2.3.1)

The installation instructions for VirtualBox and Mininet are not provided in this appendix - a reference and link to the installation guide for both has been provided in the thesis. VirtualBox can be tricky to set up correctly, as it has several quirks related to X11 port forwarding. Logging in and out of the VM is found to solve some issues if the MCC begins giving odd errors; this is not a problem with the MCC. It is left to the user to ensure that both VirtualBox and Mininet are set up and working correctly before trying to run anything else. Failing which, the Mininet Control Center has been tested to work perfectly on VMware Fusion - a more user-friendly (but not free) hypervisor.

In terms of Ryu and Openswitch, as there are several methods of installing them, this section lists the method used by the student. This setup should be followed to avoid anomalies. An older version of OpenvSwitch comes included with Mininet, these instructions update them to the version used, i.e. 2.3.1. LXDE is a lightweight desktop environment, required to gain the use of the Chromium browser, which in turn will be used for the topology viewer module. 

Ryu and OpenvSwitch can be directly installed using the Mininet install script as of Mininet 2.2.0, while LXDE can be installed with use of Linux’s ‘apt-get’. The following commands should be entered in the CLI:

      •	sudo apt-get update		[updates Linux dependencies]
      •	cd mininet/util
      •	sudo ./install.sh -V 2.3.1  	[installs OpenvSwitch version 2.3.1]
      •	sudo ./install.sh -y 		[installs Ryu]
      •	sudo apt-get install xinit lxde	[installs LXDE desktop environment]

The Mininet Control Center source files come in a folder on a CD provided with the printed version of this thesis. Simply copy the folder named “MininetControlCenter” into the home directory of Mininet (~/home/mininet).

An alternative method is cloning the folder directly from the online repository hosting it. The link to the repository has been provided in the references [41]. To clone the repository, the following commands should be entered in the Mininet CLI:

    •	cd  
    •	git clone https://github.com/joshuakjacobs/MininetControlCenter.git

Both these methods achieve the same aim. The installation procedure only requires the bash script “cleaner.sh” to be run, using the command below:
    
    •	sudo ./cleaner.sh

The script makes small modification to the Ryu GUI topology module to enable the Mininet Control Center to use it. The rest of the files are Python scripts, so they do not require installation.

Note: It is important that the source files must be extracted to a folder in the HOME DIRECTORY (~/home/mininet) named “MininetControlCenter”. 

The commands below show how to start the Mininet Control Center from the home directory of Mininet.

    •	cd MininetControlCenter
    •	sudo ./controlcenterMain.py

The application will then start. 

This concludes the installation guide for the project application (Mininet Control Center), as well as Ryu, OpenvSwitch and LXDE.
