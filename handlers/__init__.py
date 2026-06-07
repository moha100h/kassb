from aiogram import Router
from .cmd import router as cmd_r
from .search import router as search_r

router = Router()
router.include_router(cmd_r)
router.include_router(search_r)
