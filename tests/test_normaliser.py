from pipeline.normaliser import normalise_to_utc


def test_valid_timestamp():
    ts = "2024-04-23 13:10:55"
    result = normalise_to_utc(ts)
    assert result.startswith("2024-04-23T13:10:55")


def test_invalid_timestamp():
    ts = "not-a-time"
    result = normalise_to_utc(ts)
    assert result is None
