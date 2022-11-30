# leveldiagram

This module creates energy level diagrams common to atomic physics as matplotlib graphics.
The level structure is defined using networkx graphs.

## Quick Usage

Put stuff here with an example plot output.

## Installation

Presently, installation must be done manually using a copy of the repository.

### Pure pip installation

To install in an editable way (which allows edits of the source code), run:
```shell
pip install -e .
```
from within the top level `leveldiagram` directory (i.e. where the `setup.cfg` file resides).
This command will use pip to install all necessary dependencies.

To install normally, run:
```shell
pip install .
```
from the same directory.

### conda installation

Think about making a conda channel.

### Confirm installation

Proper installation can be confirmed by executing the following commands in a python terminal.


### Updating an existing installation

Upgrading an existing installation is simple.
Simply run the pip installation commands described above with the update flag.
```shell
pip install -U .
```
This command will also install any new dependencies that are required.

If using an editable install, simply replacing the files in the same directory is sufficient.
Though it is recommended to also run the appropriate pip update command as well.
```shell
pip install -U -e .
```

### Dependencies

Requires `matplotlib`, `networkx`, etc

## Documentation

Documentation is available somewhere.

### Examples

Example jupyter notebooks that demonstrate leveldiagrams can be found in the `examples` subdirectory.
Printouts of these notebooks are available in the docs as well.