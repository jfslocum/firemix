import sys
import logging
import argparse
import signal

from PySide import QtGui

from firemix_app import FireMixApp
from ui.firemixgui import FireMixGUI


def sig_handler(sig, frame):
    global app
    app.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    log = logging.getLogger("firemix")

    signal.signal(signal.SIGINT, sig_handler)

    parser = argparse.ArgumentParser(description="Firelight mixer and preset host")
    parser.add_argument("scene", type=str, help="Scene file to load (create scenes with FireSim)")
    parser.add_argument("--playlist", type=str, help="Playlist file to load", default=None)
    parser.add_argument("--audiobehaviors", type=str, help="Audio Behavior playlist to load", default=None)
    parser.add_argument("--speech_layer", action='store_const', const=True, default=False, help="Enable speech layer")
    parser.add_argument("--speech_playlist", type=str, help="Playlist file to load for the speech layer", default=None)
    parser.add_argument("--speech_audiobehaviors", type=str, help="Audio Behavior playlist to load for the speech layer", default=None)
    parser.add_argument("--leap_layer", action='store_const', const=True, default=False, help="Enable leap layer")
    parser.add_argument("--leap_playlist", type=str, help="Playlist file to load for the leap layer", default=None)
    parser.add_argument("--leap_audiobehaviors", type=str, help="Audio Behavior playlist to load for the leap layer", default=None)
    parser.add_argument("--profile", action='store_const', const=True, default=False, help="Enable profiling")
    parser.add_argument("--yappi", action='store_const', const=True, default=False, help="Enable YAPPI")
    parser.add_argument("--nogui", action='store_const', const=True, default=False, help="Disable GUI")
    parser.add_argument("--preset", type=str, help="Specify a preset name to run only that preset (useful for debugging)")
    parser.add_argument("--verbose", action='store_const', const=True, default=False, help="Enable verbose log output")
    parser.add_argument("--noaudio", action='store_const', const=True, default=False, help="Disable audio processing client")
    parser.add_argument("--osc_port", type=int, default=2447, help="OSC server port")
    parser.add_argument("--mixxx_osc_port", type=int, default=2448, help="Mixxx OSC server port")
    parser.add_argument("--noosc", action='store_const', const=True, default=False, help="Disable OSC server")

    parser.add_argument("--all", action='store_const', const=True, default=False, help="Enable speech layer, audo layer and leap layer")
    
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    log.info("Booting FireMix...")

    qt_app = QtGui.QApplication(sys.argv)

    app = FireMixApp(args, parent=qt_app)
    app.start()

    if not args.nogui:
        gui = FireMixGUI(app=app)
        gui.show()

    qt_app.exec_()

    if args.profile:
        print   "------ TICK TIME HISTOGRAM ------"
        elapsed = (app.mixer._stop_time - app.mixer._start_time)
        print "%d frames in %0.2f seconds (%0.2f FPS) " %  (app.mixer._num_frames, elapsed, app.mixer._num_frames / elapsed)
        for c in sorted(app.mixer._tick_time_data.iterkeys()):
            print "[%d fps]:\t%4d\t%0.2f%%" % (c, app.mixer._tick_time_data[c], (float(app.mixer._tick_time_data[c]) / app.mixer._num_frames) * 100.0)
