#!/usr/bin/env python

"""Removes SavedVariables files for unused addons."""

import sys
import os
import re

if os.name == "posix":
    WOW_PATH = "/run/media/soulsbane/Games/Games/WoW/World of Warcraft/_retail_"
elif (os.name == "win") or (os.name == "nt"):
    WOW_PATH = r"E:\World of Warcraft\\"

WOW_PATH = './'

def listfiles(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def listdirs(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]


def get_addon_list(wow_path):
    return listdirs(os.path.join(wow_path, "Interface", "AddOns"))


def remove_unused_files(path, addons, extension):
    re_sv_filename = re.compile(r"^(.*)\." + extension + "$")

    for sv_file in listfiles(path):
        match = re_sv_filename.match(sv_file)

        if match:
            addon_name = match.group(1)

            if addon_name not in addons:
                if os.path.exists(path):
                    print("Removing " + os.path.join(path, sv_file))
                    os.remove(os.path.join(path, sv_file))

def clean_saved_variables(wow_path):
    addons = get_addon_list(wow_path)
    # /_retail_/WTF/Account
    sv_base_path = os.path.join(wow_path, "WTF", "Account")
    for account in listdirs(sv_base_path):
        # /_retail_/WTF/Account/<account name>
        account_path = os.path.join(sv_base_path, account)
        # /_retail_/WTF/Account/<account name>/SavedVariables
        account_sv_path = os.path.join(account_path, "SavedVariables")
        remove_unused_files(account_sv_path, addons, "lua")
        remove_unused_files(account_sv_path, addons, "bak")

        for server in [f for f in listdirs(account_path) if f != "SavedVariables"]:
            server_path = os.path.join(account_path, server)

            for character in listdirs(server_path):
                character_path = os.path.join(server_path, character)
                character_sv_path = os.path.join(character_path, "SavedVariables")

                if os.path.isdir(character_sv_path):
                    remove_unused_files(character_sv_path, addons, "lua")
                    remove_unused_files(character_sv_path, addons, "bak")

def main(argv=None):
    wow_path = WOW_PATH

    if len(argv) == 2:
        wow_path = argv[1]

    if not os.path.isdir(wow_path):
        print("Error: WoW directory not found!")
        return -1

    clean_saved_variables(wow_path)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
