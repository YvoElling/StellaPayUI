# Stella Pay

Stella Pay is the touch-software that is running on touch-display in the Solar Team Eindhoven office at the Eindhoven University of Technology in the building Momentum. It has been developed in Python, using Kivy and KivyMD for the graphical parts of the code. The server has been developed in Django, which is also a Python library. 

For more documentation regarding the application, see the wiki.

For support:  
Stella Pay application, NFC reader, touchscreen:  Yvo.elling@solarteameindhoven.nl  
Stella Pay backend, administrator rights: Vincent.bolta@solarteameindhoven.nl

NFC reader software and documentation  
https://github.com/YvoElling/PythonNFCReader


-------------------
# General installation instructions
To get started with this repo, clone it and update the submodules by performing `git submodule update --init --recursive`. Next, go to [this](https://github.com/YvoElling/PythonNFCReader) submodule and follow the instructions there.

This project was built and tested on a Raspberry Pi 4 Model B, although it can be run on any other system (I presume). Since this project uses Kivy and KivyMD, make sure to install those as well.
Install instructions can be found [here](https://kivy.org/doc/stable/installation/installation-linux.html) for Kivy and [here](https://kivymd.readthedocs.io/en/latest/getting-started/) for KivyMD.

-----------
# Read on
If you came this far you probably want to use this system. Head over to the wiki to see more detailed info about the actual usage of the system.
