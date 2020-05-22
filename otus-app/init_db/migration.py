import os
import argparse
from alembic.config import Config
from alembic import command
import inspect


def alembic_set_stamp_head():
    # set the paths values
    this_file_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    root_directory = os.path.join(this_file_directory, '../config')
    alembic_directory = os.path.join(this_file_directory, 'alembic')
    ini_path = os.path.join(root_directory, 'alembic.ini')

    # create Alembic config and feed it with paths
    config = Config(ini_path)
    config.set_main_option('script_location', alembic_directory)
    config.cmd_opts = argparse.Namespace()  # arguments stub
    config.attributes['configure_logger'] = False

    # prepare and run the command
    revision = 'head'

    # upgrade command
    command.upgrade(config, revision)
