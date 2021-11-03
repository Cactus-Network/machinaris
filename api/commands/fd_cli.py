#
# Performs a daily NFT wins recovery using fd-cli: https://github.com/Flora-Network/flora-dev-cli
#

import datetime
import os
import sqlite3
import time
import traceback

from subprocess import Popen, TimeoutExpired, PIPE

from common.config import globals
from api import app

# No need to reward recover for either Chia or Chives
def get_rpc_port(blockchain):
    if blockchain == 'flax':
        return 6759
    if blockchain == 'flora':
        return 18759
    if blockchain == 'hddcoin':
        return 28559
    if blockchain == 'nchain':
        return 38559
    if blockchain == 'silicoin':
        return 11000
    if blockchain == 'cactus':
        return 11559
    raise Exception(f"Unknown rpc_port for blockchain: {blockchain}")

def reward_recovery(wallet_id, launcher_id, pool_contract_address):
    app.logger.info("NFT reward recovery requested for {wallet_id} {launcher_id} {pool_contract_address}")
    logfile = "/root/.chia/machinaris/logs/fd-cli.log"
    log_fd = os.open(logfile, os.O_RDWR | os.O_CREAT)
    log_fo = os.fdopen(log_fd, "a+")
    vars = {}
    blockchain = globals.enabled_blockchains()[0]
    mainnet = globals.get_blockchain_mainnet(blockchain)
    vars['FD_CLI_BC_DB_PATH'] = f'{mainnet}/db/blockchain_v1_mainnet.sqlite'
    vars['FD_CLI_WT_DB_PATH'] = f'{mainnet}/wallet/db/blockchain_wallet_v1_mainnet_{wallet_id}.sqlite'
    fd_env = os.environ.copy()
    fd_env.update(vars)
    rpc_port = get_rpc_port(blockchain)
    cmd = f"/usr/local/bin/fd-cli nft-recover -l {launcher_id} -p {pool_contract_address} -nh 127.0.0.1 -np {rpc_port} -ct {mainnet}/config/ssl/full_node/private_full_node.crt -ck {mainnet}/config/ssl/full_node/private_full_node.key"
    app.logger.info(f"Executing NFT 1/8 win recovery for {blockchain}: {cmd}")
    log_fo.write("\n{0} --> Executed at: {1}\n".format(cmd, time.strftime("%Y%m%d-%H%M%S")))
    proc = Popen(cmd,cwd="/fd-cli", env=fd_env, shell=True, universal_newlines=True, stdout=log_fo, stderr=log_fo)
    try:
        outs, errs = proc.communicate(timeout=1800)
    except TimeoutExpired:
        proc.kill()
        proc.communicate()
    if errs:
        app.logger.error(errs.decode('utf-8'))
    elif outs:
        app.logger.info(outs.decode('utf-8'))
    else:
        app.logger.error("Nothing returned from fd-cli call.")
