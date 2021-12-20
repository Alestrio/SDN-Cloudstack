#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, HTTPException, Depends

from src.api.auth_utils import get_current_admin_user
from src.api.routers import ROUTE_PREFIX, operations

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Miscellaneous"],
                   dependencies=[Depends(get_current_admin_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get("/rebuild")
def rebuild_cache():
    # Rebuild the cache from the switch
    try:
        operations.rebuild_cache()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while rebuilding cache \n'
                                                    'Either the switch is offline/unreachable or the credentials'
                                                    ' are wrong')
    return {'message': 'Cache rebuilt'}


