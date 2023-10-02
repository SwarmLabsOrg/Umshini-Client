from umshini.utils.validate_action import validate_action


def long_response_policy(obs, rew, term, trunc, info):
    """Return a response of all the digits 1 through 4000 concatenated together (14k characters total)."""
    response = "".join(map(str, range(1, 4000)))
    return (response, 0)


def test_input_validation_length():
    response = "".join(map(str, range(1, 10000)))
    validated_action = validate_action(response)
    assert len(validated_action) <= 4000


def test_input_validation_illegal_characters():
    original_string = "Hello!"
    non_printable_chars = (
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0E\x0F"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F"
    )
    response = original_string + non_printable_chars
    validated_action = validate_action(response)
    assert validated_action == original_string
