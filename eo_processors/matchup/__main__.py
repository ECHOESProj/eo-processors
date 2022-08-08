#!/usr/bin/env python3

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from eo_custom_scripts import ProcessingChain



instrument = 'sentinel2_l1c'
processing_module = 'ndvi_greyscale'
area_wkt = "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))"
start = '2019-01-01'
end = '2019-12-31'
mosaicking_order = 'LEAST_CC'
frequency = 'daily'

pc = ProcessingChain(instrument, processing_module, area_wkt, start, end)

for p in pc:
    print(p)
    break


