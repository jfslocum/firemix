import math
import numpy as np
import time
from lib.raw_preset import RawPreset
from lib.parameters import StringParameter, FloatParameter, HLSParameter
from lib.color_fade import ColorFade
from lib.colors import clip

class HueBeats(RawPreset):

    class BeatParticle(object):
        _fader_steps = 256
        def __init__(self, pos, fade_colors):
            self.pos = pos
            self.distance = 0
            self.color = 0
            self._fader = ColorFade(fade_colors, self._fader_steps)
            self.alive = True
            self.feature = 'onset'
            
    def setup(self):
        self.hue_offset = 0.0
        self.hue_center = 0.0
        self.beats = []
        self.add_parameter(StringParameter('feature', 'onset'))
        self.add_parameter(FloatParameter('speed', 100))
        self.add_parameter(FloatParameter('width', 5))
        self.add_parameter(FloatParameter('hue_step', 0.05))
        self.add_parameter(FloatParameter('hue_drift', 0.01))
        self.add_parameter(FloatParameter('hue_width', 0.2))
        self.add_parameter(HLSParameter('color-end', (1.0, 0.5, 1.0)))
        self.beat_time = 0

    def parameter_changed(self, parameter):
        self.feature = self.parameter('feature').get()

    def reset(self):
        self.pixel_locations = self.scene().get_all_pixel_locations()


    def fade_luminance(self):
        """
        Returns a luminance value that exponentially fades to minimal after a beat
        """
        dt = time.time() - self.beat_time #seconds since last beat
        return 0.01+clip(0.0, 0.0 + math.pow(math.e, -dt*4), 1.0)
        
    def draw(self, dt):
        x, y = self.pixel_locations.T
        hues = np.zeros(x.shape, float)
        luminances = np.zeros(x.shape, float)

        hues[:] = (self.hue_center + self.hue_offset) % 1.0
        luminances[:] = self.fade_luminance()
        
        self.setAllHLS(hues, luminances, 1)

    def on_feature(self, feature):
        if feature['feature'] == self.feature:
            self.beat_time = time.time()
            hue_step = self.parameter('hue_step').get()
            hue_drift = self.parameter('hue_drift').get()
            hue_width = self.parameter('hue_width').get()
            self.hue_offset = (self.hue_offset + hue_step) % hue_width
            self.hue_center = (self.hue_center + hue_drift) % 1.0
