import globus_sdk
import os
import json
from stat import *
import logging

home = os.environ['HOME']
token_path = home+'/.globus/token'
CLIENT_ID = 'ebe0d06d-df9c-4310-8dbb-5c3f40a891fb'


def create_token():
    """Creates access tokens manually if they don't already exist in the users home dir"""
    logging.debug("create_token: Starting")
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(refresh_tokens=True)

    authorize_url = client.oauth2_get_authorize_url()
    print('Please go to this URL and login: {0}'.format(authorize_url))

    get_input = getattr(__builtins__, 'raw_input', input)
    auth_code = get_input('Please enter the code you get after login here: ')
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    globus_auth_data = token_response.by_resource_server['auth.globus.org']
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']

    # most specifically, you want these tokens as strings
    transfer_rt = globus_transfer_data['refresh_token']
    transfer_at = globus_transfer_data['access_token']
    token = {"transfer_at":transfer_at,"transfer_rt":transfer_rt}
#    AUTH_TOKEN = globus_auth_data['access_token']
#    TRANSFER_TOKEN = globus_transfer_data['access_token']
    save_tokens_to_file(token_path,token)
    authorizer = activate_token(token)

    #need some try except stuff here

    return authorizer


def save_tokens_to_file(token_path, tokens):
    """Save a set of tokens for later use."""
    logging.debug("save_tokens_to_file: Starting")
    #Create directory if it doesn't exist already
    dirname, leaf = os.path.split(token_path)
    if not os.path.isdir(dirname):
        try:
            os.mkdir(dirname)
        except Exception as e:
            print("Error making directory:",e) 
    with open(token_path, 'w') as f:
        json.dump(tokens, f)
    os.chmod(token_path, S_IRUSR)

def load_tokens_from_file(token_path):
    """Load a set of saved tokens."""
    logging.debug("load_tokens_to_file: Starting")
    if not os.path.exists(token_path):
        return []
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return tokens

def check_token(token):
    """Check tokens from users file"""
#    from globus_sdk import AuthClient
    logging.debug("check_token: Starting")
    logging.debug("token is %s",token)
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    data = client.oauth2_validate_token(token)
    logging.debug('check_auth %s',data)
    return data['active']

def activate_token(token):
    logging.debug("activate_token: Starting")
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    authorizer = globus_sdk.RefreshTokenAuthorizer(token['transfer_rt'],client)
    logging.debug(authorizer)
    return authorizer

def check_token_file_exists(token_path):
    """Check for token file and that the permissions are only u+r"""
    logging.debug("check_token_file_exists: Starting")
    if os.path.isfile(token_path):
        #do some checking of perms here, file must be user read only (oct(0o400))
        stmode = os.stat(token_path).st_mode
        permbits = oct(stmode & 0o777)
        if permbits != oct(0o400):
            log_string = str("File " + token_path + " is not read only! Permissions are " + filemode(stmode))
            print(log_string)
            print("Exiting")
            logging.critical(log_string)
            exit()
        return True
    else: 
        return False
        
def get_token(failifnotoken=False):
    logging.debug("get_token: Starting")
    #If token file doesn't exist, then create one
    if check_token_file_exists(token_path) == False:
        if not failifnotoken:
            authorizer = create_token()
        else:
            print("No token and in non-interactive mode, exiting")
            exit()
            
    #Read in the token from the file
    token = load_tokens_from_file(token_path)

    #If token isn't activated, then activate it
    if not check_token(token):
        authorizer = activate_token(token)

    #get a transfer client that can be used to move data
    tc = globus_sdk.TransferClient(authorizer=authorizer)
    return tc

