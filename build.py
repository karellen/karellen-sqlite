#
#  -*- coding: utf-8 -*-
#
# (C) Copyright 2016 Karellen, Inc. (http://karellen.co/)
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
#

from pybuilder.core import use_plugin, init, before, Project, Author, Logger
from pybuilder.errors import BuildFailedException
from pybuilder.pip_utils import pip_install

use_plugin("pypi:karellen_pyb_plugin", ">=0.0.1.dev")

name = "karellen-sqlite"
version = "0.0.4.dev"

url = "https://github.com/karellen/karellen-sqlite"
description = "Please visit %s for more information!" % url
summary = "Karellen Core"

author = Author("Karellen, Inc", "supervisor@karellen.co")
authors = [author]
license = "Apache License, Version 2.0"

default_task = ["install_dependencies", "analyze", "sphinx_generate_documentation", "publish"]

obsoletes = "pysqlite"


@init
def set_properties(project: Project):
    project.set_property("verbose", True)

    # Dependencies
    project.build_depends_on("karellen-testing", ">=0.0.1dev")

    # Cram Configuration
    project.set_property("cram_fail_if_no_tests", False)

    # Integration Tests Coverage is disabled since there are no integration tests
    project.set_property("integrationtest_coverage_threshold_warn", 0)
    project.set_property("integrationtest_coverage_branch_threshold_warn", 0)
    project.set_property("integrationtest_coverage_branch_partial_threshold_warn", 0)

    project.set_property("distutils_classifiers", project.get_property("distutils_classifiers") + [
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules"])


@before("run_integration_tests")
def install_self(project: Project, logger: Logger):
    logger.info("Installing %s..." % name)
    if pip_install(project.expand_path("$dir_dist"), force_reinstall=True):
        raise BuildFailedException("Unable to install %s" % name)
