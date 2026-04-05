# User Manual — CV Measurement Device

## 1. Overview

### Purpose  
The system enables automated execution of multiple cyclic voltammetry (CV) measurements across different samples and positions. It coordinates hardware components to perform reproducible electrochemical experiments with minimal manual intervention.

### Scope  
The platform is intended for automated CV workflows with predefined settings for electrolyte handling, sample selection, LED control, and stage positioning. The system operates using a G-code–based 3D printer stage, a pump system, and a microcontroller-controlled potentiostat.

## 2. System Requirements

### Hardware  
- **3D printer XY stage (G-code based)**  
  Used for automated positioning of the measurement head across different samples and locations. Must support standard G-code communication via serial interface.

- **Potentiostat with microcontroller and three-electrode setup**  
  Required for performing cyclic voltammetry measurements. The system should include working, reference, and counter electrodes and provide serial communication for control and data acquisition.

- **Pump system for electrolyte handling**  
  Enables automated filling, flushing, or exchange of electrolyte during measurement sequences. The pump must be controllable via the software interface.

- **LED illumination (optional but recommended)**  
  Provides controlled illumination of the sample during measurements, e.g., for photoelectrochemical experiments. Should be electrically controllable if automated workflows are desired.

### Software

- **NOMAD CAMELS**  
  Primary measurement orchestration software used to configure instruments, execute protocols, and store FAIR-compliant data. NOMAD CAMELS is an open-source, Python-based measurement framework that provides a graphical user interface for defining and running automated experiments without requiring deep programming knowledge. :contentReference[oaicite:0]{index=0}  
  Installation instructions: https://fau-lap.github.io/NOMAD-CAMELS/doc/installation/installation.html

- **CAMELS Python environment**  
  Additional Python packages required by this project can be installed directly into the CAMELS Python environment.

  **Activate the environment:**

  ```bash
  .desertenv\Scripts\activate
  ```

  **Install packages with pip:**

  ```bash
    pip install <package-name>
    ```

- **pyserial (update required)**  
  The `pyserial` package must be installed or updated inside the CAMELS Python environment to ensure reliable serial communication with the hardware.


---

## 3. Installation

### 3.1 Clone the Repository  
Clone the NOMAD CAMELS repository to your local machine:

```bash
git clone https://gitlab-intern.ait.ac.at/ech-materials/nomad_camels.git
cd nomad_camels
```
### 3.2 Copy the Drivers to your local NOMAD-CAMELS Folder  

After cloning the repository, copy the folders **`xy`** and **`Potentiostat`** from the repository into your local NOMAD CAMELS driver directory.  
By default, this directory is `NOMAD_CAMELS\camels_drivers`. Note that the driver folder name may differ depending on your local CAMELS installation (e.g., `camels_drivers`, `drivers`, or a custom path). Ensure the two folders are placed inside the directory where CAMELS loads its device drivers.

### 3.3 Copy the protocols to your local NOMAD-CAMELS Folder

After cloning the repository, copy the entire **`protocols`** folder from the repository into your local **NOMAD CAMELS** installation directory.

By default, this is the main `NOMAD-CAMELS` folder. Ensure the `protocols` folder is placed at the top level of your CAMELS installation so that the protocols can be discovered and imported by the GUI.

### 3.4 Install Dependencies  
Install all required Python dependencies as described in the **System Requirements** section above.

### 3.5 Open NOMAD-CAMELS GUI and Load Protocols  
Start the NOMAD CAMELS GUI. First add the required devices, then import the measurement protocols.

---

## 4. Hardware Setup

### Connections
Ensure that all components of the measurement platform are properly connected before starting the system.  
This includes the **3D printer (XY stage)**, the **pump/head system**, the **LED illumination source**, and the **potentiostat microcontroller**.  

All devices that communicate via serial connection must have the **correct COM ports configured** in the corresponding drivers or configuration files so that CAMELS can establish communication with the hardware.

Additionally, the **electrodes must be correctly connected to the potentiostat microcontroller**:
- **WE (Working Electrode)**
- **RE (Reference Electrode)**
- **CE (Counter Electrode)**

Make sure the wiring matches the potentiostat labeling to ensure correct electrochemical measurements.

### Power-Up Procedure
Before running a protocol, power on all hardware components (3D printer, pump system, LED source, and potentiostat microcontroller) and verify that the devices are detected on the configured COM ports.

---

## 5. Configuration

Before running measurements, configure the required device and experiment parameters in NOMAD CAMELS.

### Required Parameters  
Typical parameters that must be set include:

- COM ports for stage, head, and potentiostat  
- Stage positions (e.g., reservoir, cleaning, waste, sample origin)  
- Heights (move height, safe height, cleaning height, etc.)  
- Volume settings (measurement, cleaning, purge, negative volume)  
- Potentiostat settings (voltage limits, cycles, step number, waiting time)  
- Optional LED settings for illumination experiments  

### Configuration Methods  

Configuration can be performed in the CAMELS GUI:

1. Add the devices (**xy**, **Potentiostat**) in the Devices panel.  
2. Open the device configuration and enter the required parameters.  
3. Save the configuration before running protocols.

The standard configurations can be changed in `NOMAD-CAMELS\camels_drivers\xy\nomad_camels_drivers_xy\xy.py`.

Ensure all hardware-related parameters are validated before starting automated runs.

## 6. Running a Measurement in the GUI

You can use prebuilt protocols via **Import** or create your own protocols.

The full measurement process protocols are stored directly in `NOMAD-CAMELS\protocols`.  
Subprotocols (e.g., XY stage steps or potentiostat measurements) are located in:

- `NOMAD-CAMELS\protocols\xyprotocols`  
- `NOMAD-CAMELS\protocols\potentiostatprotocols`

The following list provides a short overview of the most important protocols:

---

#### Lowest Level Subprotocols

- **home**  
  Executes the homing routine of the XY system. It triggers the hardware home command and records the status of the operation.

- **move**  
  Basic positioning primitive for the XY stage. The protocol first moves to a safe height and then drives the stage to the requested target position.

- **Protocol_CV_Real**  
  Executes the actual cyclic voltammetry measurement using the potentiostat. The protocol performs a voltage sweep from start to minimum, runs the defined number of CV cycles between minimum and maximum voltage while recording current and voltage, and finally returns the potential to the specified end value.

#### Medium Level Subprotocols

- **draw_solution_reservoir**  
  Handles electrolyte uptake from the reservoir. The system moves to the reservoir position, lowers to the correct height, fills the head with the defined total volume, and then executes the finalize routine.

- **draw_solution_finalize**  
  Finalizes the solution handling after filling. It performs positioning between cleaning and waste locations, adjusts volumes, triggers the shed-drop step, and returns the head to a safe height.

- **approach_sample_index**  
  Positions the measurement head above the selected sample index using the XY stage. It prepares the system for the electrochemical measurement at the correct spatial location.

- **discard_solution**  
  Handles post-measurement liquid disposal. The protocol moves to the waste position, purges the head, and resets the height to a safe move position.

- **clean_head**  
  Performs automated cleaning cycles of the measurement head. The protocol repeatedly moves to the cleaning position, fills the head with cleaning solution, and discards it for a defined number of iterations.

#### High Level Measurement Protocols

- **CVMeasurement_noclean**  
  Core single-point CV workflow. It draws electrolyte, moves to the selected sample position, performs the cyclic voltammetry measurement, and discards the used solution without performing a full cleaning cycle.

- **CVMeasurementLoop**  
  Main automation protocol that iterates over multiple sample positions and executes CV measurements sequentially. It loops over defined sample points, runs the CV measurement workflow at each position, and performs a final head cleaning step.


## Building new Protocols  

Protocols in NOMAD CAMELS define the automated workflow of an experiment. In the CAMELS GUI, a protocol is created by adding sequential steps such as running subprotocols, setting channels, waiting, or reading data. Channels represent the controllable or readable interfaces of devices (e.g., setting a voltage, moving a stage, or measuring a current) and are used within protocol steps to send commands to hardware or acquire values. A detailed step-by-step tutorial is available in the [Protocols-Tutorials](https://fau-lap.github.io/NOMAD-CAMELS/doc/tutorials/quick_start_protocols.html).  

There are multiple Channels for xyz_stage and Potentiostat commands. A quick overview will be provided below, detailed information can be found in the drivers ophyd python scripts.  

The `Xy` driver exposes CAMELS channels that wrap the underlying **stage**, **head**, and **sample** backends. These channels provide low-level hardware control as well as convenient higher-level operations.  

---
### Stage Channels

#### Read Channels

- **home**  
  Triggers the homing routine of the XY stage via the backend. Ensures the stage knows its absolute position.

- **shed_drop**  
  Performs the programmed lateral movement used to shed a droplet from the head.

- **finish_move**  
  Blocks execution until all stage motion commands have completed.

- **parking**  
  Moves the stage to the predefined parking position.

- **testmove**  
  Executes a short diagnostic Z motion for quick functionality testing.

#### Set Channels

- **positionxy**  
  Moves the stage to an explicit `(x, y)` coordinate.  
  **Input:** string filled with two floats  `"x, y"` in millimeters, e.g. `"156.0, 193.0"`.

- **position_param**  
  Moves the stage to a named position stored in the sample parameter dictionary (e.g., `CLEANING_POSITION`).  
  **Input:** string with the exact parameter key name, e.g. `"CLEANING_POSITION"`.

- **position_sample**  
  Moves to the *i-th* generated sample point.  
  **Input:** integer index `i` (0-based).

- **height**  
  Moves the Z axis to an absolute height.  
  **Input:** float height in millimeters, e.g. `30.0`.

- **height_param**  
  Moves the Z axis to a height defined in the sample parameters.  
  **Input:** string with the parameter key name, e.g. `"MOVE_HEIGHT"` or `"SAMPLE_HEIGHT"`.

- **command**  
  Executes higher-level procedure commands (e.g., `draw_solution_reservoir`, `clean_head`).  
  **Input:** string command; either just the command name (e.g. `"clean_head"`) or `"command;arg1,arg2,..."`
  depending on the procedure (e.g. `"safe_move;156.0,193.0"`).

---

### Head Channels

#### Read Channels

- **volume_zero**  
  Forces the pump volume to zero by commanding the head backend.

#### Set Channels

- **fill_head**  
  Fills the syringe head to the specified volume using the relay logic in the backend.  
  **Input:** float volume in milliliters, e.g. `1.0`.

- **fill_head_param**  
  Same as `fill_head`, but the volume is taken from a named sample parameter.  
  **Input:** string with parameter key name, e.g. `"TOTAL_VOLUME"`.

- **purge_head**  
  Purges liquid from the head by the specified volume.  
  **Input:** float volume in milliliters, e.g. `0.5`.

- **purge_head_param**  
  Parameter-based variant of `purge_head`.  
  **Input:** string with parameter key name, e.g. `"PURGE_VOLUME"`.

- **change_volume**  
  Changes the current pump volume by a relative amount.  
  **Input:** float volume change in milliliters (can be positive or negative depending on backend logic), e.g. `0.15`.

- **change_volume_param**  
  Parameter-based variant of `change_volume`.  
  **Input:** string with parameter key name, e.g. `"NEGATIVE_VOLUME"`.

- **approach**  
  Performs force-controlled touchdown of the head onto the sample using the stage.  
  **Input:** float target force in gram-force (gf), e.g. `60.0`.

- **approach_param**  
  Parameter-based variant of `approach`.  
  **Input:** string with parameter key name, e.g. `"TARGET_GRAM_FORCE"`.

---

### Sample Channels

#### Set Channels

- **samplepointnumber**  
  Generates a grid of sample positions based on the requested number of points. The positions are stored internally and used by `position_sample`.  
  **Input:** integer number of sample points, e.g. `9`.

---

### Notes

- All set channels return `True` on successful execution.  
- Parameter-based channels allow protocol-level indirection via the sample parameter dictionary.  
- The `command` channel exposes composite liquid-handling workflows implemented in `procedure.py`.


---


## 7. Output Data

The measurement data is stored automatically in an **HDF5 file** generated by NOMAD CAMELS. This file contains all recorded channels (e.g., current, voltage, positions, and other device signals) together with the corresponding timestamps and metadata of the run.

Additionally, CAMELS allows adding **live plots directly within the measurement protocol**. By including a plot step in the protocol, selected channels can be visualized during the measurement. These plots are also available after the run and can be explored **interactively within the CAMELS interface**.

---

## 8. Support

Email:  

bastian.guggenberger@aon.at  
maximilian.wolf@ait.ac.at