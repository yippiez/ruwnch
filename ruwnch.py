
import sys
import json
import os
import importlib
import hashlib

from datetime import datetime
from enum import Enum
import time
import subprocess
from typing import List, Tuple

# =========================

DEFAULT_CONFIG = {
    "checkPeriod": 5,
    "useColorama": True,
    "enableHashCache": True,
    "enableLastCommandCache": True,
    "quitOnError": False
}

DEFAULT_CACHE = {
    "files": {},
    "last": "",
}

colorama = None

# =========================


def get_config(key: str) -> bool | int | None:
    """Gets the config given a key

    Args:
        key (str): key to look and get for in the config

    Returns:
        bool | int: value of the config
    """

    if not os.path.exists("config.json"):
        fatal("Config missing, this shouldn't be.")

    with open("config.json", "r") as f:
        config = json.loads(f.read())

        try:
            return config[key]
        except KeyError:
            fatal(f"The key {key} does not exist in config.")


def is_colorama_avaible() -> bool:
    """Chekcs if colorama is aviable i.e. allowed by the config.
    If so imports it if not imported and returns true fale otherwise.

    Returns:
        bool: flag to see if colorama is avaible
    """
    global colorama

    if get_config("useColorama"):
        colorama = importlib.import_module('colorama')
        return True
    else:
        return False


# =========================


def get_current_date() -> str:
    """Gets the current date in dd-mm-yyyy format.

    Returns:
        str: current date as string
    """
    return datetime.now().strftime("%d-%m-%Y")


def get_current_time() -> str:
    """Gets the current time in military (24) format.

    Returns:
        str: current time as string
    """
    return datetime.now().strftime("%H:%M")


def print_info(msg: str):
    """Prints out a info formatted message.

    Args:
        msg (str): message to be printed
    """
    header = f"[{get_current_date()} {get_current_time()}] (INFO) "

    if is_colorama_avaible():
        YELLOW = colorama.Fore.YELLOW  # type: ignore
        WHITE = colorama.Fore.WHITE  # type: ignore
        RESET = colorama.Style.RESET_ALL  # type: ignore

        result = f"{YELLOW}{header}{WHITE}{msg}{RESET}"
    else:
        result = f"{header}{msg}"

    print(result)


def print_fatal(msg: str):
    """Prints out a info formatted message.

    Args:
        msg (str): message to be printed
    """
    header = f"[{get_current_date()} {get_current_time()}] (FATAL) "

    if is_colorama_avaible():
        RED = colorama.Fore.RED  # type: ignore
        WHITE = colorama.Fore.WHITE  # type: ignore
        RESET = colorama.Style.RESET_ALL  # type: ignore

        result = f"{RED}{header}{WHITE}{msg}{RESET}"
    else:
        result = f"{header}{msg}"

    print(result)

# =========================


def fatal(msg: str):
    """Prints out a message and then quits.

    Args:
        msg (str): message to be printed
    """
    print_fatal(msg)
    print(
        "Usage ruwnch <filepath: string | List[string]> <shellcommand: string | List[string]>")
    exit()

# =========================


def generate_missing_files():

    if not os.path.exists("config.json"):
        with open("config.json", "w") as f:
            json_string = json.dumps(DEFAULT_CONFIG)
            f.write(json_string)

    if not os.path.exists("ruwnch.cache.json"):
        with open("ruwnch.cache.json", "w") as f:
            json_string = json.dumps(DEFAULT_CACHE)
            f.write(json_string)

# =========================


def save_last_cache(argv: List[str]):
    """Saves the argv to be used later

    Args:
        argv (List[str]): argv to be saved
    """
    cache = None

    # Load
    with open("ruwnch.cache.json", "r") as f:
        content = f.read()
        cache = json.loads(content)

    # Mutate
    cache['last'] = argv

    # Save
    with open("ruwnch.cache.json", "w") as f:
        content = json.dumps(cache)
        f.write(content)


def get_last_cache() -> List[str] | None:
    """Gets the last saved argv if there any if not returns empty list

    Returns:
        List[str]: last saved argv, if it doesn't exist empty list
    """
    with open("ruwnch.cache.json", "r") as f:
        content = f.read()
        cache = json.loads(content)

        try:
            return cache['last']
        except KeyError:
            fatal("For some reason cache doesn't have the field last")


def get_hash_list() -> dict | None:
    """Gets the hashed "hashlist" a dict that matches absolute paths to 
    hashes last calculated.

    Returns:
        dict | None: Cached hashlist if present else None
    """
    with open("ruwnch.cache.json", "r") as f:
        content = f.read()
        cache = json.loads(content)

        try:
            return cache['files']
        except KeyError:
            fatal("For some reason cache doesn't have the field last")


def save_hash_list(hashlist: dict):
    new_cache_hashlist = None

    with open("ruwnch.cache.json", "r") as f:
        content = f.read()
        cache = json.loads(content)

        cache['files'] = hashlist

        new_cache_hashlist = cache

    with open("ruwnch.cache.json", "w") as f:
        new_cache_hashlist_string = json.dumps(new_cache_hashlist)

        f.write(new_cache_hashlist_string)

# =========================


class ExecutionMode(Enum):
    SINGLE_TO_SINGLE = 0
    MULTI_TO_SINGLE = 2
    MULTI_TO_MULTI = 3


def get_execution_mode_from_arguments(filepaths: List[str], commands: List[str]) -> ExecutionMode | None:
    num_files = len(filepaths)
    num_commands = len(commands)

    MODE = None
    if num_files == 1 and num_commands == 1:
        MODE = ExecutionMode.SINGLE_TO_SINGLE
    elif num_files > 1 and num_commands == 1:
        MODE = ExecutionMode.MULTI_TO_SINGLE
    elif num_files == num_commands:
        MODE = ExecutionMode.MULTI_TO_MULTI
    else:
        fatal("Number of arguments incorrect. Check readme for more information.")

    return MODE

# =========================


def parse_argument(argument: str) -> List[str]:
    if '[' == argument[0]:
        argument = argument[1:len(argument)-1]
        splitted = argument.split(',')

        return splitted
    else:
        return [argument]


def parse_argv(argv: List[str]) -> Tuple[List[str], List[str]]:

    if len(argv) == 2 and get_config("enableLastCommandCache"):
        if argv[1] == "last":
            if last := get_last_cache():
                argv = last
            else:
                fatal("No last cache found in ruwnch.cache.json")

    if len(argv) != 3:
        fatal(f"Wrong number of arguments ({len(argv)}) given. {argv}")

    return (parse_argument(argv[1]),  parse_argument(argv[2]))


# =========================


def generate_hash_from_filepath(relative_path: str) -> str:
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()

    with open(relative_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

# =========================


def main():
    # Generate missing conifg and cache files
    generate_missing_files()

    # Get arguments
    parsed_filepaths, parsed_commands = parse_argv(sys.argv)

    if get_config("enableLastCommandCache"):
        save_last_cache(sys.argv)

    # Infer mode from arguments
    MODE = get_execution_mode_from_arguments(parsed_filepaths, parsed_commands)

    # Get current hash list and check period
    hashlist = get_hash_list()
    checkPeriod = get_config("checkPeriod")
    cacheEnabled = get_config("enableHashCache")
    quitOnError = get_config("quitOnError")

    assert isinstance(hashlist, dict)
    assert isinstance(checkPeriod, int)
    assert isinstance(cacheEnabled, bool)
    assert isinstance(quitOnError, bool)

    if not cacheEnabled:
        hashlist = {}

    try:
        while True:
            for relative_path in parsed_filepaths:
                hash = generate_hash_from_filepath(relative_path)
                absolutepath = os.path.abspath(relative_path)

                if hashlist.get(absolutepath, None) != hash:
                    match (MODE):
                        case ExecutionMode.SINGLE_TO_SINGLE:
                            command = parsed_commands[0]
                        case ExecutionMode.MULTI_TO_SINGLE:
                            command = parsed_commands[0]
                        case ExecutionMode.MULTI_TO_MULTI:
                            command = parsed_commands[parsed_filepaths.index(
                                relative_path)]
                        case _:
                            fatal("Unknown execute mode given to execute")

                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )

                    print_info(
                        f"CHANGE Detected running command ({command}) for file ({absolutepath})")

                    if result.stderr:
                        if quitOnError:
                            fatal(
                                f"Error when running command. STDERR -> {result.stderr}")
                        else:
                            print_info(
                                f"Error when running command ({command}) for file ({absolutepath})")

                hashlist[absolutepath] = hash

            if cacheEnabled:
                save_hash_list(hashlist)

            time.sleep(checkPeriod)
    except KeyboardInterrupt:
        print_fatal("Keyboard interrupt detected. Quitting...")


if __name__ == "__main__":
    main()
