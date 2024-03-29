# **Gazebo Fiducial Generator**
A ROS package that can be used to generate SDF models for fiducial markers. This is more of a helper package to create large amount of SDF marker models with relative ease which can be used in robotic simulation software like Gazebo.

## Dependencies

The following software dependencies must me met before using this package.

- `shuitils` via PyPi
- `lxml` via PyPi
- `opencv-python` via PyPi
- `opencv-contrib-python` via PyPi
- `ar_track_alvar` via ROS

## Installations

Change directory into `~/catkin_ws/src/gazebo_fiducial_generator` and run the following commands to setup the package and create SDF models. First install the required Python packages.

```bash
pip3 install -r requirements.txt
```

#### **For ArUco markers**
ArUco marker creator comes packaged with OpenCV
#### **For ALVAR markers**
The final step is to install `ar_track_alvar` package which is found [here][ARTrackALVAR]. This package contains the `createMarker` binary which is used by this package to create the marker models.

```bash
sudo apt install ros-<distribution>-ar-track-alvar
```
**Please note that this is only tested with Melodic Morenia**
## Usage

To create the SDF models, there are multiple methods. But first, the marker type needs to be selected using `--marker_type` option. By default `aruco` is used. For other marker types use `--help`. 

```bash
# To create a single model of an ALVAR marker 
rosrun gazebo_fiducial_generator createMarkerModels.py --marker_type alvar --ids 0

# To create a range of marker models with IDs from 0 to 5
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5

# To create a list of markers models whose IDs are discontinous
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 2,3,5,7,11,13
```

This will create a root directory called `<marker_type>_markers` which will contain folders of the SDF marker models that were specified. The root directory which contains all the models is by default created in the current working directory.

If the models needs to be created without a root directory, the `--no_root_dir` option can be used. If it is required to put the models in a different director other than the current working directory, the `--output_dir` option can be used. Both of these options are useful if the marker models needs to be placed in the default Gazebo models folder. This is usally located in `~/.gazebo/models/`.

```bash
# To create the models in Gazebo's default models directory
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5 --no_root_dir --output_dir ~/.gazebo/models/
```

By default, the geometry of the model is a box with sides 9.0cm and thickness 0.1cm. When the size of the sides of the box is set to a value, the same size is used to create the fiducial marker. The geometry of the model can be set to either `box` or `plane` using the `--geometry` option. An example of this is given below. Size and thickness inputs are in centimeters.

```bash
# To create marker models with box geometry, size 11.0cm and thickness 0.2cm
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5 --geometry box --size 11.0 --thickness 0.2

# To create marker models with plane geometry, size 10.0cm (Thickness is not required)
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5 --geometry plane --size 10.0
```

If a white border needs to be added around the marker, the size of it can be specified using the `--white_border_size` option. The size of the model will
be automatically adjusted to accomodate the border while keeping the specified tag size.

```bash
# To create tag models with a white border of size 2.0cm
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5 --size 9.0 --thickness 0.01 --white_border_size 2.0
```

To get all the marker images that were used when creating the SDF model in a separate directory, the `--copy_tag_images` option can be used. This will create a directory called `<marker_type>_tag_images` in the root directory `<marker_type>_markers`, if it is enabled otherwise it will be created in the working directory.

```bash
# To copy the marker images used for model creation
rosrun gazebo_fiducial_generator createMarkerModels.py --ids 0-5 --copy_tag_images
```

Other options are also available and can be viewed by using the `--help` option.

```bash
rosrun gazebo_fiducial_generator createMarkerModels.py -h

usage: createMarkerModels.py [-h] [-i IDS] [-mt {aruco,alvar}] [-g {box,plane}] [-s SIZE] [-t THICKNESS] [-wb WHITEBORDERSIZE] [-o OUTPUTDIR] [-nrd] [-cti] [-mdv VERSION] [-sdfv SDFVERSION] [-a AUTHOR] [-v] [-d DICTIONARY]

optional arguments:
  -h, --help            show this help message and exit
  -i IDS, --ids IDS     Required marker IDs in the form '2', '1-5' or '10,12,15'. Maximum number depends on marker type
  -mt {aruco,alvar}, --marker_type {aruco,alvar}
                        The type of marker to be generated for creating the SDF models
  -g {box,plane}, --geometry {box,plane}
                        Geometry of the marker model
  -s SIZE, --size SIZE  Length and width of the box or plane in cm
  -t THICKNESS, --thickness THICKNESS
                        Thickness of box if it is used as model geometry in cm
  -wb WHITEBORDERSIZE, --white_border_size WHITEBORDERSIZE
                        White border to be applied around the marker image in cm
  -o OUTPUTDIR, --output_dir OUTPUTDIR
                        Directory where the models are saved to. Defaults to current working directory
  -nrd, --no_root_dir   Do not create a root directory for the models to be saved in
  -cti, --copy_tag_images
                        Copies the tag images used for model creation to a separate directory
  -mdv VERSION, --model_version VERSION
                        Model version number
  -sdfv SDFVERSION, --sdf_version SDFVERSION
                        SDF version number
  -a AUTHOR, --author AUTHOR
                        Name of the author for the model
  -v, --verbose         Verbose output during model creation

ArUco marker specific arguments:
  -d DICTIONARY, --dictionary DICTIONARY
                        The dictionary to use for creating markers if ArUco is selected

```

The marker models can be inserted into Gazebo by adding the folder path to the models in the insert tab. A marker model in Gazebo simulation is shown below. To add the marker models in a custom path, the `GAZEBO_MODEL_PATH` environment variable needs to be set to the correct path in either the `~/.bashrc` file or roslaunch file using the `<env>` tag when launching Gazebo.

<p align="center">
<img src=./images/tag_on_floor.png alt="Tag" width="640">
</p>


<p align="center">
<img src=./images/tag_static_floating.png alt="Tag" width="640">
</p>


[ARTrackALVAR]:http://wiki.ros.org/ar_track_alvar