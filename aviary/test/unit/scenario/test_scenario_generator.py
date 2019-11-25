
import pytest

import os
import json
import time
from datetime import datetime

import aviary.scenario.scenario_generator as sg


@pytest.fixture(params=['i_element', 'x_element'])
def target_sector(request):
    """Test fixture: used to test scenario generation for each sector fixture in params"""
    return request.getfixturevalue(request.param)


@pytest.fixture(params=['poisson_scenario'])
def target_scenario(request):
    """Test fixture: used to test scenario generation for each scenario fixture in params"""
    return request.getfixturevalue(request.param)


def test_generate_scenario(target_sector, target_scenario):
    seed = 83
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)

    assert sg.START_TIME_KEY in scenario.keys()
    assert sg.AIRCRAFT_KEY in scenario.keys()
    assert isinstance(scenario[sg.START_TIME_KEY], str)
    assert isinstance(scenario[sg.AIRCRAFT_KEY], list)
    assert len(scenario[sg.AIRCRAFT_KEY]) > 0

    total_time = 0
    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sg.START_TIME_KEY in aircraft.keys()
        total_time += aircraft[sg.AIRCRAFT_TIMEDELTA_KEY]
    assert total_time <= duration

    for i in range(10):
        scenario2 = scen_gen.generate_scenario(duration=duration, seed=seed)
        assert scenario == scenario2


def test_generate_scenario_with_start_time(target_sector, target_scenario):
    seed = 83
    duration = 1000
    scenario_start_time = datetime.strptime("12:05:42", "%H:%M:%S")

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario, scenario_start_time)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)

    total_time = 0
    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sg.AIRCRAFT_TIMEDELTA_KEY in aircraft.keys()
        assert datetime.strptime(aircraft[sg.START_TIME_KEY], "%H:%M:%S") > scenario_start_time
        inferred_aircraft_timedelta = (datetime.strptime(aircraft[sg.START_TIME_KEY], "%H:%M:%S") - scenario_start_time).total_seconds()
        assert inferred_aircraft_timedelta == int(aircraft[sg.AIRCRAFT_TIMEDELTA_KEY])
        total_time += aircraft[sg.AIRCRAFT_TIMEDELTA_KEY]

    assert total_time <= duration


def test_serialisation(target_sector, target_scenario):
    seed = 62
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)
    scenario = scen_gen.serialize_route(scenario)

    serialised = json.dumps(scenario, sort_keys=True)

    deserialised = json.loads(serialised)

    assert isinstance(deserialised, dict)
    assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])


def test_write_json_scenario(target_sector, target_scenario):
    seed = 76
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)

    filename = "test_scenario"
    here = os.path.abspath(os.path.dirname(__file__))
    file = scen_gen.write_json_scenario(
        scenario = scenario,
        filename = filename,
        path = here
        )

    assert os.path.exists(file)

    # Clean up.
    os.remove(file)