import sys
sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\.desertenv\Lib\site-packages")
sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\.desertenv\Lib\site-packages/nomad_camels")
sys.path.append(r"C:/Users/GuggenbergerB/AppData/Local/Programs/NOMAD-CAMELS/devices_drivers")

import numpy as np
import importlib
import bluesky
import ophyd
import requests
from nomad_camels.bluesky_handling.run_engine_overwrite import RunEngineOverwrite
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.preprocessors import fly_during_wrapper
import bluesky.plan_stubs as bps
import databroker
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QCoreApplication, QThread
import datetime
import subprocess
import time
from nomad_camels.utility import theme_changing
from nomad_camels.bluesky_handling.evaluation_helper import Evaluator
from nomad_camels.bluesky_handling import helper_functions, variable_reading
from event_model import RunRouter
darkmode = False
theme = "default"
protocol_step_information = {"protocol_step_counter": 0, "total_protocol_steps": 1, "protocol_stepper_signal": None}

namespace = {}
all_fits = {}
plots = []
plots_plotly = []
flyers = []
web_ports = []
boxes = {}
live_windows = []
app = None
save_path = "C:/Users/GuggenbergerB/Documents/NOMAD_CAMELS_data/SPEC/test/data"
session_name = ""
export_to_csv = False
export_to_json = False
new_file_each_run = True
new_file_hours = 0
do_nexus_output = False
For_Loop_Count = 0
namespace["For_Loop_Count"] = For_Loop_Count
For_Loop_Value = 0
namespace["For_Loop_Value"] = For_Loop_Value
points = 0
namespace["points"] = points
For_Loop_Count = 0
namespace["For_Loop_Count"] = For_Loop_Count
For_Loop_Value = 0
namespace["For_Loop_Value"] = For_Loop_Value

SamplePosLoop_variable_signal = variable_reading.Variable_Signal(name="SamplePosLoop_variable_signal", variables_dict=namespace)
aliases = {}
eva = Evaluator(namespace=namespace, aliases=aliases)



sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\devices_drivers\xy")
from nomad_camels_driver_xy.xy_ophyd import Xy




def SamplePosLoop_plan_inner(devs, stream_name="primary", runEngine=None):
    global For_Loop_Count, For_Loop_Value, points

    """height"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    yield from bps.abs_set(devs["xy"].height, eva.eval("4.0"), group="A")
    yield from bps.wait("A")

    """setpoints"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    yield from bps.abs_set(devs["xy"].samplepoints, eva.eval("'25.5,73.5;33.0,73.5;40.5,73.5;25.5,81.0;33.0,81.0;40.5,81.0;25.5,88.5;33.0,88.5;40.5,88.5'"), group="A")
    yield from bps.wait("A")

    """readpointnumber"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    channels_readpointnumber = [devs["xy"].samplepointnumber, SamplePosLoop_variable_signal]
    yield from helper_functions.trigger_and_read(channels_readpointnumber, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False])

    """setpointnumber"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    points = eva.eval("xy_samplepointnumber")
    namespace["points"] = points

    """For_Loop"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    for For_Loop_Count, For_Loop_Value in enumerate(helper_functions.get_range(eva, "0", "points-1", "15", "nan", "nan", "start - stop", "linear", "True", "1", True)):
        namespace.update({"For_Loop_Count": For_Loop_Count, "For_Loop_Value": For_Loop_Value})

        """Set_Channels"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        yield from bps.abs_set(devs["xy"].position_sample, eva.eval("For_Loop_Value"), group="A")
        yield from bps.wait("A")



def SamplePosLoop_plan(devs, md=None, runEngine=None, stream_name="primary"):
    sub_eva = runEngine.subscribe(eva)
    yield from bps.open_run(md=md)

    if web_ports:
        yield from wait_for_dash_ready_plan(web_ports)
    yield from SamplePosLoop_plan_inner(devs, stream_name, runEngine)
    yield from helper_functions.get_fit_results(all_fits, namespace, True)
    yield from bps.close_run()
    runEngine.unsubscribe(sub_eva)

def create_plots(RE, stream="primary"):
    return [], [], None, None

def steps_add_main(RE, devs, stream="primary"):
    returner = {}
    return returner


def create_live_windows():
    global live_windows
    return live_windows


uids = []
def uid_collector(name, doc):
    uids.append(doc["uid"])



def subscribe_plots_from_dict(plot_dict, dispatcher):
    if plot_dict and dispatcher:
        for k, v in plot_dict.items():
            if k == "plots":
                for plot in v:
                    dispatcher.subscribe(plot.livePlot)
            elif k == "plots_plotly":
                for plotly_plot in v:
                    dispatcher.subscribe(plotly_plot)
            elif isinstance(v, dict):
                subscribe_plots_from_dict(v, dispatcher)
def run_protocol_main(RE, dark=False, used_theme="default", catalog=None, devices=None, md=None, dispatcher=None, publisher=None, additionals=None):

    if (dispatcher and publisher):
        for plot in plots:
            dispatcher.subscribe(plot.livePlot)
        for plotly_plot in plots_plotly:
            dispatcher.subscribe(plotly_plot)
    subscribe_plots_from_dict(additionals, dispatcher)
    devs = devices or {}
    md = md or {}
    global darkmode, theme, protocol_step_information
    darkmode, theme = dark, used_theme
    protocol_step_information["total_protocol_steps"] = 7
    md["user"] = {'name': 'SPEC', 'email': '', 'affiliation': '', 'address': '', 'orcid': '', 'telephone_number': ''}
    md["sample"] = {'name': 'test', 'sample_id': '', 'description': '', 'owner': 'SPEC', 'display_name': 'test'}
    md["session_name"] = session_name
    md["protocol_overview"] = """Set Channels 'height' - {'xy_height': '4.0'}\nSet Channels 'setpoints' - {'xy_samplepoints': "'25.5,73.5;33.0,73.5;40.5,73.5;25.5,81.0;33.0,81.0;40.5,81.0;25.5,88.5;33.0,88.5;40.5,88.5'"}\nRead Channels 'readpointnumber' - ['xy_samplepointnumber']\nSet Variables 'setpointnumber' - {'Variable': ['points'], 'Value': ['xy_samplepointnumber']}\n'For_Loop' for (start: 0, stop: points-1, points: 15):\n\tSet Channels 'Set_Channels' - {'xy_position_sample': 'For_Loop_Value'}\n"""
    md["description"] = ''
    md["measurement_tags"] = []
    md["measurement_description"] = ''
    try:
        with open("C:/Users/GuggenbergerB/AppData/Local/Programs/NOMAD-CAMELS/protocols/SamplePosLoop.cprot", "r", encoding="utf-8") as f:
            md["protocol_json"] = f.read()
    except FileNotFoundError:
        print('Could not find protocol configuration file, information will be missing in data.')
    with open(__file__, "r", encoding="utf-8") as f:
        md["python_script"] = f.read()
    md = helper_functions.get_opyd_and_py_file_contents(Xy, md, 'xy')
    md["variables"] = namespace
    subscription_uid = RE.subscribe(uid_collector, "start")
    publisher_subscription = RE.subscribe(publisher)
    try:
        RE(SamplePosLoop_plan(devs, md=md, runEngine=RE))
    finally:
  
        if dispatcher:
            dispatcher.unsubscribe_all()
        if publisher_subscription:
            RE.unsubscribe(publisher_subscription)
        RE.unsubscribe(subscription_uid)
        for window in live_windows:
            window.close()


def ending_steps(runEngine, devs):
    yield from bps.checkpoint()

def wait_for_dash_ready_plan(web_ports, check_interval=0.1, timeout=60):
    start_time = time.time()
    while True:
        all_ready = True
        for web_port in web_ports:
            try:
                response = requests.get(f"http://127.0.0.1:{web_port}/status")
                if response.status_code != 200:
                    all_ready = False
                    break
            except requests.ConnectionError:
                all_ready = False
                break
        if all_ready:
            # All ports are ready; optionally return the list of ports or simply exit.
            return web_ports
        if time.time() - start_time > timeout:
            raise TimeoutError("Not all Dash servers started in time")
        yield from bps.sleep(check_interval)



def main(dispatcher=None, publisher=None):
    RE = RunEngineOverwrite()
    bec = BestEffortCallback()
    RE.subscribe(bec)

    if not (dispatcher and publisher):
        from bluesky.callbacks.zmq import RemoteDispatcher, Publisher
        from nomad_camels.main_classes.plot_proxy import StoppableProxy as Proxy
        from threading import Thread
        from zmq.error import ZMQError
        import asyncio
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        def setup_threads():
            try:
                proxy = Proxy(5577, 5578)
                proxy_created = True
            except ZMQError as e:
                # If the proxy is already running, a ZMQError will be raised.
                proxy = None  # We will use the already running proxy.
                proxy_created = False
            dispatcher = RemoteDispatcher("localhost:5578")

            def start_proxy():
                if proxy_created and proxy is not None:
                    proxy.start()
            
            def start_dispatcher(plots, plots_plotly):
                for plot in plots:
                    dispatcher.subscribe(plot.livePlot)
                for plotly_plot in plots_plotly:
                    dispatcher.subscribe(plotly_plot)
                try:
                    dispatcher.start()
                except asyncio.exceptions.CancelledError:
                    # This error is raised when the dispatcher is stopped. It can therefore be ignored
                    pass

            return proxy, dispatcher, start_proxy, start_dispatcher
        publisher = Publisher('localhost:5577')
        publisher_subscription = RE.subscribe(publisher)
        proxy, dispatcher, start_proxy, start_dispatcher = setup_threads()
        proxy_thread = Thread(target=start_proxy, daemon=True)
        dispatcher_thread = Thread(target=start_dispatcher, args=(plots, plots_plotly,), daemon=True)#
        proxy_thread.start()
        dispatcher_thread.start()
        time.sleep(0.5)
    try:
        catalog = databroker.catalog["CAMELS_CATALOG"]
    except KeyError:
        import warnings
        warnings.warn("Could not find databroker catalog, using temporary catalog. If data is not transferred, it might get lost.")
        catalog = databroker.temp().v2
    RE.subscribe(catalog.v1.insert)

    from nomad_camels.utility import tqdm_progress_bar
    tqdm_bar = tqdm_progress_bar.ProgressBar(7)

    protocol_step_information["protocol_stepper_signal"] = tqdm_bar
    devs = {}
    device_config = {}
    try:
        """xy (Xy):
        """
        settings = {}
        additional_info = {'config_channel_metadata': {'xy_STAGE_A_Z_SAFE': 'units: \ndescription: ', 'xy_STAGE_COM_PORT': 'units: \ndescription: ', 'xy_STAGE_PARKING': 'units: \ndescription: ', 'xy_HEAD_COM_PORT': 'units: \ndescription: ', 'xy_HEAD_FORCE_CALIBRATION': 'units: \ndescription: ', 'xy_HEAD_STANDARD_FLOW': 'units: \ndescription: ', 'xy_SAMPLE_HEIGHT': 'units: \ndescription: ', 'xy_SAMPLE_DISTANCEBORDER': 'units: \ndescription: ', 'xy_POSITION': 'units: \ndescription: ', 'xy_SAMPLE_ORIGIN': 'units: \ndescription: ', 'xy_ORIGIN_OFFSET': 'units: \ndescription: ', 'xy_SAMPLE_SIZE': 'units: \ndescription: ', 'xy_MOVE_HEIGHT': 'units: \ndescription: ', 'xy_SAFE_HEIGHT': 'units: \ndescription: ', 'xy_MIXER_LIMIT': 'units: \ndescription: ', 'xy_MIXER_HEIGHT': 'units: \ndescription: ', 'xy_MIXER_POSITION': 'units: \ndescription: ', 'xy_RESERVOIR_HEIGHT': 'units: \ndescription: ', 'xy_RESERVOIR_POSITION': 'units: \ndescription: ', 'xy_CLEANING_HEIGHT': 'units: \ndescription: ', 'xy_CLEANING_POSITION': 'units: \ndescription: ', 'xy_WASTE_HEIGHT': 'units: \ndescription: ', 'xy_WASTE_POSITION': 'units: \ndescription: ', 'xy_SHED_DROP_DISTANCE': 'units: \ndescription: ', 'xy_TOTAL_VOLUME': 'units: \ndescription: ', 'xy_MEASUREMENT_VOLUME': 'units: \ndescription: ', 'xy_NEGATIVE_VOLUME': 'units: \ndescription: ', 'xy_MIXER_VOLUME': 'units: \ndescription: ', 'xy_PURGE_VOLUME': 'units: \ndescription: ', 'xy_CLEANING_VOLUME': 'units: \ndescription: ', 'xy_CLEANING_STEPS': 'units: \ndescription: ', 'xy_TARGET_GRAM_FORCE': 'units: \ndescription: '}, 'description': '', 'ELN-instrument-id': '', 'ELN-service': '', 'ELN-metadata': {}, 'device_class_name': 'Xy'}
        xy = Xy("xy:", name="xy", **settings)
        print("connecting xy")
        xy.wait_for_connection()
        config = {'STAGE_A_Z_SAFE': 80.0, 'STAGE_COM_PORT': 'COM7', 'STAGE_PARKING': '141.8, 150.5', 'HEAD_COM_PORT': 'COM6', 'HEAD_FORCE_CALIBRATION': 17462, 'HEAD_STANDARD_FLOW': 0.1, 'SAMPLE_HEIGHT': 1.0, 'SAMPLE_DISTANCEBORDER': 5.0, 'POSITION': 0, 'SAMPLE_ORIGIN': '20.5, 68.5', 'ORIGIN_OFFSET': '0., 0.', 'SAMPLE_SIZE': '25.0, 25.0', 'MOVE_HEIGHT': 30.0, 'SAFE_HEIGHT': 80.0, 'MIXER_LIMIT': '125.0, 125.0', 'MIXER_HEIGHT': 62.0, 'MIXER_POSITION': '181.7, 73.5', 'RESERVOIR_HEIGHT': 3.0, 'RESERVOIR_POSITION': '205.0, 193.0', 'CLEANING_HEIGHT': 3.0, 'CLEANING_POSITION': '156.0, 193.0', 'WASTE_HEIGHT': 27.5, 'WASTE_POSITION': '205.0, 144.0', 'SHED_DROP_DISTANCE': 25.0, 'TOTAL_VOLUME': 0.5, 'MEASUREMENT_VOLUME': 0.3, 'NEGATIVE_VOLUME': 0.0, 'MIXER_VOLUME': 2.0, 'PURGE_VOLUME': 0.5, 'CLEANING_VOLUME': 1.0, 'CLEANING_STEPS': 3, 'TARGET_GRAM_FORCE': 60.0}
        configs = xy.configure(config)[1]
        device_config["xy"] = {"settings": {}}
        device_config["xy"]["settings"].update(helper_functions.simplify_configs_dict(configs))
        device_config["xy"]["settings"].update(settings)
        device_config["xy"].update(additional_info)
        devs.update({"xy": xy})
        print("devices connected")
        md = {"devices": device_config}
        rr = RunRouter([lambda x, y: helper_functions.saving_function(x, y, save_path, new_file_each_run, plots, do_nexus_output, new_file_hours)])
        subscription_rr = RE.subscribe(rr)
        plot_etc = create_plots(RE)
        additional_step_data = steps_add_main(RE, devs)
        create_live_windows()
        run_protocol_main(RE=RE, catalog=catalog, devices=devs, md=md, dispatcher=dispatcher, publisher=publisher, additionals=additional_step_data)
    finally:
        while RE.state not in ["idle", "panicked"]:
            time.sleep(0.5)
        for name, device in devs.items():
            if hasattr(device, "finalize_steps") and callable(device.finalize_steps):
                device.finalize_steps()
        if uids:
            runs = catalog[tuple(uids)]
            helper_functions.export_function(runs, save_path, False, new_file_each=new_file_each_run, plot_data=plots, do_nexus_output=do_nexus_output)
        RE.unsubscribe(subscription_rr)



if __name__ == "__main__":
    main()
    print("protocol finished!")
    if app is not None:
        sys.exit(app.exec())
