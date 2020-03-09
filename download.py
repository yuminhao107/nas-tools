import pyinotify
import sys
import os
import aria2p

def main():
    if len(sys.argv) < 6:
        print("Script needs 6 arguments")
        return
    watch_path=sys.argv[1]
    if not watch_path.endswith('/'):
        watch_path=watch_path+'/'
    rpc_host=sys.argv[2]
    port=int(sys.argv[3])
    secreat=sys.argv[4]
    url_pre=sys.argv[5]
    if not url_pre.endswith('/'):
        url_pre=url_pre+'/'
    
    aria2 = aria2p.API(
    aria2p.Client(
        host=rpc_host,
        port=port,
        secret=secreat
    )
)
    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_CLOSE_WRITE 
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            if len(event.name) > 0:
                download_url=url_pre+event.pathname[len(watch_path):]
                uris=[download_url,]
                print ("Download: "+download_url)
                aria2.add_uris(uris)

    handler = EventHandler()

    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(watch_path, mask, rec=True)

    notifier.loop()

if __name__=="__main__":
    main()