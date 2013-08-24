import math
import numpy as np
import time

from lib.raw_preset import RawPreset
from lib.parameters import StringParameter, FloatParameter, HLSParameter
from lib.color_fade import ColorFade
from lib.colors import clip

class LeapDemo(RawPreset):

    def setup(self):
        pass
        # self.add_parameter(StringParameter('feature', 'onset'))
        # self.add_parameter(FloatParameter('speed', 100))
        # self.add_parameter(FloatParameter('width', 5))
        # self.add_parameter(FloatParameter('hue_step', 0.05))
        # self.add_parameter(FloatParameter('hue_drift', 0.01))
        # self.add_parameter(FloatParameter('hue_width', 0.2))
        # self.add_parameter(HLSParameter('color-end', (1.0, 0.5, 1.0)))

    def parameter_changed(self, parameter):
        self.feature = self.parameter('feature').get()

    def reset(self):
        self.pixel_locations = self.scene().get_all_pixel_locations()

        
    def draw(self, dt):
        frame = self._mixer.getLeapFrame()
        height = 0.0
        hand = None
        #print "Drawing: hands is: ", frame.hands

        x, y = self.pixel_locations.T
        hues = np.zeros(x.shape, float) #+ (height / 200.0)) % 1.0
        luminances = np.zeros(x.shape, float)

        if not frame.hands.empty:
            hand = frame.hands[0]
            height = hand.palm_position[1]
            hues += ((height / 200.0) % 1.0)
            luminances += 0.5
            self.setAllHLS(hues, luminances, 1)

        else:
            self.setAllHLS(hues, luminances, 1)
            
        
