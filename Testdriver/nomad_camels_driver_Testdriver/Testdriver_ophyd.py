from ophyd import Component as Cpt

from nomad_camels.bluesky_handling.custom_function_signal import Custom_Function_Signal, Custom_Function_SignalRO
from ophyd import Device

from .backend.Test_backend import virtualdevice

class Testdriver(Device):
	U = Cpt(Custom_Function_Signal, name="U", metadata={"units": "V", "description": "Voltage"})
	I = Cpt(Custom_Function_SignalRO, name="I", metadata={"units": "A", "description": "Current"})

	def __init__(self, prefix="", *, name, kind=None, read_attrs=None, configuration_attrs=None, parent=None, **kwargs):
		super().__init__(prefix=prefix, name=name, kind=kind, read_attrs=read_attrs, configuration_attrs=configuration_attrs, parent=parent, **kwargs)
		self.I.read_function = self.I_read_function
		self.U.put_function = self.U_put_function
		self.Device_Backend = virtualdevice(4)

	def finalize_steps(self):
		"""This function is called when the device is not used anymore. It is used for example to close the connection to the device."""
		pass

	def I_read_function(self):
		return self.Device_Backend.get_I()
	
	def U_read_function(self):
		return self.Device_Backend.get_U()
		

	def U_put_function(self, value):
		self.Device_Backend.set_U(value)
		

