import os
import gc
import logging
import random

from PySide import QtCore

from lib.json_dict import JSONDict
from lib.preset_loader import Loader
from audio_behavior import AudioBehavior

class Audiolist(JSONDict):
    """
    Manages the available behaviors and the current audiolist of behaviors.
    """

    class Notifier(QtCore.QObject):
        audiolist_changed = QtCore.Signal()

    
    def __init__(self, app, name, last_audiolist_settings_key, subdir = ''):
        self._app = app
        self.last_audiolist_settings_key = last_audiolist_settings_key
        self.name = name
        self._notifier = Audiolist.Notifier()
        if self.name is None:
            self.name = self._app.settings.get("mixer").get(
                self.last_audiolist_settings_key, "default")
        filepath = os.path.join(os.getcwd(), "data", "playlists", subdir, 'audio',
                                "".join([self.name, ".json"]))
        JSONDict.__init__(self, 'audiolist', filepath, True)

        self.open()

    def set_filename(self, filename):
        self.name = os.path.split(filename)[1].replace(".json", "")
        self.filename = filename

    def open(self):
        try:
            self.load(False)
        except ValueError:
            print "Error loading %s" % self.filename
            return False

        self._loader = Loader('behaviors', AudioBehavior, interface_names=['AudioBehavior'])
        self._behavior_classes = self._loader.load()
        self._audiolist_data = self.data.get('audiolist', [])
        self._audiolist = []

        self._active_index = 0
        self._next_index = 0
        self._shuffle = self._app.settings['mixer']['shuffle']
        self._shuffle_list = []

        self.generate_audiolist()

        self._notifier.audiolist_changed.emit()
        return True

    def generate_audiolist(self):
        """Creates an instance of each audioBehavior object used in the playlist"""
        if len(self._audiolist_data) == 0:
            self._audiolist = []

        for entry in self._audiolist_data:
            if entry['classname'] in self._behavior_classes:

                inst = self._behavior_classes[entry['classname']](self._app.mixer, name=entry['name'])
                inst._reset()

                for _, key in enumerate(entry.get('params', {})):
                    try:
                        inst.parameter(key).set_from_str(str(entry['params'][key]))
                    except AttributeError:
                        log.warn("Parameter %s called out in audiolist but not found in plugin.  Perhaps it was renamed?" % key)
                self._audiolist.append(inst)
            else:
                self._audiolist_data.remove(entry)

        self._active_index = 0
        if self._shuffle and len(self._audiolist) > 1:
            self.generate_shuffle()
            self._next_index = self._shuffle_list.pop()
        else:
            self._next_index = 0 if len(self._audiolist) == 0 else 1 % len(self._audiolist)

        return self._audiolist

    def shuffle_mode(self, shuffle=True):
        """
        Enables or disables audiolist shuffle
        """
        self._shuffle = shuffle

    def generate_shuffle(self):
        """
        Creates a shuffle list
        """
        self._shuffle_list = range(len(self._audiolist))
        random.shuffle(self._shuffle_list)
        if self._active_index in self._shuffle_list:
            self._shuffle_list.remove(self._active_index)

    def reload_behaviors(self):
        """Attempts to reload all behavior classes in the audiolist"""
        old_active = self._active_index
        old_next = self._next_index
        self._behavior_classes = self._loader.reload()
        while len(self._audiolist) > 0:
            inst = self._audiolist.pop(0)
            inst.clear_parameters()
            del inst

        gc.collect()
        self.generate_audiolist()
        self._active_index = old_active % len(self._audiolist)
        self._next_index = old_next % len(self._audiolist)
        self._notifier.audiolist_changed.emit()

    # def save(self):
    #     log.info("Saving audiolist")
    #     # Pack the current state into self.data
    #     self.data = {'file-type': 'audiolist'}
    #     audiolist = []
    #     for behavior in self._audiolist:
    #         audiolist_entry = {'classname': behavior.__class__.__name__,
    #                           'name': behavior.get_name()}
    #         param_dict = {}
    #         for name, param in behavior.get_parameters().iteritems():
    #             param_dict[name] = param.get_as_str()
    #         audiolist_entry['params'] = param_dict
    #         audiolist.append(audiolist_entry)
    #     self.data['audiolist'] = audiolist
    #     # Superclass write to file
    #     self._app.settings.get("mixer")[self._last_audiolist_settings_key] = self.name
    #     JSONDict.save(self)

    def get(self):
        return self._audiolist

    def advance(self, direction=1):
        """
        Advances the audiolist
        """
        #TODO: support transitions other than cut
        self._active_index = self._next_index

        if self._shuffle:
            if len(self._shuffle_list) == 0:
                self.generate_shuffle()
            self._next_index = self._shuffle_list.pop()
        else:
            self._next_index = (self._next_index + direction) % len(self._audiolist)

        self._notifier.audiolist_changed.emit()

    def __len__(self):
        return len(self._audiolist)

    def get_active_index(self):
        return self._active_index

    def get_next_index(self):
        return self._next_index

    def get_active_behavior(self):
        if len(self._audiolist) == 0:
            return None
        else:
            return self._audiolist[self._active_index]

    def get_behavior_relative_to_active(self, pos):
        """
        Returns the behavior name of a behavior relative to the active behavior by an offset of pos
        For exapmle, get_behavior_relative_to_active(1) would return the next in the audiolist
        """
        return self._audiolist[(self._active_index + pos) % len(self._audiolist)].get_name()

    def get_next_behavior(self):
        if len(self._audiolist) == 0:
            return None
        else:
            return self._audiolist[self._next_index]

    def get_behavior_by_index(self, idx):
        if len(self._audiolist) == 0:
            return None
        else:
            return self._audiolist[idx]

    def get_behavior_by_name(self, name):
        for behavior in self._audiolist:
            if behavior.get_name() == name:
                return behavior
        return None

    def set_active_index(self, idx):
        self._active_index = idx % len(self._audiolist)
        self._next_index = (self._active_index + 1) % len(self._audiolist)
        self.get_active_behavior()._reset()
        self._notifier.audiolist_changed.emit()

    def set_active_behavior_by_name(self, name):
        #TODO: Support transitions other than jump cut
        for i, behavior in enumerate(self._audiolist):
            if behavior.get_name() == name:
                behavior._reset()
                self._active_index = i
                self._app.mixer._elapsed = 0.0  # Hack
                self._notifier.audiolist_changed.emit()
                return

    def set_next_behavior_by_name(self, name):
        for i, behavior in enumerate(self._audiolist):
            if behavior.get_name() == name:
                self._next_index = i
                self._notifier.audiolist_changed.emit()
                return

    def reorder_audiolist_by_names(self, names):
        """
        Pass in a list of behavior names to reorder.
        """
        current = dict([(behavior.get_name(), behavior) for behavior in self._audiolist])

        new = []
        for name in names:
            new.append(current[name])

        self._audiolist = new
        self._notifier.audiolist_changed.emit()

    def get_available_behaviors(self):
        return self._behavior_classes.keys()

    def behavior_name_exists(self, name):
        return True if name in [p.get_name() for p in self._audiolist] else False

    def add_behavior(self, classname, name, idx=None):
        """
        Adds a new behavior instance to the audiolist.  Classname must be a currently loaded
        behavior class.  Name must be unique.  If idx is specified, the behavior will be inserted
        at the position idx, else it will be appended to the end of the audiolist.
        """
        if classname not in self._behavior_classes:
            log.error("Tried to add nonexistent behavior class %s" % classname)
            return False

        if self.behavior_name_exists(name):
            return False

        inst = self._behavior_classes[classname](self._app.mixer, name=name)
        inst._reset()

        if idx is not None:
            self._audiolist.insert(idx, inst)
        else:
            self._audiolist.append(inst)

        if self._active_index == self._next_index:
            self._next_index = (self._next_index + 1) % len(self._audiolist)

        self._notifier.audiolist_changed.emit()
        return True

    def remove_behavior(self, name):
        """
        Removes an existing instance from the audiolist
        """
        if not self.behavior_name_exists(name):
            return False

        pl = [(i, p) for i, p in enumerate(self._audiolist) if p.get_name() == name]
        assert len(pl) == 1

        self._audiolist.remove(pl[0][1])

        self._next_index = self._next_index % len(self._audiolist)
        self._active_index = self._active_index % len(self._audiolist)
        self._notifier.audiolist_changed.emit()
        return True

    def clone_behavior(self, old_name):
        old = self.get_behavior_by_name(old_name)
        classname = old.__class__.__name__
        new_name = old_name + " clone"
        self.add_behavior(classname, new_name, self.get_active_index())
        new = self.get_behavior_by_name(new_name)

        for name, param in old.get_parameters().iteritems():
            new.parameter(name).set_from_str(param.get_as_str())
        self._notifier.audiolist_changed.emit()

    def clear_audiolist(self):
        self._audiolist = []
        self._active_index = 0
        self._next_index = 0
        self._notifier.audiolist_changed.emit()

    def rename_behavior(self, old_name, new_name):
        pl = [i for i, p in enumerate(self._audiolist) if p.get_name() == old_name]
        if len(pl) != 1:
            return False
        self._audiolist[pl[0]].set_name(new_name)
        self._notifier.audiolist_changed.emit()

    def generate_default_audiolist(self):
        """
        Wipes out the existing audiolist and adds one instance of each behavior
        """
        self.clear_audiolist()
        for cn in self._behavior_classes:
            name = cn + "-1"
            inst = self._behavior_classes[cn](self._app.mixer, name=name)
            inst.setup()
            self._audiolist.append(inst)
        self._notifier.audiolist_changed.emit()

    def suggest_behavior_name(self, classname):
        """
        Returns an unused behavior name based on the classname, in the form "Classname-N",
        where N is an integer.
        """
        i = 1
        name = classname + "-" + str(i)
        while self.behavior_name_exists(name):
            i += 1
            name = classname + "-" + str(i)
        return name
