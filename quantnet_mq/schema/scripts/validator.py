#!/usr/bin/env python

"""
Usage:
  validator [options] <schema> <instance> <object>

Options:
  -s schema directory
  -h --help
"""

import os
from docopt import docopt
import json
import jsonschema
from jsonschema import validate


def get_file_json(f):
    with open(f, "r") as file:
        data = json.load(file)
    return data


def validate_json(schema, instance, sdir):
    try:
        resolver = jsonschema.validators.RefResolver(
            base_uri=f"file://{sdir}/",
            referrer=True,
        )
        validate(instance=instance, schema=schema, resolver=resolver)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "Given JSON data is InValid"
        return False, err

    message = "Given JSON data is Valid"
    return True, message


def main():
    args = docopt(__doc__, version="0.1")
    sname = args.get("<schema>")
    iname = args.get("<instance>")
    sdir = args.get("-s")
    if not sdir:
        sdir = os.path.dirname(os.path.abspath(sname))
    obj = args.get("<object>")
    print(f"Validating {iname} against {sname}...")
    try:
        schema = get_file_json(sname)
        schema = schema["components"]["schemas"][obj]
    except Exception as e:
        print(f"Error: Could not find requested schema: {e}")
        return
    (status, msg) = validate_json(schema, get_file_json(iname), sdir)
    print(msg)


if __name__ == "__main__":
    main()
