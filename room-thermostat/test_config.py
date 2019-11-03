from config import Config

def test_mqtt():
    config = Config('./test_config.yaml')

    assert config.mqtt['host'] == 'mqtt.foobar.com'
    assert config.mqtt['port'] == 12345
    assert config.mqtt['prefix'] == 'topic_prefix'
    assert config.mqtt['client_id'] == 'mqtt_client_id'

def test_rooms():
    config = Config('./test_config.yaml')

    assert len(config.rooms) == 2

    first_room = config.rooms[0]
    assert first_room['name'] == 'first room with long name'
    assert first_room['name_snakecase'] == 'first_room_with_long_name'
    assert first_room['measurement_topic'] == 'some_sensor/xyz01'
    assert first_room['control_topic'] == 'some_controller/abc01'
    assert len(first_room['temperatures']) == 3
    assert first_room['temperatures']['home'] == 21
    assert first_room['temperatures']['away'] == 15
    assert first_room['temperatures']['sleep'] == 18

    second_room = config.rooms[1]
    assert second_room['name'] == 'second_room'
    assert second_room['name_snakecase'] == 'second_room'
    assert second_room['measurement_topic'] == 'some_sensor/xyz02'
    assert second_room['control_topic'] == 'some_controller/abc02'
    assert len(second_room['temperatures']) == 3
    assert second_room['temperatures']['home'] == 21
    assert second_room['temperatures']['away'] == 21
    assert second_room['temperatures']['sleep'] == 21

def test_root_params():
    config = Config('./test_config.yaml')

    assert config.interval == 10
