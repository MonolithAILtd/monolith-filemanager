# General File Manager
This module enables the users to read and write files from local or s3 with just a few 
lines of code. This file manager works out the type of file that is to be loaded by the 
extension and where the file is located by the prefix.


### Main Interface
Because there are different protocols the interface is managed by selecting the right adapter. This is 
done by importing the factory that will select the right adapter based on the file path characteristics.
To use it do the following:

```python
from monolith_filemanager import file_manager

file = file_manager(file_path="some/file.path.txt")

file_data = file.read_file()

file.write_file(data=file_data)
``` 

### s3 interface
The interface is exactly the same, however, there is sometimes the need for caching when reading and writing to 
s3 buckets. This can we handled with the ```monolith-caching``` module which can be installed
by ```pip install monolithcaching```. The caching module enables the filemanager so store files 
that have just been downloaded from the s3 to read for some formats.

```python
from monolith_filemanager import file_manager
from monolithcaching import CacheManager

manager = CacheManager(local_cache_path="/path/to/local/directory/for/all/caches")
file = file_manager(file_path="s3://some/file.path.txt", caching=manager)

file_data = file.read_file()

file.write_file(data=file_data)
``` 
It has to be noted that the ```s3``` is triggered by having the ```"s3://"``` at the start of the 
file path.

### Custom Reading
Some files require custom reading where the file is parsed line by line rather than converted entirely to another format. 
To do this we can pass the function we need into the general file manager. 
This avoids handling file paths and caching outside of the general file manager. 

```python
def example_read_function(filepath):
    file = open(filepath, 'rb')
    ... read the file ... 
    return data

from monolith_filemanager import file_manager

file = file_manager(file_path="some/file.path.txt")

file_data = file.custom_read_file(example_read_function)
```
### Custom Templates
Custom templates can be built by building our own objects that inherit from our ```File``` object as demonstrated by the 
code below:

```python
from typing import Any, Union

from monolith_filemanager.file.base import File
from monolith_filemanager.path import FilePath

from adapters.file_manager_adapters.errors import PickleFileError


class PickleFile(File):
    """
    This is a class for managing the reading and writing of pickled objects.
    """
    SUPPORTED_FORMATS = ["pickle"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the PickleFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: (Any) Data from the pickle file
        """
        try:
            from pickle_factory import base as pickle_factory
        except ImportError:
            raise PickleFileError(
                "You are trying to read a legacy object without the "
                "pickle_factory plugin. You need the pickle_factory directory in your "
                "PYTHONPATH")
        raw_data = open(self.path, 'rb')
        loaded_data = pickle_factory.load(file=raw_data)
        raw_data.close()
        return loaded_data

    def write(self, data: Any) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """
        try:
            from pickle_factory import base as pickle_factory
        except ImportError:
            raise PickleFileError(
                "You are trying to read a legacy object without the "
                "pickle_factory plugin. You need the pickle_factory directory in your "
                "PYTHONPATH")
        file = open(self.path, 'wb')
        pickle_factory.dump(obj=data, file=file)
```
Here we can see that we need to accept a ```path``` parameter in the constructor, we also have to write our own read and 
write functions. In the example here at monolith we have built our own ```pickle_factory``` for a certain platform so we 
import and use this. We also have to note that there is a ```SUPPORTED_FORMATS```, this list can be as long as you want and 
it's used for mapping the extensions. We have ```["pickle"]``` which means that all files with ```.pickle``` extensions 
will use this object to read and write. if we had ```["pickle", "sav"]```, these functions would be used on files with extensions with either ```.pickle``` or ```.sav```. We can write our custom functions as if we're reading locally, because the module uses
caching when downloading and uploading to s3. This means that the file is cached locally before being uploaded or read and then 
the cache is deleted. This keeps maintaining code around reading and writing from s3 and local consistent and easy to maintain.

Now that we have defined our custom file object, we just need to add it to the file map with the code below:

```python
from some.path import PickleFile

file_map: FileMap = FileMap()
if file_map.get("pickle") is not None:
    del file_map["pickle"]
file_map.add_binding(file_object=PickleFile)
```
The ```FileMap``` is a dictionary and the key is the extension. If we try and add duplicate extensions then the ```add_binding```
function will raise an error. The map is also a Singleton, therefore it's a single point of truth in the application that you 
are building. 


### List Directory
If a file path refers to a directory, you can use `ls` to get all the direct subdirectories and files in that directory.
A tuple of two lists are returned - the list of subdirectories, followed by the list of files.

```python
from monolith_filemanager import file_manager

folder = file_manager(file_path="some/folder")

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