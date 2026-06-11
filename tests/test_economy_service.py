import pytest
from core.database import Database
from services.economy_service import EconomyService, BalanceChange, EconomyError
@pytest.mark.asyncio
async def test_balance_changes_and_negative_prevention(tmp_path):
    db=Database(tmp_path/'bot.db'); await db.open(); await db.apply_migrations(); svc=EconomyService(db)
    assert await svc.balance(1,10)==0
    assert await svc.change_balance(BalanceChange(1,10,100,'test'))==100
    with pytest.raises(EconomyError): await svc.change_balance(BalanceChange(1,10,-101,'too_much'))
    assert await svc.balance(1,10)==100
    await db.close()
@pytest.mark.asyncio
async def test_transfer(tmp_path):
    db=Database(tmp_path/'bot.db'); await db.open(); await db.apply_migrations(); svc=EconomyService(db)
    await svc.change_balance(BalanceChange(1,1,200,'seed'))
    a,b=await svc.transfer(1,1,2,75)
    assert (a,b)==(125,75)
    rows=await db.fetchall('SELECT * FROM economy_transactions WHERE guild_id=1')
    assert len(rows)==3
    await db.close()
