# globus_sync_client
sync remote filesystems using globus-sdk


To use, set PATH & PYTHONPATH to installation and PYTHONPATH to globus-sdk site-package

usage: remote_sync.py [-h] -o OUT_DIR -i IN_DIR [-p] [-s SOURCE] [-t TARGET]
                      [-n BASELABEL]

remote sync tool via globus-sdk, used as a backup tool from hiccup to NERSC

help arguments:
    -h, --help      show this help message and exit


    Required arguments:
        -o OUT_DIR      target endpoint output directory
        -i IN_DIR       target endpoint input directory

    Optional arguments:
        -p, --preserve  Preserve time stamps
        -s SOURCE       source endpoint UUID (Default is globus personal connect
                                                          server)
        -t TARGET       target endpoint UUID (Default is NERSC ALICEPRO
                                                            collaboration endpoint)
        -n BASELABEL    base label for transfer target (perhaps adds source details)

