# OpenMC-Dash-Interface
Status: ~~This project has been put on hold due to the lack interactivity allowable by Dash. Since OpenMC is coupled so 
intensely to the interactivity of the interface, I cannot make further progress until issues such as the following are 
addressed:~~

- [Component property 'figure' will not update hover-text for go.Heatmap object](https://github.com/plotly/dash/issues/235) 
- [Can same component id reside in input/state and output simultaneously?](https://community.plot.ly/t/can-same-component-id-reside-in-input-state-and-output-simultaneously/9125/14) 

~~The problem, specifically, is that it is difficult to code around an object or function whose attributes can serve as both 
*Inputs* and *Outputs*. It seems Dash is supposed to be to handle this sort of thing though I have not found a working 
solution as of yet. In addition, OpenMC objects cannot be handled in client-side javascript thus they must be globally stored
in Python which is not recommended if individual user sessions are desired (which they might be in the future). The 
combination of these obstacles and the notable issues above encourage a temporary hold until functionality can be created.~~ 

I am attempting to essentially restart this problem from scratch. over the course of time, I have had a chance to reevaluate
potential solutions to certain issues. Standby for results though it may be awhile. 

![alt text](outputs/Demo.png)
![alt text](outputs/Score.png)


## Summary
I've decided to attempt to replicate (more or less) 
ERSN for OpenMC (Open Source Monte Carlo Neutron Transport Code) but using Dash. This project will create a GUI for 
setting up OpenMC simulations, running them, and depicting the results. Dash is pythonic way of coding HTML and Js with 
callbacks. Right now the project is segmented into several dash apps in the `parameters` directory. While you can run 
`main.py` in the project directory, it wont do much for you - I am merely using it as a reference. Once each dash app is 
working individually, I will combine them into a single application. 

It is unlikely that I will be able to create support for every feature of OpenMC by myself so the goal right now is to 
merely get a UI working for your average joe or NUEN B.S. college student, then maybe add support where requests 
are made. 

### Desired 1st release features
##### Materials:
##### Geometry:
- ~~Cell region select feature~~
- ~~Assembly-cell selection feature~~
- ~~Assembly fill dropdown~~
- Set whole geometry boundary boundaries/min/max based on geometry dimensions
##### Mesh:
- set resolution
##### Cross-Sections:
- energy groups selection and mesh selection
- maybe delayed groups
- maybe cross-section type (like scores)
##### Tallies:
- mesh filters and scores
##### Settings:
- batches (total & inactive)
- particles
- generation/batch
- most other settings
- particle traces

#### TODO's:
- Make boundaries dependent on root region
- ~~Create cross-section graphs for radionuclides~~
- Add 3D rendering of geometry

