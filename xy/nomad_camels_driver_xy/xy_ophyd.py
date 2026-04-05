#NOMAD INTERNAL CLASS "Xy", describing the nomad driver and its channels and configurations
#The class uses instances of the backend classes for stage, head and sample

from ophyd import Component as Cpt
from nomad_camels.bluesky_handling.custom_function_signal import Custom_Function_Signal, Custom_Function_SignalRO
from ophyd import Device
from pathlib import Path
import sys

#importing helper-packages:
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import xyz_stage
import procedure
import head_control

statusfile = "state.csv" #file where the hardware state (volume of pump..) is stored

#nomad driver class "Xy"
class Xy(Device):

	#----------------------------------------------------------------------------------------------#
	#-----------CHANNELS AND CONFIG----------------------------------------------------------------#
	#----------------------------------------------------------------------------------------------#

	#stage-read-channels:
	home = Cpt(Custom_Function_SignalRO, name="home", metadata={"units": "", "description": ""})
	shed_drop = Cpt(Custom_Function_SignalRO, name="shed_drop", metadata={"units": "", "description": ""})
	finish_move = Cpt(Custom_Function_SignalRO, name="finish_move", metadata={"units": "", "description": ""})
	parking = Cpt(Custom_Function_SignalRO, name="parking", metadata={"units": "", "description": ""})
	testmove = Cpt(Custom_Function_SignalRO, name="testmove", metadata={"units": "", "description": ""})

	#stage-set-channels:
	positionxy = Cpt(Custom_Function_Signal, name="positionxy", metadata={"units": "", "description": ""}) #do not name it "position" because that is for some reason forbidden in camels
	position_param = Cpt(Custom_Function_Signal, name="position_param", metadata={"units": "", "description": ""}) #do not name it "position" because that is for some reason forbidden in camels
	position_sample = Cpt(Custom_Function_Signal, name="position_sample", metadata={"units": "", "description": ""}) #do not name it "position" because that is for some reason forbidden in camels
	position_drop = Cpt(Custom_Function_Signal, name="position_drop", metadata={"units": "", "description": ""}) #do not name it "position" because that is for some reason forbidden in camels
	height = Cpt(Custom_Function_Signal, name="height", metadata={"units": "", "description": ""})
	height_param = Cpt(Custom_Function_Signal, name="height_param", metadata={"units": "", "description": ""})
	command = Cpt(Custom_Function_Signal, name="command", metadata={"units": "", "description": ""})

	#head-read-channels:
	volume_zero = Cpt(Custom_Function_SignalRO, name="volume_zero", metadata={"units": "", "description": ""})

	#head-set-channels:
	purge_head = Cpt(Custom_Function_Signal, name="purge_head", metadata={"units": "", "description": ""})
	purge_head_param = Cpt(Custom_Function_Signal, name="purge_head_param", metadata={"units": "", "description": ""})
	fill_head = Cpt(Custom_Function_Signal, name="fill_head", metadata={"units": "", "description": ""})
	fill_head_param = Cpt(Custom_Function_Signal, name="fill_head_param", metadata={"units": "", "description": ""})
	change_volume = Cpt(Custom_Function_Signal, name="change_volume", metadata={"units": "", "description": ""})
	change_volume_param = Cpt(Custom_Function_Signal, name="change_volume_param", metadata={"units": "", "description": ""})
	approach = Cpt(Custom_Function_Signal, name="approach", metadata={"units": "", "description": ""})
	approach_param = Cpt(Custom_Function_Signal, name="approach_param", metadata={"units": "", "description": ""})
	led_intensity = Cpt(Custom_Function_Signal, name="led_intensity", metadata={"units": "", "description": ""})

	#sample-set-channels:
	samplepointnumber = Cpt(Custom_Function_Signal, name="samplepointnumber", metadata={"units": "", "description": ""})
	samplepoints = Cpt(Custom_Function_Signal, name="samplepointnumber", metadata={"units": "", "description": ""})

	#config parameters
	STAGE_A_Z_SAFE = Cpt(Custom_Function_Signal, name="STAGE_A_Z_SAFE", kind="config", metadata={"units": "", "description": ""})
	STAGE_COM_PORT = Cpt(Custom_Function_Signal, name="STAGE_COM_PORT", kind="config", metadata={"units": "", "description": ""})
	STAGE_PARKING = Cpt(Custom_Function_Signal, name="STAGE_PARKING", kind="config", metadata={"units": "", "description": ""})
	HEAD_COM_PORT = Cpt(Custom_Function_Signal, name="HEAD_COM_PORT", kind="config", metadata={"units": "", "description": ""})
	HEAD_FORCE_CALIBRATION = Cpt(Custom_Function_Signal, name="HEAD_FORCE_CALIBRATION", kind="config", metadata={"units": "", "description": ""})
	HEAD_STANDARD_FLOW = Cpt(Custom_Function_Signal, name="HEAD_STANDARD_FLOW", kind="config", metadata={"units": "", "description": ""})
	SAMPLE_HEIGHT = Cpt(Custom_Function_Signal, name="SAMPLE_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	SAMPLE_DISTANCEBORDER = Cpt(Custom_Function_Signal, name="SAMPLE_DISTANCEBORDER", kind="config", metadata={"units": "", "description": ""})
	POSITION = Cpt(Custom_Function_Signal, name="POSITION", kind="config", metadata={"units": "", "description": ""})
	SAMPLE_ORIGIN = Cpt(Custom_Function_Signal, name="SAMPLE_ORIGIN", kind="config", metadata={"units": "", "description": ""})
	ORIGIN_OFFSET = Cpt(Custom_Function_Signal, name="ORIGIN_OFFSET", kind="config", metadata={"units": "", "description": ""})
	SAMPLE_SIZE = Cpt(Custom_Function_Signal, name="SAMPLE_SIZE", kind="config", metadata={"units": "", "description": ""})
	MOVE_HEIGHT = Cpt(Custom_Function_Signal, name="MOVE_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	SAFE_HEIGHT = Cpt(Custom_Function_Signal, name="SAFE_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	MIXER_LIMIT = Cpt(Custom_Function_Signal, name="MIXER_LIMIT", kind="config", metadata={"units": "", "description": ""})
	MIXER_HEIGHT = Cpt(Custom_Function_Signal, name="MIXER_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	MIXER_POSITION = Cpt(Custom_Function_Signal, name="MIXER_POSITION", kind="config", metadata={"units": "", "description": ""})
	RESERVOIR_HEIGHT = Cpt(Custom_Function_Signal, name="RESERVOIR_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	RESERVOIR_POSITION = Cpt(Custom_Function_Signal, name="RESERVOIR_POSITION", kind="config", metadata={"units": "", "description": ""})
	CLEANING_HEIGHT = Cpt(Custom_Function_Signal, name="CLEANING_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	CLEANING_POSITION = Cpt(Custom_Function_Signal, name="CLEANING_POSITION", kind="config", metadata={"units": "", "description": ""})
	WASTE_HEIGHT = Cpt(Custom_Function_Signal, name="WASTE_HEIGHT", kind="config", metadata={"units": "", "description": ""})
	WASTE_POSITION = Cpt(Custom_Function_Signal, name="WASTE_POSITION", kind="config", metadata={"units": "", "description": ""})
	SHED_DROP_DISTANCE = Cpt(Custom_Function_Signal, name="SHED_DROP_DISTANCE", kind="config", metadata={"units": "", "description": ""})
	TOTAL_VOLUME = Cpt(Custom_Function_Signal, name="TOTAL_VOLUME", kind="config", metadata={"units": "", "description": ""})
	MEASUREMENT_VOLUME = Cpt(Custom_Function_Signal, name="MEASUREMENT_VOLUME", kind="config", metadata={"units": "", "description": ""})
	NEGATIVE_VOLUME = Cpt(Custom_Function_Signal, name="NEGATIVE_VOLUME", kind="config", metadata={"units": "", "description": ""})
	MIXER_VOLUME = Cpt(Custom_Function_Signal, name="MIXER_VOLUME", kind="config", metadata={"units": "", "description": ""})
	PURGE_VOLUME = Cpt(Custom_Function_Signal, name="PURGE_VOLUME", kind="config", metadata={"units": "", "description": ""})
	CLEANING_VOLUME = Cpt(Custom_Function_Signal, name="CLEANING_VOLUME", kind="config", metadata={"units": "", "description": ""})
	CLEANING_STEPS = Cpt(Custom_Function_Signal, name="CLEANING_STEPS", kind="config", metadata={"units": "", "description": ""})
	TARGET_GRAM_FORCE = Cpt(Custom_Function_Signal, name="TARGET_GRAM_FORCE", kind="config", metadata={"units": "", "description": ""})


	#----------------------------------------------------------------------------------------------#
	#-----------ESSENTIAL DRIVER FUNCTIONS---------------------------------------------------------#
	#----------------------------------------------------------------------------------------------#

	#The init function will be called by CAMELS each time a new instance of the driver is built.
	#A new instance is built each time a new protocol is manually executed.
	#When a CAMELS-subprotocol is automatically executed, NO new instance is created, so the init function will not be called again.
	def __init__(self, prefix="", *, name, kind=None, read_attrs=None, configuration_attrs=None, parent=None, **kwargs):
		
		#CAMELS-default:
		super().__init__(prefix=prefix, name=name, kind=kind, read_attrs=read_attrs, configuration_attrs=configuration_attrs, parent=parent, **kwargs)

		#Create Backend Instances:
		self.StageBackend = xyz_stage.stage()
		self.HeadBackend = head_control.head()
		self.SampleBackend = procedure.sample()

		#define put functions
		self.positionxy.put_function = self.positionxy_put_function
		self.position_param.put_function = self.position_param_put_function
		self.position_sample.put_function = self.position_sample_put_function
		self.position_drop.put_function = self.position_drop_put_function
		self.height.put_function = self.height_put_function
		self.height_param.put_function = self.height_param_put_function
		self.command.put_function = self.command_put_function
		self.purge_head.put_function = self.purge_head_put_function
		self.purge_head_param.put_function = self.purge_head_param_put_function
		self.fill_head.put_function = self.fill_head_put_function
		self.fill_head_param.put_function = self.fill_head_param_put_function
		self.change_volume.put_function = self.change_volume_put_function
		self.change_volume_param.put_function = self.change_volume_param_put_function
		self.approach.put_function = self.approach_put_function
		self.approach_param.put_function = self.approach_param_put_function
		self.led_intensity.put_function = self.led_intensity_put_function


		#define read functions
		self.home.read_function = self.home_read_function
		self.finish_move.read_function = self.finish_move_read_function
		self.parking.read_function = self.parking_read_function
		self.testmove.read_function = self.testmove_read_function
		self.shed_drop.read_function = self.shed_drop_read_function
		self.volume_zero.read_function = self.volume_zero_read_function
		self.samplepointnumber.put_function = self.samplepointnumber_put_function
		self.samplepointnumber.read_function = self.samplepointnumber_read_function
		self.samplepoints.put_function = self.samplepoints_put_function

		#set config parameters
		self.STAGE_PARKING.put_function = self.STAGE_PARKING_put_function
		self.STAGE_A_Z_SAFE.put_function = self.STAGE_A_Z_SAFE_put_function
		self.HEAD_FORCE_CALIBRATION.put_function = self.HEAD_FORCE_CALIBRATION_put_function
		self.HEAD_STANDARD_FLOW.put_function = self.HEAD_STANDARD_FLOW_put_function
		self.SAMPLE_HEIGHT.put_function = self.SAMPLE_HEIGHT_put_function
		self.SAMPLE_DISTANCEBORDER.put_function = self.SAMPLE_DISTANCEBORDER_put_function
		self.POSITION.put_function = self.POSITION_put_function
		self.SAMPLE_ORIGIN.put_function = self.SAMPLE_ORIGIN_put_function
		self.ORIGIN_OFFSET.put_function = self.ORIGIN_OFFSET_put_function
		self.SAMPLE_SIZE.put_function = self.SAMPLE_SIZE_put_function
		self.MOVE_HEIGHT.put_function = self.MOVE_HEIGHT_put_function
		self.SAFE_HEIGHT.put_function = self.SAFE_HEIGHT_put_function
		self.MIXER_LIMIT.put_function = self.MIXER_LIMIT_put_function
		self.MIXER_HEIGHT.put_function = self.MIXER_HEIGHT_put_function
		self.MIXER_POSITION.put_function = self.MIXER_POSITION_put_function
		self.RESERVOIR_HEIGHT.put_function = self.RESERVOIR_HEIGHT_put_function
		self.RESERVOIR_POSITION.put_function = self.RESERVOIR_POSITION_put_function
		self.CLEANING_HEIGHT.put_function = self.CLEANING_HEIGHT_put_function
		self.CLEANING_POSITION.put_function = self.CLEANING_POSITION_put_function
		self.WASTE_HEIGHT.put_function = self.WASTE_HEIGHT_put_function
		self.WASTE_POSITION.put_function = self.WASTE_POSITION_put_function
		self.SHED_DROP_DISTANCE.put_function = self.SHED_DROP_DISTANCE_put_function
		self.TOTAL_VOLUME.put_function = self.TOTAL_VOLUME_put_function
		self.MEASUREMENT_VOLUME.put_function = self.MEASUREMENT_VOLUME_put_function
		self.NEGATIVE_VOLUME.put_function = self.NEGATIVE_VOLUME_put_function
		self.MIXER_VOLUME.put_function = self.MIXER_VOLUME_put_function
		self.PURGE_VOLUME.put_function = self.PURGE_VOLUME_put_function
		self.CLEANING_VOLUME.put_function = self.CLEANING_VOLUME_put_function
		self.CLEANING_STEPS.put_function = self.CLEANING_STEPS_put_function
		self.TARGET_GRAM_FORCE.put_function = self.TARGET_GRAM_FORCE_put_function

		#connect and home stage:
		self.STAGE_COM_PORT.put_function = self.STAGE_COM_PORT_put_function

		#connect and home head:
		self.HEAD_COM_PORT.put_function = self.HEAD_COM_PORT_put_function
		

	#The finalize steps function will be called each time CAMELS closes a driver instance.
	#This happens each time a manually executed protocol is finished or aborted by error.
	#It does not happen, when a automatically executed subprotocol is finished.
	def finalize_steps(self):

		#write down status
		with open(statusfile,"w+") as file:
			volumestring = "volume," + str(self.HeadBackend.volume())
			file.write(volumestring)
			print(volumestring)
		file.close()

		#disconnect
		self.StageBackend.disconnect()
		self.HeadBackend.disconnect()
		del self.StageBackend
		del self.HeadBackend


	#----------------------------------------------------------------------------------------------#
	#-----------HARDWARE FUNCTIONS-----------------------------------------------------------------#
	#----------------------------------------------------------------------------------------------#

	# ----- Stage Hardware functions --------------:
	#for more descriptions of the functions look in the xyz_stage.py backend script

	#takes tuple (x,y) and moves to position
	def positionxy_put_function(self, postuple):
		if(isinstance(postuple,str)):
			#as a string, postuple must look like "x,y" . Not "(x,y)".
			postuple = postuple.split(",")
		x = float(postuple[0])
		y = float(postuple[1])
		self.StageBackend.position(x,y,fast=True)
		return True
	
	#takes string (e.g. "CLEANING_POSITION") and moves to corresponding position
	def position_param_put_function(self, paramname):
		self.positionxy_put_function(self.SampleBackend.params[paramname])
		return True
	
	#move to position i of the positionvector
	def position_sample_put_function(self, i):
		i = int(i)
		if (i<len(self.SampleBackend.samplepoints)):
			self.positionxy_put_function(self.SampleBackend.samplepoints[i])
			return True
		else:
			print("Position Index too high!")
			raise IndexError
		
	#move to position i of the positionvector
	def position_drop_put_function(self, i):
		i = int(i)
		if (i<len(self.SampleBackend.samplepoints)):
			x,y = self.SampleBackend.samplepoints[i]
			x += self.SampleBackend.params["SAMPLE_SIZE"][0]
			self.positionxy_put_function((x,y))
			return True
		else:
			print("Position Index too high!")
			raise IndexError
	
	#move to height z
	def height_put_function(self, z):
		self.StageBackend.height(z)
		return True
	
	#takes string (e.g. "SAMPLE_HEIGHT") and moves to the corresponding height
	def height_param_put_function(self, paramname):
		if(paramname == "APPROACH_SAMPLE_HEIGHT"):
			self.StageBackend.height(self.SampleBackend.params["SAMPLE_HEIGHT"]+2.0)
		else:
			self.StageBackend.height(self.SampleBackend.params[paramname])
		return True
	
	def home_read_function(self):
		self.StageBackend.home()
		return True
	
	def shed_drop_read_function(self):
		self.StageBackend.position(-self.SampleBackend.params["SHED_DROP_DISTANCE"], 0., relative=True, fast=True)
		return True
	
	def finish_move_read_function(self):
		self.StageBackend.finish_move()
		return True
	
	def parking_read_function(self):
		self.StageBackend.parking()
		return True
	
	def testmove_read_function(self):
		self.StageBackend.testmove()
		return True
	
	
	# ----- Head Hardware functions --------------:
	#for more descriptions of the functions look in the head_control.py backend script

	def volume_zero_read_function(self):
		self.HeadBackend.set_volume(0)
		return True

	def fill_head_put_function(self, volume):
		self.HeadBackend.fill_head(volume)
		return True
	
	def fill_head_param_put_function(self, paramname):
		self.HeadBackend.fill_head(self.SampleBackend.params[paramname])
		return True
	
	def purge_head_put_function(self, volume):
		self.HeadBackend.purge_head(volume)
		return True

	def purge_head_param_put_function(self, paramname):
		self.HeadBackend.purge_head(self.SampleBackend.params[paramname])
		return True

	def change_volume_put_function(self, milliliter):
		self.HeadBackend.change_volume(milliliter)
		return True

	def change_volume_param_put_function(self, paramname):
		print(self.SampleBackend.params[paramname])
		self.HeadBackend.change_volume(self.SampleBackend.params[paramname])
		return True

	def approach_put_function(self, force):
		self.HeadBackend.approach(self.StageBackend, force)
		return True

	def approach_param_put_function(self, paramname):
		self.HeadBackend.approach(self.StageBackend, self.SampleBackend.params[paramname])
		return True
	
	def led_intensity_put_function(self, pwm):
		self.HeadBackend.set_led_intensity(pwm)
		return True


	#----------------------------------------------------------------------------------------------#
	#-----------HIGH-LEVEL COMMANDS----------------------------------------------------------------#
	#----------------------------------------------------------------------------------------------#

	#This set-channel takes a command as a string and executes the command in the backend, if it fits to the options below
	def command_put_function(self, commandstr):
		commandstr = commandstr.split(";")
		command = commandstr[0]
		if len(commandstr)>1:
			argument = commandstr[1]

		print(command)
		match command:
			#procedure commands (no input):
			case "draw_solution_finalize":
				procedure.draw_solution_finalize(self.StageBackend, self.HeadBackend)
			case "draw_solution_reservoir":
				procedure.draw_solution_reservoir(self.StageBackend, self.HeadBackend)
			case "discard_solution":
				procedure.discard_solution(self.StageBackend, self.HeadBackend)
			case "clean_head":
				procedure.clean_head(self.StageBackend, self.HeadBackend)

			#procedure commands (with input):
			case "safe_move":
				pos = tuple([float(x) for x in argument.split(",")])
				procedure.safe_move(self.StageBackend, self.HeadBackend, pos)
			case "draw_solution_mixer":
				ratios = tuple([float(x) for x in argument.split(",")])
				procedure.draw_solution_mixer(self.StageBackend, self.HeadBackend, ratios)
			case "approach_sample":
				pos_xyz = [float(x) for x in argument.split(",")]
				xy = tuple([pos_xyz[0],pos_xyz[1]])
				z = pos_xyz[2]
				procedure.approach_sample(self.StageBackend, self.HeadBackend, xy, z)
			
		return True


	#----------------------------------------------------------------------------------------------#
	#-----------PARAMETER CONFIG FUNCTIONS---------------------------------------------------------#
	#----------------------------------------------------------------------------------------------#

	# ----- Stage config functions --------------:

	def STAGE_COM_PORT_put_function(self,value):
		self.StageBackend.COM_PORT = value

		print("connecting Stage..")
		self.StageBackend.connect()
		print("Stage connected!")

		#home stage if necessary
		self.StageBackend.checkhomestate()

	def STAGE_PARKING_put_function(self,pos_parking_string):
		pos_parking = tuple([float(x) for x in pos_parking_string.split(",")])
		self.StageBackend.PARKING = pos_parking

	def STAGE_A_Z_SAFE_put_function(self,value):
		self.StageBackend.Z_SAFE = value


	# ----- Head config functions --------------:

	def HEAD_COM_PORT_put_function(self,value):
		self.HeadBackend.COM_PORT = value

		print("connecting Head..")
		self.HeadBackend.connect()
		print("Head connected!")
		
		#home head:
		with open(statusfile,"r") as file:
			volumestring = file.readline()
			print(volumestring)
		file.close()
		volume = float(volumestring.split(",")[1])
		self.HeadBackend.home(volume)
		

	def HEAD_FORCE_CALIBRATION_put_function(self,value):
		self.HeadBackend.FORCE_CALIBRATION = value

	def HEAD_STANDARD_FLOW_put_function(self,value):
		self.HeadBackend.STANDARD_FLOW = value


	# ----- Sample and other config functions --------------:
	#positions are converted from strings to tuples in the config functions

	#builds the list of samplepoints in self.Samplebackend with the assumption of equal distances on a square
	def samplepointnumber_put_function(self,number):
		self.SampleBackend.createsamplepointsbynumber(number)

	#builds the list of samplepoints in self.Samplebackend through a string-list with the positions
	def samplepoints_put_function(self,pointsstring):
		pointsstring = pointsstring.split(";")
		points = [(float(point.split(",")[0]),float(point.split(",")[1])) for point in pointsstring]
		self.SampleBackend.samplepoints = points

	def samplepointnumber_read_function(self):
		return len(self.SampleBackend.samplepoints)

	def SAMPLE_HEIGHT_put_function(self, value):
		self.SampleBackend.params["SAMPLE_HEIGHT"] = value

	def POSITION_put_function(self, value_int):
		self.SampleBackend.params["POSITION"] = value_int

	def SAMPLE_ORIGIN_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["SAMPLE_ORIGIN"] = value

	def SAMPLE_DISTANCEBORDER_put_function(self, value):
		self.SampleBackend.params["SAMPLE_DISTANCEBORDER"] = value

	def ORIGIN_OFFSET_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["ORIGIN_OFFSET"] = value

	def SAMPLE_SIZE_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["SAMPLE_SIZE"] = value

	def MOVE_HEIGHT_put_function(self, value):
		self.SampleBackend.params["MOVE_HEIGHT"] = value

	def SAFE_HEIGHT_put_function(self, value):
		self.SampleBackend.params["SAFE_HEIGHT"] = value

	def MIXER_LIMIT_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["MIXER_LIMIT"] = value

	def MIXER_HEIGHT_put_function(self, value):
		self.SampleBackend.params["MIXER_HEIGHT"] = value

	def MIXER_POSITION_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["MIXER_POSITION"] = value

	def RESERVOIR_HEIGHT_put_function(self, value):
		self.SampleBackend.params["RESERVOIR_HEIGHT"] = value

	def RESERVOIR_POSITION_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["RESERVOIR_POSITION"] = value

	def CLEANING_HEIGHT_put_function(self, value):
		self.SampleBackend.params["CLEANING_HEIGHT"] = value

	def CLEANING_POSITION_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["CLEANING_POSITION"] = value

	def WASTE_HEIGHT_put_function(self, value):
		self.SampleBackend.params["WASTE_HEIGHT"] = value

	def WASTE_POSITION_put_function(self, value_string):
		value = tuple([float(x) for x in value_string.split(",")])
		self.SampleBackend.params["WASTE_POSITION"] = value

	def SHED_DROP_DISTANCE_put_function(self, value):
		self.SampleBackend.params["SHED_DROP_DISTANCE"] = value

	def TOTAL_VOLUME_put_function(self, value):
		self.SampleBackend.params["TOTAL_VOLUME"] = value

	def MEASUREMENT_VOLUME_put_function(self, value):
		self.SampleBackend.params["MEASUREMENT_VOLUME"] = value

	def NEGATIVE_VOLUME_put_function(self, value):
		self.SampleBackend.params["NEGATIVE_VOLUME"] = value

	def MIXER_VOLUME_put_function(self, value):
		self.SampleBackend.params["MIXER_VOLUME"] = value

	def PURGE_VOLUME_put_function(self, value):
		self.SampleBackend.params["PURGE_VOLUME"] = value

	def CLEANING_VOLUME_put_function(self, value):
		self.SampleBackend.params["CLEANING_VOLUME"] = value

	def CLEANING_STEPS_put_function(self, value):
		self.SampleBackend.params["CLEANING_STEPS"] = value

	def TARGET_GRAM_FORCE_put_function(self, value):
		self.SampleBackend.params["TARGET_GRAM_FORCE"] = value