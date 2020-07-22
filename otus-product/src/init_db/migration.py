import os
import argparse
from alembic.config import Config
from alembic import command
import inspect


def alembic_set_stamp_head(config_migration_path):
    # set the paths values
    this_file_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    alembic_directory = os.path.join(this_file_directory, 'alembic')
    ini_path = config_migration_path
    
    # create Alembic config and feed it with paths
    config = Config(ini_path)
    config.set_main_option('script_location', alembic_directory)
    config.cmd_opts = argparse.Namespace()  # arguments stub
    config.attributes['configure_logger'] = False

    # prepare and run the command
    revision = 'head'

    # upgrade command
    command.upgrade(config, revision)
