
#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import pickle
from os.path import dirname

import dask
import numpy as np
import xarray as xr
from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery
from scipy import fftpack
from sklearn.decomposition import IncrementalPCA, PCA
# import geopandas as gpd
from eoian import command_line_interface
import pylab as plt

sub_size = 256
Ncomps = 64


# df_europe = gpd.read_file("eoian/data/europe_coastline/Europe_coastline_poly.shp")
# df_europe.intersection(b).area.sum() / shape(b).area


import click
from eoian import ProcessingChain


def process(input_file, area):
    files = find_files_and_readers(base_dir=dirname(input_file), reader='sar-c_safe')
    scn = Scene(filenames=files)
    hh_id = DataQuery(name="measurement", polarization="vv")
    lat_id = DataQuery(name='latitude', polarization='vv')
    lon_id = DataQuery(name='longitude', polarization='vv')
    scn.load([hh_id, lat_id, lon_id])
    ds = scn.to_xarray_dataset()
    ds['latitude'] = scn['latitude']
    ds['longitude'] = scn['longitude']
    return ds


@click.command()
@click.argument('instrument')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('stop')
@click.option('--cloud_cover', default=None)
@click.option('--graph_path', default=None)
def cli(instrument: str, area_wkt: str, start: str, stop: str, cloud_cover, graph_path) -> None:
    # :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    # :param processing_module: The processor to use
    # :param area_wkt: The WKT string, which is the polygon of the ROI
    # :param start: The start date of the search in the format YYYY-MM-DD
    # :param stop: The stop date of the search in the format YYYY-MM-DD
    # :param cloud_cover: Threshold for allowed cloud cover
    # :return:
    click.echo()
    processing_chain = ProcessingChain(instrument, area_wkt, start, stop,
                                       cloud_cover=cloud_cover, graph_path=graph_path)
    for data_obj in processing_chain:
        res = process(data_obj.source_product_path, area_wkt)
        plt.imshow(np.log10(res.dataset['measurement']))
        plt.show()
        break
        
        # d.to_tiff()
        # d.metadata_to_json()

    return d


if __name__ == '__main__':
    d = cli()
