import pytest
from poster_generator.loaders import YamlLoader


@pytest.fixture
def loader():
    return YamlLoader()


@pytest.fixture
def basic_yaml_data():
    return {
        "schema": "1.0",
        "settings": {"width": 400, "height": 300, "background_color": "#000"},
        "anchors": {"center": {"x": 200, "y": 150}},
        "layers": {
            "background": {
                "opacity": 1.0,
                "elements": {
                    "bg": {
                        "type": "image",
                        "position": [0, 0],
                        "values": {"path": "test.jpg"},
                        "operations": {},
                    }
                },
            }
        },
    }


def test_deserialize_settings(loader, basic_yaml_data):
    out = loader.deserialize(basic_yaml_data, variables={})
    settings = out["settings"]

    assert settings["width"] == 400
    assert settings["height"] == 300
    assert settings["background"] == "#000"


def test_variable_substitution(loader):
    data = {
        "schema": "1.0",
        "settings": {
            "width": "--${w}--",
            "height": "--${h}--",
            "background_color": "#fff",
        },
    }

    out = loader.deserialize(data, variables={"w": 999, "h": 777})
    assert out["settings"]["width"] == 999
    assert out["settings"]["height"] == 777


def test_missing_variable_raises(loader):
    data = {"schema": "1.0", "settings": {"width": "--${missing}--"}}

    with pytest.raises(ValueError):
        loader.deserialize(data, variables={})


def test_relative_position_anchor(loader):
    data = {
        "schema": "1.0",
        "anchors": {"center": {"x": 100, "y": 100}},
        "layers": {
            "main": {
                "elements": {
                    "title": {
                        "type": "text",
                        "rel_position": {
                            "source": "anchor",
                            "id": "center",
                            "offset": {"x": 10, "y": -5},
                        },
                        "values": {},
                        "operations": {},
                    }
                }
            }
        },
    }

    out = loader.deserialize(data, variables={})
    elem = out["layers"]["main"]["elements"]["title"]
    assert elem["position"] == (110, 95)


def test_relative_position_element(loader):
    data = {
        "schema": "1.0",
        "layers": {
            "main": {
                "elements": {
                    "first": {
                        "type": "text",
                        "position": [50, 50],
                        "values": {},
                        "operations": {},
                    },
                    "second": {
                        "type": "text",
                        "rel_position": {
                            "source": "element",
                            "id": "first",
                            "offset": {"x": 20, "y": 5},
                        },
                        "values": {},
                        "operations": {},
                    },
                }
            }
        },
    }

    out = loader.deserialize(data, variables={})
    elem = out["layers"]["main"]["elements"]["second"]
    assert elem["position"] == (70, 55)


def test_bad_schema(loader):
    data = {"schema": "2.0"}

    with pytest.raises(ValueError):
        loader.deserialize(data, variables={})
