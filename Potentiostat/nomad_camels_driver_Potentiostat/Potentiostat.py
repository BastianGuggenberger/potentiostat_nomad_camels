from .Potentiostat_ophyd import Potentiostat

from nomad_camels.main_classes import device_class

class subclass(device_class.Device):
	def __init__(self, **kwargs):
		super().__init__(name="Potentiostat", virtual=False, tags=['potentiostat', 'ech'], directory="Potentiostat", ophyd_device=Potentiostat, ophyd_class_name="Potentiostat", **kwargs)
		self.config["POTENTIOSTAT_COM_PORT"] = 'COM9'
		self.config["POTENTIOSTAT_SAMPLE_COUNT"] = 10


class subclass_config(device_class.Simple_Config):
	def __init__(self, parent=None, data="", settings_dict=None, config_dict=None, additional_info=None):
		super().__init__(parent, "Potentiostat", data, settings_dict, config_dict, additional_info)
		self.load_settings()
