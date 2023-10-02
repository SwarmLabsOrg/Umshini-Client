import string

from colorama import Fore, Style


def validate_action(action):
    print("VALIDATING ACTION")
    if type(action) == str:
        response = "".join(filter(lambda x: x in string.printable, action))
        if response != action:
            print(Fore.YELLOW + f"Response contained invalid characters, and has been reformatted.")
        # making sure it is within the max characters limit
        # or do some naive truncation if not
        if len(response) > 4000:
            print(Fore.YELLOW + f"Response was too long! Your action was truncated to fit within the character limit.")
            res = response.split(".")
            response = ""
            while len(res) > 0 and len(response) + len(res[0]) + 1 < 4000:
                res += res.pop(0) + "."
        return response
    else:
        return action
