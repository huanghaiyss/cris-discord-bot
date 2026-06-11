import pytest
from core.database import Database
from services.leveling_service import LevelingService, level_for_xp, xp_for_level
@pytest.mark.asyncio
async def test_level_formula():
    assert xp_for_level(2)==400
    assert level_for_xp(0)==0
    assert level_for_xp(100)==1
    assert level_for_xp(399)==1
    assert level_for_xp(400)==2
@pytest.mark.asyncio
async def test_add_xp(tmp_path):
    db=Database(tmp_path/'bot.db'); await db.open(); await db.apply_migrations(); svc=LevelingService(db)
    r=await svc.add_xp(1,2,150,cooldown=False)
    assert r.level==1 and r.leveled_up
    row=await svc.rank(1,2)
    assert row['xp']==150
    await db.close()
