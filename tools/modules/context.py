# ------------------------------------------------------------------------
# Copyright 2021 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

""" Context """


# Global modules

import sys
import types
import yaml


# Local modules

from modules.config   import Config
from modules.creds    import Creds
from modules.fail     import fail
from modules.logger   import setupLogging
from modules.nestedns import nestedNsToObj


# Functions

def _printHeader(msg):
    sep = '-' * len(msg)
    print(f'# {sep}\n# {msg}\n# {sep}\n')


def getContext(args, withCreds=True, withConfig=True):
    """ Get context """

    setupLogging(args)

    ctx = types.SimpleNamespace()

    ctx.ar = args
    ctx.cr = None
    ctx.cf = None

    if withCreds:
        ctx.creds = Creds(ctx)
        ctx.cr = ctx.creds.get()
        if withConfig:
            ctx.config = Config(ctx)
            ctx.cf = ctx.config.getFull()
    elif withConfig:
        fail("Can't get configuration without credentials")

    if args.dump_context:
        _printHeader('COMMAND LINE ARGUMENTS')
        print(yaml.dump({'ar': nestedNsToObj(ctx.ar)}))
        _printHeader('CREDENTIALS')
        print(yaml.dump({'cr': nestedNsToObj(ctx.cr)}))
        _printHeader('CONFIGURATION')
        print(yaml.dump({'cf': nestedNsToObj(ctx.cf)}))
        sys.exit(0)

    return ctx
