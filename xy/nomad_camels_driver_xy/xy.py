from .xy_ophyd import Xy

from nomad_camels.main_classes import device_class

class subclass(device_class.Device):
	def __init__(self, **kwargs):
		super().__init__(name="xy", virtual=False, tags=[], directory="xy", ophyd_device=Xy, ophyd_class_name="Xy", **kwargs)

		#stage configs:
		self.config["STAGE_A_Z_SAFE"] = 80.0
		self.config["STAGE_COM_PORT"] = 'COM7'
		self.config["STAGE_PARKING"] = '141.8, 150.5'

		#head configs:
		self.config["HEAD_COM_PORT"] = 'COM6'
		self.config["HEAD_FORCE_CALIBRATION"] = 17462
		self.config["HEAD_STANDARD_FLOW"] = 0.1

		self.config["POSITION"] = 0 # mm, mm
		self.config["SAMPLE_HEIGHT"] = 1.0 # mm, mm
		self.config["SAMPLE_DISTANCEBORDER"] = 5.0
		self.config["SAMPLE_ORIGIN"] = '20.5, 68.5' # mm, mm
		self.config["ORIGIN_OFFSET"] = '0., 0.' # mm, mm
		self.config["SAMPLE_SIZE"] = '25.0, 25.0' # mm, mm
		self.config["MOVE_HEIGHT"] = 30.0 # mm
		self.config["SAFE_HEIGHT"] = 80.0 # mm
		self.config["MIXER_LIMIT"] = '125.0, 125.0' # mm, mm
		self.config["MIXER_HEIGHT"] = 62.0 # mm
		self.config["MIXER_POSITION"] = '181.7, 73.5' # mm, mm
		self.config["RESERVOIR_HEIGHT"] = 3.0 # mm
		self.config["RESERVOIR_POSITION"] = '205.0, 193.0' # mm, mm
		self.config["CLEANING_HEIGHT"] = 3.0 # mm
		self.config["CLEANING_POSITION"] = '156.0, 193.0' # mm, mm
		self.config["WASTE_HEIGHT"] = 27.5 # mm
		self.config["WASTE_POSITION"] = '205.0, 144.0' # mm, mm
		self.config["SHED_DROP_DISTANCE"] = 25.0 # mm
		self.config["TOTAL_VOLUME"] = 1.0 # mL
		self.config["MEASUREMENT_VOLUME"] = 0.3 # ml
		self.config["NEGATIVE_VOLUME"] = 0.0 # ml
		self.config["MIXER_VOLUME"] = 2.0 # ml
		self.config["PURGE_VOLUME"] = 0.5 # mL
		self.config["CLEANING_VOLUME"] = 1.0 # mL
		self.config["CLEANING_STEPS"] = 3 # -
		self.config["TARGET_GRAM_FORCE"] = 60.0 # gf

class subclass_config(device_class.Simple_Config):
	def __init__(self, parent=None, data="", settings_dict=None, config_dict=None, additional_info=None):
		super().__init__(parent, "xy", data, settings_dict, config_dict, additional_info)
		self.load_settings()
