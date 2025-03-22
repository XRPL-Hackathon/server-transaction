import os
from dotenv import load_dotenv
import xrpl

load_dotenv()

XRPL_RPC_URL = os.getenv("XRPL_RPC_URL")

client = xrpl.clients.JsonRpcClient(XRPL_RPC_URL)