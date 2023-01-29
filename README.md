# SpatialTree

Yet another 3D mapped christmass tree using DepthAI camera, Matlab and Python.  

`Capture.m` - main Matlab file used for calculating point cloud

`opencv/capture.py` - data gathering and preprocessing Python script

## Usage

`pip -r requirements`

`python3 opencv/capture.py`

This shoud generate `capture.mat` file to be loaded by the `Capture.m` script.
