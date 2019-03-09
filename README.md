# OpenMC-Dash-Interface
Status: This project has several things that still need to be implemented but progress is coming along nicely and now 
that a basic framework has been set up, additions are become easier to implement.  

![alt text](outputs/Demo.png)
![alt text](outputs/Score.png)


## Summary
I've decided to attempt to replicate (more or less) ERSN for OpenMC (Open Source Monte Carlo Neutron Transport Code) 
but using Dash. This project will create a GUI for setting up OpenMC simulations, running them, and depicting the results. 
Dash is pythonic way of coding HTML and Js with callbacks. Right now the project is segmented into several dash apps in 
the `parameters` directory. You can now run `main.py` in the project directory (`dev` branch) to get a feel for what the application will
offer. If you have any suggestions regarding the layout, I am open to criticism and I might be able to explain the rational
for certain decisions.

It is unlikely that I will be able to create support for every feature of OpenMC by myself so the goal right now is to 
merely get a UI working for your average joe or NUEN B.S. college student, then maybe add support where requests 
are made. 

### TODO List
##### Materials:
##### Geometry:
- Set whole geometry boundary boundaries/min/max based on geometry dimensions
##### Mesh:
- Finish Layout
- Create Callbacks
##### Cross-Sections:
- Finish Layout
    - energy/delayed groups specification 
    - Mesh specification
    - Cross-Section type dropdown
##### Tallies & Settings:
- Finish Layout
- Create Callbacks

#### TODO's:
- Make boundaries dependent on root region
- ~~Create cross-section graphs for radionuclides~~
- Add 3D rendering of geometry

