# Adapters 
This is where the adapters are stored. Adapters act as an interface between the user and the 
type of protocols needed to manage the file. 

## Adding a new adapter
New adapters need to inherit the ```Base``` class from  the ```base.py``` file. In order for the 
user to use the new adapter, it also has to be registered in the factory which is located in the 
```__init__.py``` file. Each adapter needs the following functions:

- ```read_file(self)```
- ```write_file(self, data)```
- ```delete_file(self)```