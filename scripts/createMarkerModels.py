#!/usr/bin/python3

import argparse

from createMarkerSdf import CreateMarkerSDF
from utilities import ParseNumList

parser = argparse.ArgumentParser()

# Common arguments
parser.add_argument("-i", "--ids", type=ParseNumList, action="store", dest="ids", help="Required marker IDs in the form '2', '1-5' or '10,12,15'. Maximum number depends on marker type")
parser.add_argument("-mt", "--marker_type", action="store", dest="markerType", default="aruco", choices=["aruco", "alvar"], help="The type of marker to be generated for creating the SDF models")
parser.add_argument("-d" "--dictionary", type=int, action="store", dest="dictionary", default=7, help="The dictionary to use for creating markers if ArUco is selected")
parser.add_argument("-g", "--geometry", action="store", dest="geometry", default="box", choices=["box", "plane"], help="Geometry of the marker model")
parser.add_argument("-s", "--size", type=float, action="store", dest="size", default=9.0, help="Length and width of the box or plane in cm")
parser.add_argument("-t", "--thickness", type=float, action="store", dest="thickness", default=0.1, help="Thickness of box if it is used as model geometry in cm")
parser.add_argument("-wb", "--white_border_size", type=float, action="store", dest="whiteBorderSize", default=0.0, help="White border to be applied around the marker image in cm")
parser.add_argument("-o", "--output_dir", action="store", dest="outputDir", default="./", help="Directory where the models are saved to. Defaults to current working directory")
parser.add_argument("-nrd", "--no_root_dir", action="store_false", dest="createRootDir", default=True, help="Do not create a root directory for the models to be saved in")
parser.add_argument("-cti", "--copy_tag_images", action="store_true", dest="createTagImgDir", default=False, help="Copies the tag images used for model creation to a separate directory")
parser.add_argument("-mdv", "--model_version", type=float, action="store", dest="version", default=1.0, help="Model version number")
parser.add_argument("-sdfv", "--sdf_version", type=float, action="store", dest="sdfVersion", default=1.5, help="SDF version number")
parser.add_argument("-a", "--author", action="store", dest="author", default="User", help="Name of the author for the model")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose output during model creation")


if __name__ == '__main__':
    
    arg = parser.parse_args()

    modelCreator = CreateMarkerSDF(idsList=arg.ids, markerType=arg.markerType, arucoDictNo=arg.dictionary,
                                   geometry=arg.geometry, size=(arg.size/100.0), 
                                   thickness=(arg.thickness/100.0), whiteBorderSize=(arg.whiteBorderSize/100.0),
                                   outputDir=arg.outputDir, createRootDir=arg.createRootDir, 
                                   createTagImgsDir=arg.createTagImgDir, version=arg.version, 
                                   sdfVersion=arg.sdfVersion, author=arg.author)
    
    modelCreator.CreateMarkerModelsInBatches(verbose=arg.verbose)