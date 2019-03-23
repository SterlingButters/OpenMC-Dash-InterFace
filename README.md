# OpenMC-Dash-Interface
#### STATUS UPDATE: Now capable of running simulations for cells and assemblies

[Heroku Demonstration](https://openmc-dash-interface.herokuapp.com/parameters/material) 
(can't run simulations on Heroku deployment until cross-sections are implemented into environment):


![alt text](examples/material_demo_page.png)
![alt text](examples/geometry_demo_page.png)
![alt text](examples/mesh_demo_page.png)
![alt text](examples/settings_demo_page.png)
![alt text](examples/runtime_demo_page.png)

![alt text](examples/Score.png)

## Summary
This project intends to create a GUI for setting up OpenMC simulations, running them, and depicting the results. 
Dash is pythonic way of coding HTML and JavaScript with callbacks. Right now the project is segmented into several dash apps in 
the `parameters` directory. You can now run `main.py` in the project directory to get a feel for what the application will
offer. If you have any support questions, feel free to open an issue.

It is unlikely that I will be able to create support for *every* feature of OpenMC by myself so the goal right now is to 
merely get a UI working for those interested in exploring the basics of Nuclear Engineering, then maybe add support where requests 
are made. 

## Current Deployment TODO List
- Cross-sections library upload + environment variable
https://devcenter.heroku.com/articles/s3

### Current release TODO List
##### Geometry:
- Set Max Geometrical Boundaries based on Root Geometry in (%)
    - Getting weird behavior
- Make marker sizes proportional to dims of geometry (would need rectangle markers -> false: more cells doesnt change dims; would need rectangles if )
##### Mesh:
##### Cross-Sections:
##### Tallies & Settings:
- Look into rest of filters: https://openmc.readthedocs.io/en/stable/pythonapi/base.html#coarse-mesh-finite-difference-acceleration
##### Other:
- Clean up with dash multi-output support (esp `Store` components)

### Next Release Features
- Post Processing -> Clean up interface, handle uploaded files, etc
- Hexagonal Lattices
- Full Core Model 
    
- Finish Settings: https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.Settings.html?highlight=openmc.Settings
    - Source Specification (https://openmc.readthedocs.io/en/stable/pythonapi/stats.html): 
        - Remaining: Cartesian Independent
    - 
    
    
- Dispersed Knowledge/Guidance, research tooltips

### Future Releases
- Burnup and Depletion

#### Unnecessary Beautification Features
- Expand Lists in Material Table
- Add Density & Melting Point to Periodic Table: https://www.ptable.com/#Property/MeltingPoint
- 3D Rendering of Geometry
- Graph Cell(s)/Assembly(ies) from Memory
- Add Snackbars to Alert User that configs have been accepted into data (easy with multi-output)
    - This behaves oddly -> find alternative

#### Questionable Features
- Removal of items from memory
- File Browser: https://github.com/uptick/react-keyed-file-browser

# Contributing
See TODO Lists

*Basic concept*:
The original approach to this interface was to build the model a piece at a time in a corresponding callback.
While this may or may not sound intuitive to you, it is the wrong approach because handling objects is difficult
in Dash due to storage mechanisms and requirements i.e. a Redis server would allegedly handle object storage but 
I had no such success. Instead, the option we are left with is, in fact, much more modular in that the interface 
is nearly completely separate from the model building which happens all in one callback. This single callback 
references ALL the data that has been put into storage to create the model. As far as OpenMC goes, this is nice 
because their is no need to much of the functionality that OpenMC provides e.g. removing nuclides or changing 
geometry, etc. Instead, all of the data is tailored in the interface prior to model creation. You will notice 
that many of the storage callbacks *could* be merged but it was much easier to limit the amount of information in 
each component for debugging purposes. 

Happy to take on collaborators.

Email: sterlingbutters@gmail.com
