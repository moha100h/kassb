from aiogram import Router
from .cmd import router as cmd_r
from .search import router as search_r
from .settings import router as settings_r

router = Router()
router.include_router(settings_r)
router.include_router(cmd_r)
router.include_router(search_r)
