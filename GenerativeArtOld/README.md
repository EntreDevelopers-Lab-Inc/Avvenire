# Generative Art

## Requirements
- there must be an art folder, which will be taken as an argument
- each art folder must have a config file in it

## Workflow
- generate.py
    - calls HairBrows.py
        - creates hair, brows, exports them to temporary directory
    - calls FaceBody.py
        - creates faces and bodies, exports them to temporary directory
    - merges the HairBrows and FaceBody files
        - use the simple tool, create a config programmatically
    - checks to make sure there are no duplicates within MEMORY
        - later, this will be moved to sql to better track our creations
    - exports everything to some named folder
        - also has "files" and "metadata" subfolders with the appropriate content

## Temporary Directories
- all of the content created will be deleted individually, but the folders will remain
    - each folder will have 2 subfolders: "files" and "metadata"
        - this allows the traits to be joined as well as the files
