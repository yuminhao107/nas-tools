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
    
    client=aria2p.Client(
        host=rpc_host,
        port=port,
        secret=secreat
    )
    aria2 = aria2p.API(client)
    options=client.get_global_option()
    options['max_connection_per_server']=1
    base_dir=options['dir']
    if not base_dir.endswith('/'):
        base_dir=base_dir+'/'
    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE
    class EventHandler(pyinotify.ProcessEvent):
        mask=None
        wm=None

        def my_init(wm=None,mask=None):
            EventHandler.wm=wm
            EventHandler.mask=mask

        def process_IN_CREATE(self,event):
            if len(event.name)==0:
                EventHandler.wm.add_watch(event.path,mask,rec=False)

        def process_IN_CLOSE_WRITE(self, event):
            if len(event.name) > 0:
                ralative_url=event.pathname[len(watch_path):]
                download_url=url_pre+ralative_url
                if '/' in ralative_url:
                    ralative_dir=event.path[len(watch_path):]
                    options['dir']=base_dir+ralative_dir
                else:
                    options['dir']=base_dir
                uris=[download_url,]
                print ("Download: "+download_url)
                # aria2.add_uris(uris,options=options)

    

    handler = EventHandler(wm=wm,mask=mask)

    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(watch_path, mask, rec=True)

    notifier.loop()

if __name__=="__main__":
    main()