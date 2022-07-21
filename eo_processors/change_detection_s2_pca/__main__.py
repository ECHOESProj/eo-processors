#!/usr/bin/env python3

from os import environ
import xarray as xr
import numpy as np
# from matplotlib import pyplot as plt
from xcube_sh.observers import Observers
from xcube_sh.config import CubeConfig
from zarr.errors import GroupNotFoundError
from xcube_sh.cube import open_cube
import eo_io
from sklearn.decomposition import SparsePCA
from sklearn.preprocessing import StandardScaler
import click
from shapely import wkt
from sentinelhub import CRS, BBox
from os.path import join
from dataclasses import dataclass

import time

MAX_ITER = 5


def get_cloud_free(time_range, band_names, bbox, spatial_res):
    cube_config = CubeConfig(dataset_name='S2L2A',
                             band_names=band_names,
                             # tile_size=[512, 512],
                             bbox=bbox,
                             spatial_res=spatial_res,
                             time_range=time_range,
                             time_period='1D')

    request_collector = Observers.request_collector()

    cube = open_cube(cube_config, observer=request_collector)

    filt = np.logical_not(np.isnan(cube['B02']).all(dim=('lon', 'lat')))
    cube = cube.where(filt, drop=True)
    cube = cube.where(np.logical_not(cube.CLM))
    cube = cube.mean(dim='time')
    return cube


def get_dataset(d1, d2, band_names, bbox, spatial_res):
    time_range = [d1, d1]
    ds_a = get_cloud_free(time_range, band_names, bbox, spatial_res)
    time_range = [d2, d2]
    ds_b = get_cloud_free(time_range, band_names, bbox, spatial_res)
    return xr.concat([ds_a, ds_b], dim='time')


# def rescale(X):
#     X = X.where(np.isfinite(X))
#     Xmax = X.max() * 0.8
#     Xmin = X.min() * 1.2
#     return ((X - Xmin) * (1 / (Xmax - Xmin) * 1))
#
#
# def rescale(X):
#     return 4 * X
#
#
# def plot_source_data(ds):
#     for t, ds0 in ds.groupby('time'):
#         r, g, b = 'B04', 'B03', 'B02'
#         cube_rgb = xr.concat([rescale(ds0[r]), rescale(ds0[g]), rescale(ds0[b])], 'band')
#         cube_rgb.rio.to_raster(f"/tmp/{t}.tif")
#         cube_rgb.plot.imshow(rgb='band', figsize=(15, 15))
#         plt.show()


def get_components(ds):
    components = []
    t0 = time.time()
    for v in ds.isel(time=0).variables:
        print(v)
        if not v.startswith('B'):
            continue
        da_z = ds[v].fillna(0).stack(z=('lon', 'lat')).compute()

        pca = SparsePCA(alpha=.1, max_iter=MAX_ITER, method='lars', n_jobs=-1)
        #     pca = PCA()
        weights = pca.fit_transform(da_z.isel(time=[0, 1]).T)

        da_z = xr.DataArray(weights, dims=da_z.dims).compute()
        components.append(da_z.compute())

    components = np.array(components)
    tend = time.time()
    print(f"{tend - t0=}")
    return pca, components


def weights_of_diff_pca(corr_diff, components, pca):
    pca_comp_weights = components[:, :, corr_diff].T
    scaler = StandardScaler()
    pca_comp_weights = scaler.fit_transform(pca_comp_weights)
    return pca, pca_comp_weights  # / np.sqrt((pca_comp_weights**2).sum(axis=0))


def norm(x):
    return x / np.sqrt((x ** 2).sum())


def main(area_wkt, date1, date2):
    area = wkt.loads(area_wkt)
    bbox = BBox(bbox=area.bounds, crs=CRS.WGS84)

    band_nums = list(range(2, 9))
    # band_nums.remove(9)
    # band_nums.remove(10)
    band_names = [f'B0{i}' for i in band_nums if i != 9] + ['B8A', 'CLM', 'SCL']
    # band_names = [f'B0{i}' for i in band_nums[:1] if i != 9] + ['B8A', 'CLM', 'SCL']

    spatial_res = 1 * 0.00018  # = 10.038 meters in degrees

    ds = get_dataset(date1, date2, band_names, bbox, spatial_res)

    t1 = time.time()
    pca, components = get_components(ds)
    t2 = time.time()
    print(f"{t2 - t1=}")

    pca0, pca_comp_weights0 = weights_of_diff_pca(0, components, pca)
    pca1, pca_comp_weights1 = weights_of_diff_pca(1, components, pca)

    da_weights0 = xr.DataArray(pca_comp_weights0, dims=('z', 'band'))
    da_weights1 = xr.DataArray(pca_comp_weights1, dims=('z', 'band'))

    ds_diff = xr.Dataset(data_vars=dict(weights0=da_weights0, weights1=da_weights1))
    change = np.sqrt((ds_diff['weights1'] ** 2).sum(axis=1)).values.reshape(len(ds.lon), len(ds.lat)).T
    return xr.DataArray(change, dims=('lat', 'lon'), coords=ds.coords, name='change').to_dataset()


@dataclass
class Metadata(eo_io.store_dataset.BaseMetadata):
    area_wkt: str
    name: str
    platform: str
    instrument: str
    processingLevel: str
    date1: str
    date2: str

    def get_path(self):
        return join(self.area_wkt, self.name, self.platform, self.instrument, self.processingLevel,
                    f'{self.date1}_{self.date2}')


@click.command()
@click.argument('area_wkt')
@click.argument('date1')
@click.argument('date2')
def cli(area_wkt: str, date1: str, date2: str) -> None:
    """
    """

    change = main(area_wkt, date1, date2)
    metadata = Metadata(area_wkt, 'change', 'sentinel2', 'msi', 'S2L2A', date1, date2)
    store = eo_io.store_dataset.store(change, metadata)
    store.to_tiff()


if __name__ == '__main__':
    cli()
