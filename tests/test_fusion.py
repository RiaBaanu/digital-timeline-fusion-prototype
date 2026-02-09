from parsers.iot_parser import IoTCSVParser

def test_iot_parser():
    parser = IoTCSVParser("data/raw/iot_logs.csv")
    events = parser.parse()

    assert len(events) > 0
    assert events[0].device_id == "Camera01"
