import sys
import clr
import time


# Configuration
# -----------------

BASE_PATH = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1"
HW_SETUP_FILE = r"C:\ProgramData\Metrohm Autolab\13.0\HardwareSetup.AUT86381.xml"
MIC_SETUP_FILE = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.bin"
PROCEDURES_PATH = r"C:\ProgramData\Metrohm Autolab\Procedures"
PROCEDURE_NAMES = {
    "CV": "Cyclic voltammetry potentiostatic.nox"
}


# Connection
# -----------------

sys.path.append(BASE_PATH)
clr.AddReference("EcoChemie.Autolab.Sdk")
from EcoChemie.Autolab import Sdk as sdk

instrument = sdk.Instrument()
instrument.HardwareSetupFile = HW_SETUP_FILE
instrument.AutolabConnection.EmbeddedExeFileToStart = MIC_SETUP_FILE
instrument.Connect()


# Procedures
# -----------------

def cv() -> dict:
    procedure = instrument.LoadProcedure(f'{PROCEDURES_PATH}/{PROCEDURE_NAMES['CV']}')
    current_range = procedure.Commands['FHGetSetValues'].CommandParameters['EI_0.CurrentRange'].Value
    procedure.Commands['FHGetSetValues'].CommandParameters['EI_0.CurrentRange'].Value = current_range.CR12_10uA
    procedure.Commands['FHSetSetpointPotential'].CommandParameters['Setpoint value'].Value = 0.
    procedure.Commands['FHWait'].CommandParameters['Time'].Value = 5.
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Start value'].Value = 0.
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Upper vertex'].Value = 0.1
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Lower vertex'].Value = -0.85
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Stop value'].Value = -0.6
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['NrOfStopCrossings'].Value = 6
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Scanrate'].Value = 0.1
    procedure.Commands['FHCyclicVoltammetry2'].CommandParameters['Step'].Value = 0.001
    procedure.Measure()
    while procedure.IsMeasuring:
        time.sleep(0.5)
    time.sleep(1.0)
    names = list(procedure.Commands['FHCyclicVoltammetry2'].Signals.Names)
    result = {n: list(procedure.Commands['FHCyclicVoltammetry2'].Signals.get_Item(n).Value) for n in names}
    return result
