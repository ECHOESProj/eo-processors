# NDVI using Sentinel-2

This processor computes the NDVI from the Sentinel-2 SAFE files
stored in the CREODIAS object store.

## Usage

    docker run eo-processors ndvi_satpy S2_MSI_L1C "POLYGON((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90

