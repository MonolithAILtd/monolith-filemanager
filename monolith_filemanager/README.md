# General File Manager
This document covers the general file management module. 

## Structure
The following structure defines the module:

```
├── __init__.py
├── adapters
│   ├── __init__.py
│   ├── base.py
│   ├── local_file_processes.py
│   └── s3_processes.py
├── errors.py
├── file
│   ├── __init__.py
│   ├── base.py
│   ├── errors.py
│   ├── pandas_file.py
│   └── pickle_file.py
├── path.py
├── s3storage
│   ├── README.md
│   ├── __init__.py
│   ├── bucket_manager.py
│   ├── errors.py
│   └── file_manager.py
└── singleton.py
```
The main file manager interface can be found in the ```__init__``` file at
the root of this module. Because this module is big and the chances of more
file and storage types being added is high, it has it's own internal modules:

- **file**: This is where the local file interactions are defined 
- **s3storage**: This is where the s3 storage interactions are defined

The ```FilePath``` object is stored in the ```path.py``` file in the root.
Some of the objects require a singleton design pattern and this is defined 
in the ```singleton.py``` file at the root. Please use this as a metaclass
to ensure your object behaves like a singleton.

## Use
There are a couple of interfaces in this module:

### Main Interface
Because there are different protocols the interface is managed by selecting the right adapter. This is 
done by importing the factory that will select the right adapter based on the file path characteristics.
To use it do the following:

```python
from monolith_filemanager import file_manager_factory

file = file_manager_factory(file_path="some/file.path.txt")

file_data = file.read_file()

file.write_file(data=file_data)
``` 
### Custom Reading
Some files require custom reading where the file is parsed line by line rather than converted entirely to another format. 
To do this we can pass the function we need into the general file manager. 
This avoids handling file paths and caching outside of the general file manager.

```python
def example_read_function(filepath)
    file = open(filepath, 'rb')
    ... read the file ... 
    return data

from monolith_filemanager import file_manager_factory

file = file_manager_factory(file_path="some/file.path.txt")

file_data = file.custom_read_file(example_read_function)
```

### List Directory
If a file path refers to a directory, you can use `ls` to get all the direct subdirectories and files in that directory.
A tuple of two lists are returned - the list of subdirectories, followed by the list of files.

```python
from monolith_filemanager import file_manager_factory

folder = file_manager_factory(file_path="some/folder")

dirs, files = folder.ls()
```

### File Path
The ```FilePath``` is not designed to be used as an interface but it's such a useful object it makes sense
to sometimes import it for other uses. It's imported in the ```__init__.py``` file for the ```FileManager```
object so it can be directly imported. The ```FilePath``` object has the ability to see if the root exists 
and if the file exists. To use it do the following:

```python
from monolith_filemanager import FilePath

path = FilePath("this/is/a/path.txt")
```
To get documentation on the individual properties and functions simply call the help function:

```python
from monolith_filemanager import FilePath

help(FilePath)
```

## To do 
pickle files need to be configured.  