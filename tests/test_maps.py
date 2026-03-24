import pytest
import json
from pathlib import Path

from app.repositories.map_storage import MapStorage

@pytest.fixture
def example_address1():
    return "1137 Alumni Ave, Kelowna, BC"

def example_address2():
    return "2271 Harvey Ave, Kelowna, BC"

def test_delivery_time_mins() -> int: 
    address1 = "1137 Alumni Ave, Kelowna, BC"
    address2 = "2271 Harvey Ave, Kelowna, BC"
    # the drive is ~10 minutes outside of rush hour. 30 mins used in case of unprecidented route at the time of testing (i.e. hwy97 is closed, take glenmore), etc.
    # returns -1 in case of error
    assert ((MapStorage().calculateDeliveryTimeMins(address1, address2)) < 30) and ((MapStorage().calculateDeliveryTimeMins(address1, address2)) > 0)

def test_distance_kms() -> float:
    address1 = "1137 Alumni Ave, Kelowna, BC"
    address2 = "2271 Harvey Ave, Kelowna, BC"
    # the drive is slightly over 8km, when taking the 97. 20km used in case of unprecidented route at the time of testing.
    # returns -1 in case of error
    assert (MapStorage().calculateDeliveryDistanceKM(address1, address2) < 20.00) and ((MapStorage().calculateDeliveryTimeMins(address1, address2)) > 0)