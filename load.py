"""
The "Cargo Operation Tracker" Plugin
"""
try: #py3
    import tkinter as tk
except: #py2
    import Tkinter as tk
import sys
import time

this = sys.modules[__name__]  # For holding module globals

CFG_CARGO_OPERATION_TRACKER = "CargoOperationTracker"

class DockingOperation(object):
    """
    Represents docking operation
    """
    station = ""
    time = time.time()

class CargoOperationTracker(object):
    """
    The main class for the hourlyincome plugin
    """
    enabled = True
    header_widget = None
    operations_widget = None
    hauler_widget = None
    job_widget = None
    toggle_widget = None
    operations = []
    cargo = {}
    station = "Current Station"
    hauler = "Default Hauler"
    job = "Default Job"

    last_unknown_transaction = None

    def toggle(self):
        self.enabled = not self.enabled
        self.save()
        self.update_window()

    def reset(self):
        """
        Reset button pressed
        :return:
        """
        self.operations = []
        self.update_window()
        self.save()

    def load(self):
        """
        Load saved earnings from config
        :return:
        """
        return
    
    def save(self):
        """
        Save the saved earnings to config
        :return:
        """
        return
    
    def register_docking(self, station):
        """
        Record a transaction
        :param earnings:
        :return:
        """
        self.station = station
        self.update_window()

    def getOperation(self, inventory, cmdr, station):
        if inventory is None:
            return
        dict1 = {item["Name"]: item["Count"] for item in self.cargo}
        dict2 = {item["Name"]: item["Count"] for item in inventory}
        all_names = set(dict1.keys()) | set(dict2.keys())
        for name in all_names:
            count1 = dict1.get(name, 0)  # Pobierz amount z pierwszej, domyślnie 0
            count2 = dict2.get(name, 0)  # Pobierz amount z drugiej, domyślnie 0
            delta = count2 - count1
            if delta != 0:
                return {"Name": name, "Delta": delta, "Cmdr": cmdr, "Station": station}
        return None

    def register_cargo_operation(self, entry, cmdr, station):
        inventory = entry["Inventory"]
        operation = self.getOperation(inventory, cmdr=cmdr, station=station)

        if operation is not None:
             self.operations.append(operation)

        self.cargo = inventory

        self.update_window()
        self.save()

    def update_window(self):
        """
        Update the EDMC window
        :return:
        """
        self.update_operations()
        self.update_toggle()

    def update_toggle(self):
        if self.toggle_widget is None:
            # tk.messagebox.showinfo("Cargo", "No toggle widget")
            return
        if self.enabled:
            self.toggle_widget.config(text="Disable")
            self.header_widget.config(background='green')
            
        else:
            self.toggle_widget.config(text="Enable")
            self.header_widget.config(background='red')
    
    def tonage(self):
        tonage = 0
        for operation in self.operations:
            if operation["Delta"] < 0 :
                tonage += abs(operation["Delta"])
        return tonage
    
    def deliveres(self):
        deliveres = 0
        # tk.messagebox.showinfo("Operations", "{}".format(self.operations))
        for operation in self.operations:
            if operation["Delta"] < 0:
                deliveres += 1
        return deliveres
    
    def update_operations(self):
        if self.operations_widget is None:
            return
        if self.operations == []:
            msg = "..."
        else:
            msg = "Dlv: {} Wgt: {}".format(self.deliveres(), self.tonage())
        self.operations_widget.config(text = msg)

    def update_hauler(self, event=None):
        if self.hauler_widget is None:
            return
        self.hauler = self.hauler_widget.get()
    
def plugin_start():
    cargo_operation_tracker = CargoOperationTracker()
    this.cargo_operation_tracker = cargo_operation_tracker

def plugin_start3(plugin_dir):
    cargo_operation_tracker = CargoOperationTracker()
    this.cargo_operation_tracker = cargo_operation_tracker

def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    """
    cargo_operation_tracker  = this.cargo_operation_tracker
    frame = tk.Frame(parent)
    cargo_operation_tracker.header_widget = tk.Label(frame, text="SCC Operation Tracker", background='white', foreground='black', font=('Helvetica', 10))
    cargo_operation_tracker.header_widget.grid(row=0, column=0, sticky=tk.NSEW)

    cargo_operation_tracker.toggle_widget = tk.Button(frame, text="Disable", command=cargo_operation_tracker.toggle)
    cargo_operation_tracker.toggle_widget.grid(row=0, column=1, sticky=tk.NSEW)

    reset_btn = tk.Button(frame, text="Reset", command=cargo_operation_tracker.reset)
    reset_btn.grid(row=0, column=2, sticky=tk.NSEW)

    cargo_operation_tracker.operations_widget = tk.Label(
        frame,
        text="...",
        justify=tk.RIGHT)
    
    cargo_operation_tracker.operations_widget.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

    this.spacer = tk.Frame(frame)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=2)
    
    cargo_operation_tracker.update_window()
    return frame

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Process a journal event
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    if not this.cargo_operation_tracker.enabled:
        return
    # tk.messagebox.showinfo("Operations", "{} @ {}".format(cmdr, station))
    if "event" in entry:
        if "Docked" in entry["event"]:
            this.cargo_operation_tracker.register_docking(entry["StationName"])
        elif "Cargo" in entry["event"]:
            this.cargo_operation_tracker.register_cargo_operation(entry)
