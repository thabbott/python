import xarray as xr
import os
import glob
import numpy as np

def open_mfdataset(paths, **kwargs):
    """
    Wrapper for xarray.open_mfdataset

    Parameters
    ----------
    paths : str or sequence
        Files to open (see documentation for xarray.open_mfdataset)
    **kwargs : optional
        Additional keyword arguments for xarray.open_mfdataset
        
    Returns
    -------
    dset : xarray.Dataset
        Dataset object containing coordinates, variables, and grid metadata
    """

    # Open files
    dset = xr.open_mfdataset(paths, **kwargs)

    # Add horizontal grid vertex locations
    try:
        _add_v(dset)
    except KeyError:
        print('Failed to add vertices. lat and lon may be missing.')

    # Return Dataset
    return dset

def _add_v(dset):
    """
    Compute corner vertices for horizontal grid and add them as
    new coordinates

    Parameters
    ----------
    dset : xarray.Dataset
        Dataset to add corner vertices to
    """
    # Extract latitude and longitude at cell centers
    xc = np.array(dset['lon'])
    yc = np.array(dset['lat'])

    # Calculate corner locations
    xv = np.zeros((xc.size+1,))
    yv = np.zeros((yc.size+1,))
    xv[0] = 0.0
    xv[-1] = 360.0
    xv[1:-1] = 0.5*(xc[1:] + xc[:-1])
    yv[0] = -90.0
    yv[-1] = 90.0
    yv[1:-1] = 0.5*(yc[1:] + yc[:-1])

    # Add data to dataset
    dset.coords['xv'] = xv
    dset.coords['yv'] = yv
