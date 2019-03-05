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

![alt text](https://github.com/SterlingButters/OpenMC-Dash-InterFace/blob/master/examples/Demo.png)
![alt text](https://github.com/SterlingButters/OpenMC-Dash-InterFace/blob/master/examples/Score.png)


## Summary
I've been wanting to do a project using Dash now for some time. I've decided to attempt to replicate (more or less) 
ERSN for OpenMC (Open Source Monte Carlo Neutron Transport Code) but using Dash. This project will create a GUI for 
setting up OpenMC simulations, running them, and depicting the results. Dash is pythonic way of coding HTML and Js with 
callbacks. Clone the project and run `main.py` in the main directory.

### Desired 1st release features
##### Materials:
##### Geometry:
- Cell region select feature
- Assembly-cell selection feature
- Assembly fill dropdown with 2 buttons (fill whole assembly, fill selected)
- Set whole geometry boundary boundaries/min/max based on geometry dimensions (set percentage of boundary clearance)
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

##### Misc:
- messages everywhere with some documentation between to explain to user both the interface and what selections mean
	

#### TODO's:
- Support 5 cell types and 3 assembly types until dynamic callbacks are available (or find workaround)
- Fix "geometrical boundary config" dependent on assembly
- Make boundaries dependent on root region
- Figure out why not all messages display
- ~~Create cross-section graphs for radionuclides~~
- Add 3D rendering of geometry... should be easy


#### Wishlist:
- better isotope selection
- all planes
- 3d depiction of geometry
- highlight cell region
- get cell relayout for dims
- periodic boundary conditions
