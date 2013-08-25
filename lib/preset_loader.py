import os
import logging
import inspect

# from lib.preset import Preset
# from lib.audio_behavior import AudioBehavior
log = logging.getLogger("firemix.lib.preset_loader")


class Loader:
    """
    Scans the given directory and imports all the objects inheriting from a specified class.

    Based on code copyright 2005 Jesse Noller <jnoller@gmail.com>
    http://code.activestate.com/recipes/436873-import-modulesdiscover-methods-from-a-directory-na/
    """

    def __init__(self, objects_directory, superclass, interface_names=None):
        if interface_names is None:
            interface_names = [superclass.__name__]
        self.modules = []
        self.objects = []
        self.objects_directory = objects_directory
        self.superclass = superclass
        self.interface_names = interface_names

    def load(self):
        self.modules = []
        self.objects = []
        log.info("Loading objects...")
        for f in os.listdir(os.path.join(os.getcwd(), self.objects_directory)):
            module_name, ext = os.path.splitext(f)
            if ext == ".py":
                # Skip emacs lock files.
                if f.startswith('.#'):
                    continue
                print "Loading module ", self.objects_directory+"." + module_name
                module = __import__(self.objects_directory+"." + module_name, fromlist=['dummy'])
                self.modules.append(module)
                self.load_from_modules(module)
        log.info("Loaded %d objects." % len(self.objects))
        return dict([(i.__name__, i) for i in self.objects])

    def reload(self):
        """Reloads all object modules"""
        self.objects = []
        for module in self.modules:
            reload(module)
            self.load_from_modules(module)
        return dict([(i.__name__, i) for i in self.objects])

    def load_from_modules(self, module):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, self.superclass) and name not in self.interface_names:
                log.info("Loaded %s" % obj.__name__)
                print "loaded class ", name
                self.objects.append(obj)



