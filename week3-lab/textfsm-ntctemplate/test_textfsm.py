import pytest
from textfsm import generate_descriptions

def test_r1_descriptions():
    parsed_data = [
        {"neighbor_name": "R2.itkmitl.lab", "local_interface": "Gig 0/2", "neighbor_interface": "0/1"},
        {"neighbor_name": "S0.itkmitl.lab", "local_interface": "Gig 0/0", "neighbor_interface": "0/1"},
    ]
    result = generate_descriptions("R1", parsed_data)
    assert result["GigabitEthernet0/2"] == "Connect to GigabitEthernet0/1 of R2.itkmitl.lab"
    assert result["GigabitEthernet0/0"] == "Connect to GigabitEthernet0/1 of S0.itkmitl.lab"
    assert result["GigabitEthernet0/1"] == "Connect to PC"

def test_r2_descriptions():
    parsed_data = [
        {"neighbor_name": "R1.itkmitl.lab", "local_interface": "Gig 0/1", "neighbor_interface": "0/2"},
        {"neighbor_name": "S1.itkmitl.lab", "local_interface": "Gig 0/2", "neighbor_interface": "0/1"},
    ]
    result = generate_descriptions("R2", parsed_data)
    assert result["GigabitEthernet0/1"] == "Connect to GigabitEthernet0/2 of R1.itkmitl.lab"
    assert result["GigabitEthernet0/2"] == "Connect to GigabitEthernet0/1 of S1.itkmitl.lab"
    assert result["GigabitEthernet0/3"] == "Connect to WAN"

def test_s1_descriptions():
    parsed_data = [
        {"neighbor_name": "R2.itkmitl.lab", "local_interface": "Gig 0/1", "neighbor_interface": "0/2"},
    ]
    result = generate_descriptions("S1", parsed_data)
    assert result["GigabitEthernet0/1"] == "Connect to GigabitEthernet0/2 of R2.itkmitl.lab"
    assert result["GigabitEthernet1/1"] == "Connect to PC"
