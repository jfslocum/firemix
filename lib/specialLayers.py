from layer import Layer



class SpeechLayer(Layer):
    def __init__(self, app, name="Speech"):
        super(SpeechLayer, self).__init__(app, name)

    def setVolume(self, volume):
        """Set volume for mixxx emitters that play speeches"""
        raise NotImplementedError
        
    def setForeground(self):
        self.foreground = True
        self.enable()

    def setBackground(self):
        self.foreground = False
        self.disable()


class MusicLayer(Layer):
    def __init__(self, app, name="Music"):
        super(MusicLayer, self).__init__(app, name)

    def setVolume(self, volume):
        """Set volume for mixxx emitters that play the music"""
        raise NotImplementedError


    # def setForeground(self):
    #     pass

    # def setBackground(self):
    #     pass



class LeapLayer(Layer):
    def __init__(self, app, name="Leap"):
        #TODO: Am I doing this right? (calling parent's constructor)
        super(LeapLayer, self).__init__(app, name)

    # def setForeground(self):
    #     pass
    def setVolume(self, volume):
        raise NotImplementedError

        
    def setBackground(self):
        self.foreground = False
        self.volumeGain = 0.0 #no leap sounds when in background
        self.lightGain = 0.2 

    
