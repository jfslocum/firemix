import logging

from PySide import QtCore

from core.mixer import Mixer
from core.networking import Networking
from core.scene_loader import SceneLoader
from lib.settings import Settings
from lib.scene import Scene
from lib.plugin_loader import PluginLoader
from lib.aubio_connector import AubioConnector
from lib.osc_server import OscServer
from lib.buffer_utils import BufferUtils
from lib.specialLayers import MusicLayer, SpeechLayer, LeapLayer
from lib.playlist import Playlist
from lib.audiolist import Audiolist

log = logging.getLogger("firemix")


class FireMixApp(QtCore.QThread):
    """
    Main logic of FireMix.  Operates the mixer tick loop.
    """
    def __init__(self, args, parent=None):
        self._running = False
        self.args = args
        self.settings = Settings()
        self.net = Networking(self)
        BufferUtils.set_app(self)
        self.scene = Scene(self)
        self.plugins = PluginLoader()
        self.mixer = Mixer(self)

        # Create the default layer.
        default_playlist = Playlist(self, self.args.playlist, 'last_playlist',
                                    subdir = 'Music')
        default_audiolist = Audiolist(self, self.args.audiobehaviors, 'last_audiolist',
                                      subdir = 'Music')
        default_layer = MusicLayer(self)
        default_layer.set_playlist(default_playlist)
        default_layer.set_audiolist(default_audiolist)
        default_layer.setForeground()
        self.mixer.add_layer(default_layer)

        if self.args.speech_layer or self.args.all:
            speech_playlist = Playlist(self, self.args.speech_playlist,
                                       'last_speech_playlist', subdir = 'Speech')
            speech_audiolist = Audiolist(self, self.args.speech_audiobehaviors,
                                         'last_speech_audiolist', subdir = 'Speech')
            speech_layer = SpeechLayer(self)
            speech_layer.set_playlist(speech_playlist)
            speech_layer.set_audiolist(speech_audiolist)
            speech_layer.setBackground()
            self.mixer.add_layer(speech_layer)

        if self.args.leap_layer or self.args.all:
            leap_playlist = Playlist(self, self.args.leap_playlist,
                                     'last_leap_playlist', subdir = 'Leap')
            leap_audiolist = Audiolist(self, self.args.leap_audiobehaviors,
                                       'last_leap_audiolist', subdir = 'Leap')
            leap_layer = LeapLayer(self)
            leap_layer.set_playlist(leap_playlist)
            leap_layer.set_audiolist(leap_audiolist)
            leap_layer.setBackground()
            self.mixer.add_layer(leap_layer)
            

        self.scene.warmup()

        self.aubio_connector = None
        if not self.args.noaudio:
            self.aubio_connector = AubioConnector()
            self.aubio_connector.onset_detected.connect(self.mixer.onset_detected)

        self.osc_server = None
        if not self.args.noosc:
            self.osc_server = OscServer(
                self.args.osc_port, self.args.mixxx_osc_port, self.mixer)
            self.osc_server.start()

        if self.args.preset:
            log.info("Setting constant preset %s" % args.preset)
            self.mixer.set_constant_preset(args.preset)

        QtCore.QThread.__init__(self, parent)

    def run(self):
        self._running = True
        self.mixer.run()

    def stop(self):
        self._running = False
        self.mixer.stop()
        self.mixer.save()
        self.settings.save()
