from ophyd import Component as Cpt

from nomad_camels.bluesky_handling.custom_function_signal import Custom_Function_Signal, Custom_Function_SignalRO
from ophyd import Device

#Backend-skript:
from .potentiostat_backend import Potentiostat as Potentiostat_Backend
from .potentiostat_backend import Resistors
from .potentiostat_backend import SwitchState
from .potstat import cvmeasurement_stat


class Potentiostat(Device):

	U = Cpt(Custom_Function_Signal, name="U", metadata={"units": "V", "description": "WE-RE Voltage"})
	I = Cpt(Custom_Function_SignalRO, name="I", metadata={"units": "A", "description": "Current"})
	I_potstat = Cpt(Custom_Function_SignalRO, name="I_potstat", metadata={"units": "A", "description": "Current"})

	POTENTIOSTAT_COM_PORT = Cpt(Custom_Function_Signal, name="POTENTIOSTAT_COM_PORT", kind="config", metadata={"units": "", "description": ""})
	POTENTIOSTAT_SAMPLE_COUNT = Cpt(Custom_Function_Signal, name="POTENTIOSTAT_SAMPLE_COUNT", kind="config", metadata={"units": "", "description": ""})

	connected = False

	def __init__(self, prefix="", name="potentiostat", kind=None, read_attrs=None, configuration_attrs=None, parent=None, **kwargs):
		super().__init__(prefix=prefix, name=name, kind=kind, read_attrs=read_attrs, configuration_attrs=configuration_attrs, parent=parent, **kwargs)
		self.I.read_function = self.I_read_function
		self.U.put_function = self.U_put_function
		#self.U.read_function = self.U_read_function
		self.POTENTIOSTAT_COM_PORT.put_function = self.POTENTIOSTAT_COM_PORT_put_function
		self.POTENTIOSTAT_SAMPLE_COUNT.put_function = self.POTENTIOSTAT_SAMPLE_COUNT_put_function
		self.I_potstat.read_function = self.I_potstat_read_function

		self.PBackend = Potentiostat_Backend()
		self.U_stat = 0


	def finalize_steps(self):
		self.PBackend.write_switch(SwitchState.Off)
		self.PBackend.close()
		del self.PBackend

	def I_read_function(self):
		return self.PBackend.read_current()
	
	def U_put_function(self, value):
		self.PBackend.write_potential(value)
		self.U_stat = value
		return True
	
	def U_read_function(self):
		print(self.PBackend.read_potential())
		return self.PBackend.read_potential()
	
	def I_potstat_read_function(self):
		U = self.PBackend.read_potential()
		return cvmeasurement_stat(self.U_stat)

	def POTENTIOSTAT_COM_PORT_put_function(self,value):
		print("connecting Potentiostat..")
		self.PBackend.serial_port = value
		self.PBackend.connect()
		self.connected = True
		print("Potentiostat connected!")

		print("Initializing Potentiostat..")
		self.PBackend.write_switch(SwitchState.On)
		self.PBackend.write_auto_gain(True)
		#self.PBackend.write_gain(Resistors.R_1K)
		print("Potentiostat initialized!")
		print(self.PBackend.read_switch())

		return True
	

	def POTENTIOSTAT_SAMPLE_COUNT_put_function(self,value):
		self.PBackend.write_sample_count(value)
		return True