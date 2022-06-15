## Setting up a Conda Virtual Environment 

A virtual environment is a named, isolated, working copy of Python that maintains its own files, directories, and paths so that you can work with specific versions of libraries or Python itself without affecting other Python projects. Virtual environments make it easy to cleanly separate different projects and avoid problems with different dependencies and version requirements across components. 

The conda command is the preferred interface for managing installations and virtual environments with the Anaconda Python distribution. 



1. Check conda is installed and in your PATH
    - Open a terminal client
    - Windows power shell with admin rights
    - VSCode - Terminal
    - Spyder - Terminal
    - MacBook - Terminal
    - Linux - Terminal

2. Enter  conda -V into the terminal command line and press enter to see whether conda is installed. If conda is installed you should be able to see the version of the conda. 

* If you already have Anaconda installed, update the version of the conda by following instructions based on your operating system.


* If you do not have Anaconda installed on your machine please follow the instructions from [this page](https://docs.anaconda.com/anaconda/install/) based on your operating system.

3. Create virtual environment for NeuroCausal

* In the terminal client (either Anaconda prompt, VSCode terminal or Windows Powershell) enter the following where your envname is the name you want to call your environment and replace 3.10 with the Python version you wish to use.

**(To see a list of available python versions first type conda search ``"^python$"`` and press enter.)**


`conda  create -n envname python=3.10`

* Press y to proceed. To be able to see whether your environment created please type 

`conda  env list`

* Now you will be able to see your environment created with the Python version you requested and all the associated anaconda packaged libraries at 

`path_to_your_anaconda_location/anaconda/envs/envname`

4. To activate or switch into your virtual environment, simply type the following where envname is the name you gave to your environment at creation.

In Anaconda prompt type 

`conda activate env_name`


In windows terminal type 
`conda activate env_name`


In Linux or MacBook type 
`source activate env_name`


* Activating a conda environment modifies the PATH and shell variables to point to the specific isolated Python set-up you created. 

* The command prompt will change to indicate which conda environment you are currently in by prepending (envname). To see a list of all your environments, use the command conda info -e.

5. To deactivate the environment and change back to the default environment which is the base environment use the command 

`conda deactivate`

6. To remove your environment later on

`conda envname remove`



Adapted from [University of Auckland Center for eResearch Resources](https://github.com/UoA-eResearch)