from .Testdriver_ophyd import Testdriver

from nomad_camels.main_classes import device_class

class subclass(device_class.Device):
	def __init__(self, **kwargs):
		super().__init__(name="Testdriver", virtual=False, tags=[], directory="Testdriver", ophyd_device=Testdriver, ophyd_class_name="Testdriver", **kwargs)


class subclass_config(device_class.Simple_Config):
	def __init__(self, parent=None, data="", settings_dict=None, config_dict=None, additional_info=None):
		super().__init__(parent, "Testdriver", data, settings_dict, config_dict, additional_info)
		self.load_settings()
