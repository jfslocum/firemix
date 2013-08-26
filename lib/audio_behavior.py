class AudioBehavior:
    def __init__(self, mixer, name=""):
        self.mixer = mixer
        self.name = name
        self.setup()
        

    def setup(self):
        """Override this method for initialization"""
        pass

    def tick(self, dt):
        """Override this method to do something interesting with the audio emitters"""
        pass

    def on_feature(self, feature):
        """Called when the mixer receives a new feature report."""
        return

    
