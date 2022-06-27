#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from os.path import dirname
from satpy import Scene, find_files_and_readers
from shapely import wkt
from eoian import ProcessingChain, utils
import click


def main(input_file: str, area_wkt: str) -> "Dataset":
    files = find_files_and_readers(base_dir=dirname(input_file), reader='msi_safe')
    scn = Scene(filenames=files)
    scn.load(['B04', 'B08'])
    area = wkt.loads(area_wkt)

    epsg = scn['B04'].area.crs.to_epsg()
    xy_bbox = utils.get_bounds(area, epsg)
    scn = scn.crop(xy_bbox=xy_bbox)

    extents = scn.finest_area().area_extent_ll
    ad = utils.area_def(extents, 0.0001)
    s = scn.resample(ad)

    ndvi = (s['B08'] - s['B04']) / (s['B08'] + s['B04'])
    s['ndvi'] = ndvi
    s['ndvi'].attrs['area'] = s['B08'].attrs['area']
    del s['B04']
    del s['B08']
    return s


@click.command()
@click.argument('instrument')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('stop')
@click.option('--cloud_cover', default=None)
@click.option('--graph_path', default=None)
def cli(instrument: str, area_wkt: str, start: str, stop: str, cloud_cover, graph_path) -> None:
    """

    :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    :param processing_module: The processor to use.
    :param area_wkt: The WKT string, which is the polygon of the ROI
    :param start: The start date of the search in the format YYYY-MM-DD
    :param stop: The stop date of the search in the format YYYY-MM-DD
    :param cloud_cover: Threshold for allowed cloud cover
    :return:
    """
    click.echo()
    processing_chain = ProcessingChain(instrument, main, area_wkt, start, stop,
                                       cloud_cover=cloud_cover, graph_path=graph_path)
    for d in processing_chain:
        d.to_tiff()
        d.metadata_to_json()
        # d.to_zarr()


if __name__ == '__main__':
    cli()
