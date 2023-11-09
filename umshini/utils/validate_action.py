import string

from colorama import Fore

MAX_CHARS = 4000


def validate_action(action):
    if isinstance(action, str):
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
            # making sure it is within the max characters limit
            # or do some naive truncation if not
            if len(response) > 4000:
                res = response.split(".")
                response = ""
                while len(res) > 0 and len(response) + len(res[0]) + 1 < 4000:
                    response += res.pop(0) + "."
        return response
    else:
        return action
