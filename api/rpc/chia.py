#
# RPC interactions with Chia/Fork
#

import asyncio
import datetime
import importlib

if importlib.util.find_spec("chia"):
    from chia.rpc.full_node_rpc_client import FullNodeRpcClient
    from chia.rpc.farmer_rpc_client import FarmerRpcClient
    from chia.util.default_root import DEFAULT_ROOT_PATH
    from chia.util.ints import uint16
    from chia.util.config import load_config as load_fork_config
elif importlib.util.find_spec("chives"):
    from chives.rpc.full_node_rpc_client import FullNodeRpcClient
    from chives.rpc.farmer_rpc_client import FarmerRpcClient
    from chives.rpc.harvester_rpc_client import HarvesterRpcClient
    from chives.util.default_root import DEFAULT_ROOT_PATH
    from chives.util.ints import uint16
    from chives.util.config import load_config as load_fork_config
elif importlib.util.find_spec("flax"):
    from flax.rpc.full_node_rpc_client import FullNodeRpcClient
    from flax.rpc.farmer_rpc_client import FarmerRpcClient
    from flax.util.default_root import DEFAULT_ROOT_PATH
    from flax.util.ints import uint16
    from flax.util.config import load_config as load_fork_config
elif importlib.util.find_spec("flora"):
    from flora.rpc.full_node_rpc_client import FullNodeRpcClient
    from flora.rpc.farmer_rpc_client import FarmerRpcClient
    from flora.util.default_root import DEFAULT_ROOT_PATH
    from flora.util.ints import uint16
    from flora.util.config import load_config as load_fork_config
elif importlib.util.find_spec("cactus"):
    from cactus.rpc.full_node_rpc_client import FullNodeRpcClient
    from cactus.rpc.farmer_rpc_client import FarmerRpcClient
    from cactus.util.default_root import DEFAULT_ROOT_PATH
    from cactus.util.ints import uint16
    from cactus.util.config import load_config as load_fork_config
elif importlib.util.find_spec("hddcoin"):
    from hddcoin.rpc.full_node_rpc_client import FullNodeRpcClient
    from hddcoin.rpc.farmer_rpc_client import FarmerRpcClient
    from hddcoin.util.default_root import DEFAULT_ROOT_PATH
    from hddcoin.util.ints import uint16
    from hddcoin.util.config import load_config as load_fork_config

else:
    raise Exception("RPC modules found on pythonpath!")

from api import app
from api import utils

# Unused as I am getting signage points from debug.log as this API returns no dates
async def get_signage_points(blockchain):
    config = load_fork_config(DEFAULT_ROOT_PATH, 'config.yaml')
    farmer_rpc_port = config["farmer"]["rpc_port"]
    farmer = await FarmerRpcClient.create(
        'localhost', uint16(farmer_rpc_port), DEFAULT_ROOT_PATH, config
    )
    points = await farmer.get_signage_points()
    farmer.close()
    await farmer.await_closed()
    config = load_fork_config(DEFAULT_ROOT_PATH, 'config.yaml')
    full_node_rpc_port = config["full_node"]["rpc_port"]
    fullnode = await FullNodeRpcClient.create(
        'localhost', uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
    )
    for point in points:
        sp = point['signage_point']
        signage_point = await fullnode.get_recent_signage_point_or_eos(
            sp_hash=sp['challenge_chain_sp'],
            challenge_hash=sp['challenge_hash'])
        app.logger.info(signage_point)
    fullnode.close()
    await fullnode.await_closed()
    return points

# Used on Pools page to display each pool's state
async def get_pool_state(blockchain):
    pools = []
    try:
        config = load_fork_config(DEFAULT_ROOT_PATH, 'config.yaml')
        farmer_rpc_port = config["farmer"]["rpc_port"]
        farmer = await FarmerRpcClient.create(
            'localhost', uint16(farmer_rpc_port), DEFAULT_ROOT_PATH, config
        )
        result = await farmer.get_pool_state()
        farmer.close()
        await farmer.await_closed()
        if 'pool_state' in result:
            for pool in result["pool_state"]:
                pools.append(pool)
    except Exception as ex:
        app.logger.info("Error getting {0} blockchain pool states: {1}".format(blockchain, str(ex)))
    return pools

# Used to load plot type (solo or portable) via RPC
def get_all_plots():
    plots_via_rpc = asyncio.run(load_all_plots())
    return plots_via_rpc

async def load_all_plots():
    all_plots = []
    try:
        config = load_fork_config(DEFAULT_ROOT_PATH, 'config.yaml')
        farmer_rpc_port = config["farmer"]["rpc_port"]
        farmer = await FarmerRpcClient.create(
            'localhost', uint16(farmer_rpc_port), DEFAULT_ROOT_PATH, config
        )
        result = await farmer.get_harvesters()
        farmer.close()
        await farmer.await_closed()
        for harvester in result["harvesters"]:
            # app.logger.info(harvester.keys()) Returns: ['connection', 'failed_to_open_filenames', 'no_key_filenames', 'plots']
            # app.logger.info(harvester['connection']) Returns: {'host': '192.168.1.100', 'node_id': '602eb9...90378', 'port': 62599}
            host = harvester["connection"]["host"]
            plots = harvester["plots"]
            for plot in plots:
                all_plots.append({
                    "hostname": host,
                    "type": "solo" if (plot["pool_contract_puzzle_hash"] is None) else "portable",
                    "plot_id": plot['plot_id'],
                    "file_size": plot['file_size'], # bytes
                    "filename": plot['filename'], # full path and name
                    "plot_public_key": plot['plot_public_key'],
                    "pool_contract_puzzle_hash": plot['pool_contract_puzzle_hash'],
                    "pool_public_key": plot['pool_public_key'],
                })
    except Exception as ex:
        app.logger.info("Error getting plots via RPC: {0}".format(str(ex)))
    return all_plots

def get_chives_plots():
    plots_via_rpc = asyncio.run(load_chives_plots())
    return plots_via_rpc

async def load_chives_plots():
    host = utils.get_hostname()
    all_plots = []
    try:
        config = load_fork_config(DEFAULT_ROOT_PATH, 'config.yaml')
        harvester_rpc_port = config["harvester"]["rpc_port"]
        harvester = await HarvesterRpcClient.create(
            'localhost', uint16(harvester_rpc_port), DEFAULT_ROOT_PATH, config
        )
        result = await harvester.get_plots()
        harvester.close()
        await harvester.await_closed()
        for plot in result['plots']:
            all_plots.append({
                "hostname": host,
                "type": "solo" if (plot["pool_contract_puzzle_hash"] is None) else "portable",
                "plot_id": plot['plot-seed'], # chives uses plot-seed instead
                "file_size": plot['file_size'], # bytes
                "filename": plot['filename'], # full path and name
                "plot_public_key": plot['plot_public_key'],
                "pool_contract_puzzle_hash": plot['pool_contract_puzzle_hash'],
                "pool_public_key": plot['pool_public_key'],
            })
    except Exception as ex:
        app.logger.info("Error getting plots via RPC: {0}".format(str(ex)))
    return all_plots
