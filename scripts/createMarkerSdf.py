#!/usr/bin/python3

import os
import cv2
import glob
import time
import shutil
import rospkg
import subprocess
from lxml import etree
from copy import deepcopy
import concurrent.futures

from utilities import ProgressBar


class CreateMarkerSDF:

    def __init__(self, idsList, markerType="aruco", arucoDictNo=7, geometry="box", size=0.09, 
                thickness=0.001, whiteBorderSize=0.01, outputDir="./", createRootDir=True, 
                createTagImgsDir=True, version=1.0, sdfVersion=1.5, author="User"):
        
        self.idsList = idsList
        self.markerType = markerType
        self.maxZeroPadding = len(str(max(idsList)))

        self.modelVersion = version
        self.sdfVersion = sdfVersion
        self.author = author
        
        self.modelGeometry = geometry
        self.whiteBorderSize = whiteBorderSize
        self.borderColor = [255, 255, 255]
        self.modelSize = size + (2.0 * self.whiteBorderSize)
        self.modelThickness = thickness

        self.markerSize = size

        self.modelOutputDir = outputDir
        self.createRootDir = createRootDir
        self.creatTagImgsDir = createTagImgsDir 

        self.markerDirName="alvar_marker_"
        self.modelConfigFilename="model.config"
        self.modelSdfFilename = "model.sdf"
        self.materialFilename = "marker.material"
        self.markerModelName = "ALVAR marker ID-"
        self.textureName = "alvar_marker_id_"
        self.rootDirName = "alvar_markers"
        self.tagImgsDirName = "alvar_marker_images"

        # ArUco specific variables
        self.arucoDictNo = arucoDictNo

        r = rospkg.RosPack()
        self.packagePath = r.get_path("gazebo_alvar_model_generator")
        
        self.modelConfig = etree.parse(os.path.join(self.packagePath, "templates/model.config"))
        self.model = etree.parse(os.path.join(self.packagePath, "templates/model.sdf"))

        with open(os.path.join(self.packagePath, "templates/marker.material"), "r") as modelMaterialScript:
            self.materialScript = modelMaterialScript.read()

    def CreateMarkerModelsInBatches(self, verbose=False): # Create multiple models in threads
        
        print("Creating ALVAR marker SDF models")

        startTime = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futuresCreatedMarkers = {executor.submit(self.CreateMarkerModel, i, self.modelOutputDir): str(i) for i in self.idsList}
            
            creationProgress = ProgressBar(len(self.idsList))
            for future in concurrent.futures.as_completed(futuresCreatedMarkers):
                future.result()
                if verbose is True:
                    print("Created marker model with ID: "+futuresCreatedMarkers[future])
                else:
                    creationProgress.IncrementProgress()
                    creationProgress.DisplayProgressBar()

            creationProgress.ResetProgress()
        endTime = time.time()
        
        print("Models created in: %s" % (endTime-startTime))
        print("SDF models creation completed")

    # This is used for testing purposes
    def CreateMarkerModels(self, verbose=False): # Creates multiple SDF models
        
        print("Creating ALVAR marker SDF models")

        startTime = time.time()
        creationProgress = ProgressBar(len(self.idsList))
        for i in self.idsList:
            self.CreateMarkerModel(i, self.modelOutputDir)
            if verbose is True:
                print("Created marker model with ID: "+str(i))
            else:
                creationProgress.IncrementProgress()
                creationProgress.DisplayProgressBar()
        
        creationProgress.ResetProgress()
        endTime = time.time()

        print("Models created in: %s" % (endTime-startTime))
        print("SDF models creation completed")

    def CreateMarkerModel(self, markerId, outputPath): # Creates a single SDF model

        rootDirPath = "./"
        if self.createRootDir is True: 
            rootDirPath = self.rootDirName # All the models will be put into this directory

        if outputPath is None:
            outputPath = "./" # The directory in which the models should be placed
        
        markerDir = self.markerDirName+str(markerId)
        modelPath = os.path.join(os.path.expanduser(outputPath), rootDirPath, markerDir)

        markerImgsPath = None
        if self.creatTagImgsDir is True: # Create directory for marker images
            markerImgsPath = os.path.join(os.path.expanduser(outputPath), rootDirPath, self.tagImgsDirName)
            if not os.path.exists(markerImgsPath):
                os.makedirs(markerImgsPath)

        materialScriptPath = os.path.join(modelPath, "materials/scripts")
        materialTexturePath = os.path.join(modelPath, "materials/textures")

        os.makedirs(materialScriptPath)
        os.makedirs(materialTexturePath)

        modifiedModelConfig = self.ModifyModelConfig(markerId, self.modelVersion, self.sdfVersion, self.author)
        modifiedModelConfig.write(os.path.join(modelPath, self.modelConfigFilename), pretty_print=True)

        modifiedModel, textureIdName = self.ModifyModelSDF(markerId, markerDir, self.modelGeometry, self.modelSize, self.modelThickness)
        modifiedModel.write(os.path.join(modelPath, self.modelSdfFilename), pretty_print=True)

        textureFilename = self.AddMarkerTexture(markerId, materialTexturePath, markerImgsPath)
        self.ModifyMaterialScript(textureIdName, textureFilename, materialScriptPath)

    def ModifyModelConfig(self, markerId, modelVersion="1.0", sdfVersion="1.5", authorName="User"):

        modelConfig = deepcopy(self.modelConfig) 
        modelConfig.find("name").text = self.markerModelName+str(markerId).zfill(self.maxZeroPadding)
        modelConfig.find("version").text = str(modelVersion)
        modelConfig.find("sdf").set("version", str(sdfVersion))
        modelConfig.find("author").find("name").text = authorName

        return modelConfig
    
    def ModifyModelSDF(self, markerId, markerDir, modelType="box", modelSize=0.09, modelThickness=0.001): # All units are in meters
        
        model = deepcopy(self.model)

        model.getroot().set("version", str(self.sdfVersion))
        model.find("model").set("name", self.markerModelName+str(markerId).zfill(self.maxZeroPadding))

        if modelType == "box":
            model.find("model").find("link").find("pose").text = "0.0 0.0 "+str(modelThickness/2.0)+" 0.0 0.0 0.0"

            box = self.AddBoxGeometry(modelSize, modelSize, modelThickness)
            model.find("model").find("link").find("collision").find("geometry").append(box)
            model.find("model").find("link").find("visual").find("geometry").append(deepcopy(box))

        elif modelType == "plane":
            model.find("model").find("link").find("pose").text = "0.0 0.0 0.0 0.0 0.0 0.0"

            plane = self.AddPlaneGeometry(modelSize, modelSize)
            model.find("model").find("link").find("collision").find("geometry").append(plane)
            model.find("model").find("link").find("visual").find("geometry").append(deepcopy(plane))

        uriScript = etree.Element("uri")
        uriScript.text = "model://"+markerDir+"/materials/scripts/"
        model.find("model").find("link").find("visual").find("material").find("script").append(uriScript)
        
        uriTexture = etree.Element("uri")
        uriTexture.text = "model://"+markerDir+"/materials/textures/"
        model.find("model").find("link").find("visual").find("material").find("script").append(uriTexture)

        textureIdName = self.textureName+str(markerId)
        model.find("model").find("link").find("visual").find("material").find("script").find("name").text = textureIdName

        return model, textureIdName

    def ModifyMaterialScript(self, textureIdName, textureFileName, outputPath):
        
        modifiedScriptStr = self.materialScript.replace("texture_id_name", textureIdName, 1)
        modifiedScriptStr = modifiedScriptStr.replace("texture_file_name", textureFileName, 1)

        with open(os.path.join(outputPath,self.materialFilename), "w") as modifiedScript:
            modifiedScript.write(modifiedScriptStr)

    def AddMarkerTexture(self, markerId, outputPath, imgOutputPath): # All units are in meters

        if self.markerType == "aruco":
            return self.CreateArucoMarkerTexture(markerId, outputPath, imgOutputPath) # Returns the file name of marker image
        elif self.markerType == "alvar":
            return self.CreateALVARMarkerTexture(markerId, outputPath, imgOutputPath)

    def CreateALVARMarkerTexture(self, markerId, outputPath, imgOutputPath):

        # TODO: The performance is rather low for ALVAR markers because of the use of subprocess for marker image creation
        command = ["rosrun", "ar_track_alvar", "createMarker", "-ucm", "-s", str(self.markerSize*100.0), str(markerId)]
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=outputPath)
        popen.wait()

        markerImgPath = glob.glob(os.path.join(outputPath, "*.png"))[0]

        if self.whiteBorderSize > 0.0:
            markerImage = cv2.imread(markerImgPath)
            markerImageBorder = self.AddWhiteBorders(markerImage)
            cv2.imwrite(markerImgPath, markerImageBorder)
        
        if imgOutputPath is not None:
            shutil.copy(markerImgPath, imgOutputPath)
        
        fileName = os.path.basename(markerImgPath) # Only the first file is considered
        
        return fileName

    def CreateArucoMarkerTexture(self, markerId, outputPath, imgOutputPath):
        
        fileName = "marker%d.png" % markerId

        # Convert the marker and border size in meters to pixels
        sizeInPixels = int(2000.0 * (self.markerSize/0.14))

        aruco_dict = cv2.aruco.Dictionary_get(self.arucoDictNo)
        markerImage = cv2.aruco.drawMarker(aruco_dict, markerId, sizeInPixels)

        if self.whiteBorderSize > 0.0:
           markerImage = self.AddWhiteBorders(markerImage)

        cv2.imwrite(os.path.join(outputPath, fileName), markerImage)

        if imgOutputPath is not None: # Used for saving the marker image in a separate directory
            cv2.imwrite(os.path.join(imgOutputPath, fileName), markerImage)

        return fileName

    def AddWhiteBorders(self, image):

        borderSize = int(self.whiteBorderSize * (image.shape[0]/self.markerSize))

        return cv2.copyMakeBorder(image, borderSize, borderSize, borderSize, borderSize, cv2.BORDER_CONSTANT, None, self.borderColor)

    @staticmethod
    def AddBoxGeometry(w, l, h): # All units are in meters
        
        box = etree.Element("box")

        size = etree.Element("size")
        size.text = str(w)+" "+str(l)+" "+str(h)
        
        box.append(size)

        return box

    @staticmethod
    def AddPlaneGeometry(w, l): # All units are in meters
        
        plane = etree.Element("plane")

        normal = etree.Element("normal")
        normal.text = "0 0 1"

        size = etree.Element("size")
        size.text = str(w)+" "+str(l)

        plane.append(normal)
        plane.append(size)

        return plane
