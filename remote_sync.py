#!/usr/bin/env python3

"""
remote sync tool using Globus.org via globus-sdk written specifically to backup data from hiccup storage to NERSC ALICEPRO area.  

Default source is a globus personal connect server owned by the user running this code
Default destination is the NERSC ALICEPRO collaboration endpoint.  The user running this code must be authorized as a collab user of the alicepro NERSC account

code is a restructuring of code, liberally stolen from the NERSC globus-tool module

"""

from __future__ import print_function

import sys
if sys.version[0:3] < '3.0':
    print ("Python version 3.0 or greater required (found: %s)." % sys.version[0:5])
    sys.exit(-1)

import globus_sdk
import argparse, os, logging
from datetime import datetime
from getpass import getuser
from token_management import get_token
#from hpss_sort import hpss_sort

logging.basicConfig(level=os.environ.get("LOGLEVEL", "CRITICAL"))
logging.info("Started")

""" defaults """
GLOBUS_PERSONAL_HICCUP='866ba278-880f-11eb-954f-752ba7b88ebe'
GLOBUS_ALICEPRO_NERSC='8895475c-71b2-11eb-a9ad-efda19b7c028'
TRANSFER_LABEL='sync_hiccup'

#-------------------------------------------------
  
class remote_sync_client:
    """ application class"""

#-------------------------
    def __init__(self,args):
        self.out_dir=args.out_dir
        self.in_dir = args.in_dir
        self.preserve = args.preserve
        self.failifnotoken=args.failifnotoken
        self.endpoints = [args.source, args.target]
        self.baselabel=args.baselabel

#-------------------------
    def activate_client(self, tc):

        """ should only be needed once per user.  Results are a stored token in a file for future """
        
        get_input = getattr(__builtins__, 'raw_input', input)
        for ep_id in self.endpoints:
            r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
            while (r["code"] == "AutoActivationFAiled"):
                print("Endpoint requires manual activation, please open "
                      "the following URL in a browser to activate the endpoint:")
                print("https://app.globus.org/file-manager?origin_id=%s" % ep_id)
                get_input("Press ENTER after activating the endpoint:")
                r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)

#-------------------------
    def go(self):

        transfer_client = get_token(self.failifnotoken)
        self.activate_client(transfer_client)
        transfer_label = self.baselabel+"_"+datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        transfer_data = globus_sdk.TransferData(transfer_client,self.endpoints[0],self.endpoints[1],
                                                label=transfer_label,preserve_timestamp=self.preserve,
                                                sync_level="checksum")
        transfer_data.add_item(self.in_dir,self.out_dir,recursive=True)

        transfer_result = transfer_client.submit_transfer(transfer_data)
        task_id = transfer_result["task_id"]
        print("Transfer ID is",task_id,"label is",transfer_label)


#-------------------------
def main():
    """ Generic program structure to parse args, initialize and start application """

    desc = """ remote sync tool via globus-sdk, used as a backup tool from hiccup to NERSC"""

    p = argparse.ArgumentParser(description=desc, epilog="None")

# - required args
    requiredNamed = p.add_argument_group('Required arguments')
    requiredNamed.add_argument('-o',help='target endpoint output directory',required=True,dest='out_dir',type=str)
    requiredNamed.add_argument('-i',help='target endpoint input directory',required=True,dest='in_dir',type=str)

# - optional args
    optionalNamed = p.add_argument_group('Optional arguments')
    optionalNamed.add_argument('-p','--preserve',help='Preserve time stamps',required=False,dest='preserve',default=False,action='store_true')
    optionalNamed.add_argument('--failifnotoken',help=argparse.SUPPRESS,required=False,dest='failifnotoken',default=False,action='store_true')
    optionalNamed.add_argument('-s',help='source endpoint UUID (Default is globus personal connect server)',required=False, 
                                default=GLOBUS_PERSONAL_HICCUP,dest='source',type=str)
    optionalNamed.add_argument('-t',help='target endpoint UUID (Default is NERSC ALICEPRO collaboration endpoint)',required=False,
                                default=GLOBUS_ALICEPRO_NERSC,dest='target',type=str)
    optionalNamed.add_argument('-n',help='base label for transfer target (perhaps adds source details)',required=False,
                                    default=TRANSFER_LABEL,dest='baselabel',type=str)


    try:
        args = p.parse_args()
    except:
        p.print_help()
        p.exit(1)

    try:
        rsc=remote_sync_client(args)
        return(rsc.go())
    except:
        import traceback
        traceback.print_exc()
        return -1

if __name__ == "__main__":
    sys.exit(main())

