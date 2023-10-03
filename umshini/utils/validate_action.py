import string

from colorama import Fore

MAX_CHARS = 4000


def validate_action(action):
    if type(action) == str:
        response = "".join(filter(lambda x: x in string.printable, action))
        if response != action:
            print(
                Fore.YELLOW
                + "Response contained invalid characters, and has been reformatted."
            )
            response = "".join(char for char in action if char in set(string.printable))

        # making sure it is within the max characters limit
        # or do some naive truncation if not
        if len(response) > MAX_CHARS:
            print(
                Fore.YELLOW
                + f"Response was too long! ({len(response)}) Your action was truncated to fit within the character limit ({MAX_CHARS})."
            )
            response = response[:MAX_CHARS]
        return response
    else:
        return action
