#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import uvicorn

from fastapi import FastAPI

from src.api import listening_address
from src.api.routers import config_router, general_infos_router, interface_router, misc_router, vlan_router, \
    trunk_router, auth_router

api = FastAPI()

api.include_router(general_infos_router.router)
api.include_router(interface_router.router)
api.include_router(vlan_router.router)
api.include_router(trunk_router.router)
api.include_router(config_router.router)
# api.include_router(auth_router.router)
api.include_router(misc_router.router)

if __name__ == "__main__":
    uvicorn.run(api, host=listening_address, debug=True)

