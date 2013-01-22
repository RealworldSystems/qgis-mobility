from qgis_mobility.generator.standalone_toolchain import StandaloneToolchain
from qgis_mobility.generator.bzip2_builder import BZip2Builder
from qgis_mobility.generator.libiconv_builder import LibiconvBuilder
from qgis_mobility.generator.freexl_builder import FreeXLBuilder
from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder
from qgis_mobility.generator.spatialite_builder import SpatialiteBuilder
from qgis_mobility.generator.expat_builder import ExpatBuilder
from qgis_mobility.generator.gdal_builder import GDALBuilder
from qgis_mobility.generator.gsl_builder import GSLBuilder
from qgis_mobility.generator.qwt_builder import QWTBuilder
from qgis_mobility.generator.spatialindex_builder import SpatialindexBuilder
from qgis_mobility.generator.python_builder import PythonBuilder
from qgis_mobility.generator.qgis_builder import QGisBuilder
from qgis_mobility.generator.sip_builder import SipBuilder

class Recipe(object):
    def __init__(self, recon):
        self._recon = recon

    def make(self):
        recon = self._recon
        StandaloneToolchain(recon).make()
        BZip2Builder(recon).make()
        LibiconvBuilder(recon).make()
        FreeXLBuilder(recon).make()
        SQLiteBuilder(recon).make()
        GeosBuilder(recon).make()
        Proj4Builder(recon).make()
        SpatialiteBuilder(recon).make()
        ExpatBuilder(recon).make()
        GDALBuilder(recon).make()
        GSLBuilder(recon).make()
        QWTBuilder(recon).make()
        SpatialindexBuilder(recon).make()
        QGisBuilder(recon).make()
        PythonBuilder(recon).make()
        SipBuilder(recon).make()
