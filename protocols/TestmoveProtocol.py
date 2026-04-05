import sys
sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\.desertenv\Lib\site-packages")
sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\.desertenv\Lib\site-packages/nomad_camels")
sys.path.append(r"C:/Users/GuggenbergerB/AppData/Local/Programs/NOMAD-CAMELS/camels_drivers")

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
save_path = "C:/Users/GuggenbergerB/Documents/NOMAD_CAMELS_data/default_user/testsample/data"
session_name = ""
export_to_csv = False
export_to_json = False
new_file_each_run = True
new_file_hours = 0
do_nexus_output = False

TestmoveProtocol_variable_signal = variable_reading.Variable_Signal(name="TestmoveProtocol_variable_signal", variables_dict=namespace)
aliases = {}
eva = Evaluator(namespace=namespace, aliases=aliases)



sys.path.append(r"C:\Users\GuggenbergerB\AppData\Local\Programs\NOMAD-CAMELS\camels_drivers\xy")
from nomad_camels_driver_xy.xy_ophyd import Xy




def TestmoveProtocol_plan_inner(devs, stream_name="primary", runEngine=None):

    """connect"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    channels_connect = [devs["xy"].connect, TestmoveProtocol_variable_signal]
    yield from helper_functions.trigger_and_read(channels_connect, name=stream_name if stream_name == stream_name else f"{stream_name}||sub_stream||stream_name", skip_on_exception=[False, False])

    """testmove"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    channels_testmove = [devs["xy"].testmove, TestmoveProtocol_variable_signal]
    yield from helper_functions.trigger_and_read(channels_testmove, name=f"{stream_name}_1" if stream_name == f"{stream_name}_1" else f"{stream_name}||sub_stream||{stream_name}_1", skip_on_exception=[False, False])

    """disconnect"""
    helper_functions.update_protocol_counter(protocol_step_information)
    yield from bps.checkpoint()
    channels_disconnect = [devs["xy"].disconnect, TestmoveProtocol_variable_signal]
    yield from helper_functions.trigger_and_read(channels_disconnect, name=f"{stream_name}_2" if stream_name == f"{stream_name}_2" else f"{stream_name}||sub_stream||{stream_name}_2", skip_on_exception=[False, False])



def TestmoveProtocol_plan(devs, md=None, runEngine=None, stream_name="primary"):
    sub_eva = runEngine.subscribe(eva)
    yield from bps.open_run(md=md)

    if web_ports:
        yield from wait_for_dash_ready_plan(web_ports)
    yield from TestmoveProtocol_plan_inner(devs, stream_name, runEngine)
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
    protocol_step_information["total_protocol_steps"] = 3
    md["user"] = {'name': 'default_user'}
    md["sample"] = {'name': 'testsample', 'sample_id': 1, 'description': 1, 'owner': 'default_user', 'display_name': 'testsample / 1'}
    md["session_name"] = session_name
    md["protocol_overview"] = """Read Channels 'connect' - ['xy_connect']\nRead Channels 'testmove' - ['xy_testmove']\nRead Channels 'disconnect' - ['xy_disconnect']\n"""
    md["description"] = ''
    md["measurement_tags"] = []
    md["measurement_description"] = ''
    try:
        with open("C:/Users/GuggenbergerB/AppData/Local/Programs/NOMAD-CAMELS/protocols/TestmoveProtocol.cprot", "r", encoding="utf-8") as f:
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
        RE(TestmoveProtocol_plan(devs, md=md, runEngine=RE))
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
    tqdm_bar = tqdm_progress_bar.ProgressBar(3)

    protocol_step_information["protocol_stepper_signal"] = tqdm_bar
    devs = {}
    device_config = {}
    try:
        """xy (Xy):
        """
        settings = {}
        additional_info = {'config_channel_metadata': {}, 'description': '', 'ELN-instrument-id': '1', 'ELN-service': '', 'ELN-metadata': {}, 'device_class_name': 'Xy'}
        xy = Xy("xy:", name="xy", **settings)
        print("connecting xy")
        xy.wait_for_connection()
        config = {}
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
