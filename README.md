# General File Manager
This module enables the users to read and write files from local or s3 with just a few 
lines of code. This file manager works out the type of file that is to be loaded by the 
extension and where the file is located by the prefix.


### Main Interface
Because there are different protocols the interface is managed by selecting the right adapter. This is 
done by importing the factory that will select the right adapter based on the file path characteristics.
To use it do the following:

```python
from general_filemanager import file_manager_factory

file = file_manager_factory(file_path="some/file.path.txt")

file_data = file.read_file()

file.write_file(data=file_data)
``` 

### s3 interface
The interface is exactly the same, however, there is sometimes the need for caching when reading and writing to 
s3 buckets. This can we handled with the ```monolith-caching``` module which can be installed
by ```pip install monolithcaching```. 

```python
from general_filemanager import file_manager_factory
from monolithcaching import CacheManager

manager = CacheManager(local_cache_path="/path/to/local/directory/for/all/caches")
file = file_manager_factory(file_path="s3://some/file.path.txt", caching=manager)

file_data = file.read_file()

file.write_file(data=file_data)
``` 

### Custom Reading
Some files require custom reading where the file is parsed line by line rather than converted entirely to another format. 
To do this we can pass the function we need into the general file manager. 
This avoids handling file paths and caching outside of the general file manager. 

```python
def example_read_function(filepath):
    file = open(filepath, 'rb')
    ... read the file ... 
    return data

from general_filemanager import file_manager_factory

file = file_manager_factory(file_path="some/file.path.txt")

file_data = file.custom_read_file(example_read_function)
```

### List Directory
If a file path refers to a directory, you can use `ls` to get all the direct subdirectories and files in that directory.
A tuple of two lists are returned - the list of subdirectories, followed by the list of files.

```python
from general_filemanager import file_manager_factory

folder = file_manager_factory(file_path="some/folder")

dirs, files = folder.ls()
```

### File Path
The ```FilePath``` is not designed to be used as an interface but it's such a useful object it makes sense
to sometimes import it for other uses. It's imported in the ```__init__.py``` file for the ```FileManager```
object so it can be directly imported. The ```FilePath``` object has the ability to see if the root exists 
and if the file exists. To use it do the following:

```python
from general_filemanager import FilePath

path = FilePath("this/is/a/path.txt")
```
To get documentation on the individual properties and functions simply call the help function:

```python
from general_filemanager import FilePath

help(FilePath)
```
 
# Supported Formats/Extensions
The module supports the following extensions:

- csv
- dat
- data
- hdf5
- h5
- hdf5
- hdf
- json
- joblib
- mat
- npy
- pickle
- parquet
- vtk
- yml

# Contributing 
This repo is still fairly new so contributing will require some communication. 
You can contact with ideas and outline for a feature at ```maxwell@monolithai.com```.

Writing code is not the only way you can contribute. Merely using the module is a help, if you come across any issues 
feel free to raise them in the issues section of the Github page as this enables us to make the module more stable.
If there are any issues that you want to solve, your pull request has to have documentation, 100% unit test coverage 
and functional testing. 