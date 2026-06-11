import pytest
from core.config import Config, ConfigError

def test_config_from_mapping_parses_ids():
    c=Config.from_mapping({'DISCORD_TOKEN':'x','OWNER_IDS':'1, 2','DEV_GUILD_ID':'3','LOG_LEVEL':'debug'})
    assert c.owner_ids=={1,2}
    assert c.dev_guild_id==3
    assert c.log_level=='DEBUG'

def test_config_requires_token():
    with pytest.raises(ConfigError): Config.from_mapping({})
