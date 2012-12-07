import wx
import MplayerCtrl as mpc

class Frame(wx.Frame):
    def __init__(self, parent, id, title, mplayer, media_file):
        wx.Frame.__init__(self, parent, id, title)

        self.mpc = mpc.MplayerCtrl(self, -1, mplayer, media_file)

        self.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        self.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        self.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        self.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)

        self.Bind(mpc.EVT_STDERR, self.on_stderr)

        self.Show()

    def on_process_started(self, evt):
        print 'Process started'
    def on_media_started(self, evt):
        print 'Media started'
    def on_media_finished(self, evt):
        print 'Media finished'
        self.mpc.Quit()
    def on_process_stopped(self, evt):
        print 'Process stopped'

    def on_stderr(self, evt):
        print 'oh oh some errors:'
        print '==>', evt.data

if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = Frame(None, -1, 'Hello MplayerCtrl', u'mplayer', u'/home/cgarcia/Videos/HCOROMOTO/VTS_01_1.VOB')
    app.MainLoop()
