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
save_path = "test"
session_name = ""
export_to_csv = False
export_to_json = False
new_file_each_run = True
new_file_hours = 0
do_nexus_output = False
CyclesLoop_Count = 0
namespace["CyclesLoop_Count"] = CyclesLoop_Count
CyclesLoop_Value = 0
namespace["CyclesLoop_Value"] = CyclesLoop_Value
MintoLast_Count = 0
namespace["MintoLast_Count"] = MintoLast_Count
MintoLast_Value = 0
namespace["MintoLast_Value"] = MintoLast_Value
StarttoMin_Count = 0
namespace["StarttoMin_Count"] = StarttoMin_Count
StarttoMin_Value = 0
namespace["StarttoMin_Value"] = StarttoMin_Value
Voltage_Loop_Down_Count = 0
namespace["Voltage_Loop_Down_Count"] = Voltage_Loop_Down_Count
Voltage_Loop_Down_Value = 0
namespace["Voltage_Loop_Down_Value"] = Voltage_Loop_Down_Value
Voltage_Loop_Up_Count = 0
namespace["Voltage_Loop_Up_Count"] = Voltage_Loop_Up_Count
Voltage_Loop_Up_Value = 0
namespace["Voltage_Loop_Up_Value"] = Voltage_Loop_Up_Value
cycles = 1
namespace["cycles"] = cycles
last_V = 0.0
namespace["last_V"] = last_V
max_V = 1.0
namespace["max_V"] = max_V
min_V = -1.3
namespace["min_V"] = min_V
start_V = 0.0
namespace["start_V"] = start_V
deltaV = 0.02
namespace["deltaV"] = deltaV
waitingtime = 0.01
namespace["waitingtime"] = waitingtime

Protocol_CV_Real_variable_signal = variable_reading.Variable_Signal(name="Protocol_CV_Real_variable_signal", variables_dict=namespace)
aliases = {}
eva = Evaluator(namespace=namespace, aliases=aliases)



sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\devices_drivers\Potentiostat")
from nomad_camels_driver_Potentiostat.Potentiostat_ophyd import Potentiostat




def Protocol_CV_Real_plan_inner(devs, stream_name="primary", runEngine=None):
    global CyclesLoop_Count, CyclesLoop_Value, MintoLast_Count, MintoLast_Value, StarttoMin_Count, StarttoMin_Value, Voltage_Loop_Down_Count, Voltage_Loop_Down_Value, Voltage_Loop_Up_Count, Voltage_Loop_Up_Value, cycles, last_V, max_V, min_V, start_V, deltaV, waitingtime

    """StarttoMin"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    for StarttoMin_Count, StarttoMin_Value in enumerate(helper_functions.get_range(eva, "start_V", "min_V", "100", "nan", "nan", "start - stop", "linear", "True", "deltaV", True)):
        namespace.update({"StarttoMin_Count": StarttoMin_Count, "StarttoMin_Value": StarttoMin_Value})

        """SetU0"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        yield from bps.abs_set(devs["Potentiostat"].U, eva.eval("StarttoMin_Value"), group="A")
        yield from bps.wait("A")

        """Wait0"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        yield from bps.sleep(eva.eval("waitingtime"))

        """readi0"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        channels_readi0 = [devs["Potentiostat"].I, devs["Potentiostat"].U, Protocol_CV_Real_variable_signal]
        yield from helper_functions.trigger_and_read(channels_readi0, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False, False])

    """CyclesLoop"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    for CyclesLoop_Count, CyclesLoop_Value in enumerate(helper_functions.get_range(eva, "1", "cycles", "cycles", "nan", "nan", "start - stop", "linear", "True", "nan", False)):
        namespace.update({"CyclesLoop_Count": CyclesLoop_Count, "CyclesLoop_Value": CyclesLoop_Value})

        """Voltage_Loop_Up"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        for Voltage_Loop_Up_Count, Voltage_Loop_Up_Value in enumerate(helper_functions.get_range(eva, "min_V", "max_V", "100", "nan", "nan", "start - stop", "linear", "True", "deltaV", True)):
            namespace.update({"Voltage_Loop_Up_Count": Voltage_Loop_Up_Count, "Voltage_Loop_Up_Value": Voltage_Loop_Up_Value})

            """Set_U"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            yield from bps.abs_set(devs["Potentiostat"].U, eva.eval("Voltage_Loop_Up_Value"), group="A")
            yield from bps.wait("A")

            """Wait"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            yield from bps.sleep(eva.eval("waitingtime"))

            """Read_CV"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            channels_Read_CV = [devs["Potentiostat"].I, devs["Potentiostat"].U, Protocol_CV_Real_variable_signal]
            yield from helper_functions.trigger_and_read(channels_Read_CV, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False, False])

        """Voltage_Loop_Down"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        for Voltage_Loop_Down_Count, Voltage_Loop_Down_Value in enumerate(helper_functions.get_range(eva, "max_V", "min_V", "100", "nan", "nan", "start - stop", "linear", "True", "deltaV", True)):
            namespace.update({"Voltage_Loop_Down_Count": Voltage_Loop_Down_Count, "Voltage_Loop_Down_Value": Voltage_Loop_Down_Value})

            """Set_U_1"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            yield from bps.abs_set(devs["Potentiostat"].U, eva.eval("Voltage_Loop_Down_Value"), group="A")
            yield from bps.wait("A")

            """Wait_1"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            yield from bps.sleep(eva.eval("waitingtime"))

            """Read_CV_1"""
            helper_functions.update_protocol_counter(protocol_step_information)
            yield from bps.checkpoint()
            channels_Read_CV_1 = [devs["Potentiostat"].I, devs["Potentiostat"].U, Protocol_CV_Real_variable_signal]
            yield from helper_functions.trigger_and_read(channels_Read_CV_1, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False, False])

    """MintoLast"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    for MintoLast_Count, MintoLast_Value in enumerate(helper_functions.get_range(eva, "min_V", "last_V", "100", "nan", "nan", "start - stop", "linear", "True", "deltaV", True)):
        namespace.update({"MintoLast_Count": MintoLast_Count, "MintoLast_Value": MintoLast_Value})

        """SetU2"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        yield from bps.abs_set(devs["Potentiostat"].U, eva.eval("MintoLast_Value"), group="A")
        yield from bps.wait("A")

        """Wait2"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        yield from bps.sleep(eva.eval("waitingtime"))

        """readi2"""
        helper_functions.update_protocol_counter(protocol_step_information)
        yield from bps.checkpoint()
        channels_readi2 = [devs["Potentiostat"].I, devs["Potentiostat"].U, Protocol_CV_Real_variable_signal]
        yield from helper_functions.trigger_and_read(channels_readi2, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False, False])



def Protocol_CV_Real_plan(devs, md=None, runEngine=None, stream_name="primary"):
    sub_eva = runEngine.subscribe(eva)
    yield from bps.open_run(md=md)

    if web_ports:
        yield from wait_for_dash_ready_plan(web_ports)
    yield from Protocol_CV_Real_plan_inner(devs, stream_name, runEngine)
    yield from helper_functions.get_fit_results(all_fits, namespace, True)
    yield from bps.close_run()
    runEngine.unsubscribe(sub_eva)

def create_plots(RE, stream="primary"):
    global app
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    from nomad_camels.main_classes import plot_pyqtgraph, list_plot
    if darkmode:
        plot_pyqtgraph.activate_dark_mode()
    plot_evaluator = eva
    subs = []
    fits = []
    plot_info = dict(x_name="Potentiostat_U", y_names=['Potentiostat_I'], ylabel="Potentiostat_I", xlabel="Potentiostat_U", title="", stream_name=stream, evaluator=plot_evaluator, fits=fits, multi_stream=True, y_axes={'Potentiostat_I': 1}, ylabel2="", logX=False, logY=False, logY2=False, maxlen="inf", manual_plot_position=True, top_left_x="", top_left_y="", plot_width="", plot_height="", show_in_browser=False, web_port=8050)
    plot_0 = plot_pyqtgraph.PlotWidget(**plot_info)
    plots.append(plot_0)
    plot_0.show()
    for fit in plot_0.liveFits:
        all_fits[fit.name] = fit
    return plots, subs, app, plots_plotly

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
    protocol_step_information["total_protocol_steps"] = 1097
    md["user"] = {'name': 'default_user'}
    md["sample"] = {'name': 'default_sample'}
    md["session_name"] = session_name
    md["protocol_overview"] = """'StarttoMin' for (start: start_V, stop: min_V, points: 100):\n\tSet Channels 'SetU0' - {'Potentiostat_U': 'StarttoMin_Value'}\n\tWait 'Wait0' - waitingtime s\n\tRead Channels 'readi0' - ['Potentiostat_I', 'Potentiostat_U']\n'CyclesLoop' for (start: 1, stop: cycles, points: cycles):\n\t'Voltage_Loop_Up' for (start: min_V, stop: max_V, points: 100):\n\t\tSet Channels 'Set_U' - {'Potentiostat_U': 'Voltage_Loop_Up_Value'}\n\t\tWait 'Wait' - waitingtime s\n\t\tRead Channels 'Read_CV' - ['Potentiostat_I', 'Potentiostat_U']\n\t'Voltage_Loop_Down' for (start: max_V, stop: min_V, points: 100):\n\t\tSet Channels 'Set_U_1' - {'Potentiostat_U': 'Voltage_Loop_Down_Value'}\n\t\tWait 'Wait_1' - waitingtime s\n\t\tRead Channels 'Read_CV_1' - ['Potentiostat_I', 'Potentiostat_U']\n'MintoLast' for (start: min_V, stop: last_V, points: 100):\n\tSet Channels 'SetU2' - {'Potentiostat_U': 'MintoLast_Value'}\n\tWait 'Wait2' - waitingtime s\n\tRead Channels 'readi2' - ['Potentiostat_I', 'Potentiostat_U']\n"""
    md["description"] = ''
    md["measurement_tags"] = []
    md["measurement_description"] = ''
    try:
        with open("C:/Users/GuggenbergerB/AppData/Local/Programs/NOMAD-CAMELS/protocols/potentiostatprotocols/Protocol_CV_Real.cprot", "r", encoding="utf-8") as f:
            md["protocol_json"] = f.read()
    except FileNotFoundError:
        print('Could not find protocol configuration file, information will be missing in data.')
    with open(__file__, "r", encoding="utf-8") as f:
        md["python_script"] = f.read()
    md = helper_functions.get_opyd_and_py_file_contents(Potentiostat, md, 'Potentiostat')
    md["variables"] = namespace
    subscription_uid = RE.subscribe(uid_collector, "start")
    publisher_subscription = RE.subscribe(publisher)
    try:
        RE(Protocol_CV_Real_plan(devs, md=md, runEngine=RE))
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
                response = requests.get(f"http://127.0.0.1:{web_port}/status", timeout=1,)
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
    tqdm_bar = tqdm_progress_bar.ProgressBar(1097)

    protocol_step_information["protocol_stepper_signal"] = tqdm_bar
    devs = {}
    device_config = {}
    try:
        """Potentiostat (Potentiostat):
        """
        settings = {}
        additional_info = {'config_channel_metadata': {'Potentiostat_POTENTIOSTAT_COM_PORT': 'units: \ndescription: '}, 'description': '', 'ELN-instrument-id': '', 'ELN-service': '', 'ELN-metadata': {}, 'device_class_name': 'Potentiostat'}
        Potentiostat = Potentiostat("Potentiostat:", name="Potentiostat", **settings)
        print("connecting Potentiostat")
        Potentiostat.wait_for_connection()
        config = {'POTENTIOSTAT_COM_PORT': 'COM11'}
        configs = Potentiostat.configure(config)[1]
        device_config["Potentiostat"] = {"settings": {}}
        device_config["Potentiostat"]["settings"].update(helper_functions.simplify_configs_dict(configs))
        device_config["Potentiostat"]["settings"].update(settings)
        device_config["Potentiostat"].update(additional_info)
        devs.update({"Potentiostat": Potentiostat})
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
