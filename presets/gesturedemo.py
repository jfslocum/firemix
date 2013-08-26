import math
import numpy as np
import time

from lib.raw_preset import RawPreset
from lib.parameters import StringParameter, FloatParameter, HLSParameter
from lib.color_fade import ColorFade
from lib.colors import clip

class GestureDemo(RawPreset):
    class GestureParticle:
        def __init__(self, position, velocity, lifespan, color_list):
            self.position = position
            self.velocity = velocity
            self.lifespan = lifespan
            self.color_list = color_list

    
    def setup(self):
        self.particles = []
        self.active_gestures = {}
        # self.add_parameter(StringParameter('feature', 'onset'))
        # self.add_parameter(FloatParameter('hue_width', 0.2))
        # self.add_parameter(HLSParameter('color-end', (1.0, 0.5, 1.0)))

    def parameter_changed(self, parameter):
        self.feature = self.parameter('feature').get()

    def reset(self):
        self.pixel_locations = self.scene().get_all_pixel_locations()
        self.particles = []
        self.active_gestures = {}

    def animateParticles(self):
        
        
    def draw(self, dt):
        frame = self._mixer.getLeapFrame()
        swipes = [gesture if gesture.type == 1 for gesture in frame.gestures()]

        hues = np.zeros(x.shape, float) #+ (height / 200.0)) % 1.0
        luminances = np.zeros(x.shape, float)

        if len(swipes) > 0:
            #do cool stuff
            pass

        self.animateParticles()
        self.setAllHLS(hues, luminances, 1) #blank frame
            
        
