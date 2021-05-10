# Local File Protocols
This is where the reading and writing protocols for local file storage are stored. 
The custom dict that manages the pairing of the different types is located in the ```__init__.py```
file. 

## Adding new file types
You will have to register your new file type with the ```FileMap``` object in the ```__init__.py``` file
in order for the file manager to access it. To register it, import it in the following function:

```python
    def init_bindings(self):
        """
        Imports and loads the file objects.

        :return: None
        """
        if self.bindings_imported is False:
            from general_filemanager.file.pandas_file import PandasFile
            self.add_binding(file_object=PandasFile)

            self.bindings_imported = True
```

Let say we add another, it would be like:
```python
    def init_bindings(self):
        """
        Imports and loads the file objects.

        :return: None
        """
        if self.bindings_imported is False:
            from general_filemanager.file.pandas_file import PandasFile
            self.add_binding(file_object=PandasFile)
            from general_filemanager.file.pickle_file import PickleFile
            self.add_binding(file_object=PickleFile)

            self.bindings_imported = True
```
This dynamic import gives you full freedom in your class with class attributes. These will not get 
fired every time the the ```__init__.py``` file is passed. The ```FileMap``` is also a singleton 
and even if the ```init_bindings``` function is fired again it will not do another round of imports 
due to the attribute ```bindings_imported```. 

It will automatically warn you if your new file type clashes with other file types. 