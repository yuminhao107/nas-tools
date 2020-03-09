import pyinotify
import sys
import os

def main():
    if len(sys.argv) < 4:
        print("Script needs 3 arguments")
        return
    watch_path=sys.argv[1]
    remote_path=sys.argv[2]
    if not remote_path.endswith('/'):
        remote_path=remote_path+'/'
    port=int(sys.argv[3])

    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_CLOSE_WRITE 
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            # print ("Close: "+str(event.pathname))
            os.system('scp -P {0} {1} {2}'.format(port,event.pathname,remote_path))
            os.system('rm '+str(event.pathname))

    handler = EventHandler()

    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(watch_path, mask, rec=True)

    notifier.loop()

if __name__=="__main__":
    main()