# S3 Storage
This document covers the process of Monolith's S3 Storage module. 

## Structure
The following structure defines the flat module:

```
├── __init__.py
├── bucket_manager.py
├── errors.py
└── file_manager.py
```
The engine is stored in the ```__init__.py```. It's currently got a flat structure as there doesn't seem to be a need for complex design at this stage. If common patterns start to arise then developing a deeper structure can be explored. Right now the engine uses multiple inheritance. The two objects it inherits (file and bucket managers) are not tied. If the implementation of this module remains simple in the future with no need for more development, the file manager could simply inherit the bucker manager. However, if protocols such as back-up or migration are needed then this approach should be kept as these protocols can be defined in the engine. 

## Use
Below is an example of using the engine pickle a list, upload it, download it, and deserialise it for use:

```python
from general_filemanager.s3storage import V1Engine
import pickle

test = V1Engine()
bucket = 'demo-data.monolith'
data = pickle.dumps([1, 2, 3])

test.upload_serialised_data(bucket_name=bucket, file_name="test-list.pkl", data=data)

downloaded_data = test.download_file_to_memory(bucket_name=bucket,
                                                       file_name="test-list.pkl")

usable_data = pickle.loads(downloaded_data)
```

## To Do
Right now the standlone module works out of the box and can be used but below are some areas that could be developed:

- **path protocols**: Right now the ```FileManager``` is merely holding ```self.BASE_DIR``` and ```self.FILE_PATH``` to manage the download to disk and upload from disk functions. Agreemet on disk upload/download protocols with defined paths should really be agreed on before this gets implemented.
-  **creating buckets**: The function for creating a bucket exists however, it complains about not defining a region. This bug fix isn't essential as I doubt that we have automated functions that are creating buckets right now, however, it should be fixed at some point.
-  **naming convention**: naming convention needs to be agreed on. Right now before uploading, the ```FileManager``` just uploads the name passed to it. When downloading it does the same. This doesn't affect the user interface and tells use where a file should be. However, there is a risk of versions getting in the way. It would be nice to agree on a naming protocol that indicates a version so this can be managed. 