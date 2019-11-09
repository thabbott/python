import xarray as xr
import os
import glob
import numpy as np

def open_mfdataset(data_dir, inp_dir, casename, prefix = None,
    timestep = 'all', **kwargs):
    """
    Open 3D SAM output as an xarray dataset

    Parameters
    ----------
    data_dir : string
        Path to the data directory
    inp_dir : string
        Path to directory with input files.
    casename : string
        Subdirectory within data_dir and inp_dir where NetCDF and input files, respectively, are stored.
    prefix : string, optional
        NetCDF file prefix. If provided, files with names given by
        ['%s_%010d.nc' % (prefix, ts) for ts in timestep] will be loaded; otherwise, the prefix will be determined automatically.
    timestep : list, optional
        List of timesteps to load. If ``all'' (default), all timesteps will be read; if ``none'', no timesteps will be read (but output metadata will still be loaded)
    **kwargs : optional
        Additional arguments passed on to xarray.open_mfdataset

    Returns
    -------
    dset : xarray.Dataset
        Dataset object containing coordinates, variables, and grid metadata
    """

    # Determine file prefix
    if prefix is None:
        files = glob.glob(
            os.path.join(data_dir, casename, '*.nc'))
        prefix = os.path.basename(
            '_'.join(files[0].split('_')[:-1]))
        for f in files[1:]:
            if not os.path.basename(
                '_'.join(f.split('_')[:-1])) == prefix:
                raise ValueError('Auto-detected multiple file prefixes')

    # Construct list of files
    if type(timestep) is list:
        files = [os.path.join(data_dir, 
            casename, 
            '%s_%010d.nc' % (prefix, ts)) for ts in timesteps]
    elif timestep == 'all':
        files = glob.glob(os.path.join(data_dir,
            casename, '%s_*.nc' % prefix))
    elif timestep == 'none':
        files = []

    # Open files
    dset = xr.open_mfdataset(files, **kwargs)

    # Add file locations as attributes
    dset.attrs['data_dir'] = data_dir
    dset.attrs['inp_dir'] = inp_dir
    dset.attrs['casename'] = casename

    # Add new grid metadata
    try:
        _add_zi(dset)
    except KeyError:
        print('Failed to add interface heights')

    # Return Dataset
    return dset

def _add_zi(dset):
    """
    Compute interface heights and add them to the dataset
    as a new coordinate

    Parameters
    ----------
    dset : xarray.Dataset
        Dataset for which to calculate interface heights.
    """
    # Extract levels at cell centers
    zc = np.array(dset['z'])

    # Calculate interface heights -- based on setgrid.f90
    z = np.zeros((zc.size+1,))
    z[:-1] = zc
    z[-1] = z[-2] + (z[-2] - z[-3])
    adzw = np.zeros((z.size,))
    dz = 0.5*(z[0] + z[1])
    adzw[0] = 1.0
    adzw[1:-1] = (z[1:-1] - z[0:-2])/dz
    adzw[-1] = adzw[-2]
    adz = np.zeros((z.size-1,))
    adz[0] = 1.0
    adz[1:-1] = 0.5*(z[2:-1] - z[0:-3])/dz
    adz[-1] = adzw[-2]
    zi = np.zeros((z.size,))
    zi[0] = 0.0
    for ii in range(1,zi.size):
        zi[ii] = zi[ii-1] + adz[ii-1]*dz

    # Add data to dataset
    dset.coords['zi'] = zi
    dz = np.diff(zi)
    dset['dz'] = xr.DataArray(dz, dims = 'z',
        coords = {'z': dset.coords['z']})


if __name__ == '__main__':
    dset = open_3d('..\\scratch\\OUT_3D', '..\\home', 
        'CWTG_SST300_NC100')
    print(dset)
    print(dset['W'])
