import pytest

from scripts.script_definitions import *


@pytest.fixture
def no_auction():
    set_base_uri("https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/")
    end_auction()
