# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
from sys import exit
from typing import Optional

from wusa.new import new


def _as_absolute_Path(path: str):
    return Path(path).absolute()


def subcommand_new(parser: ArgumentParser):
    """Attaches all required arguments to new subcommand"""
    new_subcommand = parser.add_parser("new")
    new_subcommand.add_argument(
        "repo",
        help="URL of the repo for the runner.",
    )
    new_subcommand.add_argument(
        "token",
        help="Token of the GitHub action runner.",
    )
    new_subcommand.add_argument(
        "--dir",
        metavar="<working_dir>",
        help="Working directory of the runner.",
        default=".",
        type=_as_absolute_Path,
    )
    new_subcommand.add_argument(
        "--labels",
        metavar="label",
        help="Labels for GitHub action runner.",
        default="",
        type=str,
        nargs="*",
    )
    # adds default function to be called
    new_subcommand.set_defaults(func=new)


def main(prog_name: Optional[str] = None):
    """Main CLI program"""
    parser = ArgumentParser(
        prog=prog_name,
        description="CLI for managing docker-based GitHub action Runner.",
    )
    subparsers = parser.add_subparsers()

    # subcommands
    subcommand_new(subparsers)

    # parsing and calling subcommands
    args = parser.parse_args()
    if not vars(args):
        # if nothing provided -> print help
        parser.print_help()
        exit(0)
    else:
        # parse commands
        args.func(args)
