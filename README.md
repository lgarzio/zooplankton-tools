# zooplankton-tools
Tools for analyzing zooplankton data.


## Installation Instructions
Add the channel conda-forge to your .condarc. You can find out more about conda-forge from their website: https://conda-forge.org/

`conda config --add channels conda-forge`

Clone the zooplankton-tools repository

`git clone https://github.com/lgarzio/zooplankton-tools.git`

Change your current working directory to the location that you downloaded zooplankton-tools. 

`cd /Users/lgarzio/Documents/repo/zooplankton-tools/`

Create conda environment from the included environment.yml file:

`conda env create -f environment.yml`

Once the environment is done building, activate the environment:

`conda activate zooplankton-tools`

Install the toolbox to the conda environment from the root directory of the data-review-tools toolbox:

`pip install .`

The toolbox should now be installed to your conda environment.

You will also need to install the [broxenaxes package](https://github.com/bendichter/brokenaxes) in the zooplankton-tools environment:

`pip install brokenaxes==0.4.2`


## Folders
- [DE Bay microplastics](https://github.com/lgarzio/zooplankton-tools/tree/master/DE_Bay_microplastics): scripts to analyze and plot zooplankton data for the Delaware Bay microplastics project

- [Raritan Bay 2019](https://github.com/lgarzio/zooplankton-tools/tree/master/RaritanBay2019): figures for the NOAA Raritan Bay Sea Grant project