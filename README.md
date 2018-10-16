
# recboard - Recommendation models as a service [![CircleCI](https://circleci.com/gh/mohit-chawla/recboard.svg?style=svg)](https://circleci.com/gh/mohit-chawla/recboard)

Recboard aims to provide recommedation models as a service. We use [openrec](http://openrec.ai) (Check it out, its cool!) for modular recommendation systems.

### **Objectives:**
Recboard plans to satisfy the following objectives:
- Create recommendation systems on the fly via a UI or a command line tool.
- Visualize model training (running locally or in a remote machine) and results.
- Serve the trained model as a REST API.


### **Contrbutions**
This project is not open for contributions, as of now. 
This is a semester project, for now.
Once we have a PoC that resonates well with users, we will clean (some / all) code and then open this for contributions. :)

### **Wiki**

All fun stuff [here](https://github.com/mohit-chawla/recboard/wiki)


### Fun questions 
**Why are we not using golang?** 
We know that golang would have been a better choice considering mem usage of goroutines but we constrained due to human factors (experience, community here, libraries we are using and most importantly time [This is supposed to a PoC, for now.].).

**If you are using python, Why no react?**
We know react has faster rendering and other benefits. But it has a steep learning curve and we want to complete a user-testable PoC ASAP. 

**Okay, but atleast you could have used gRPC?**
You might want to read [this](https://github.com/mohit-chawla/recboard/wiki).

**Other**
Feel free to roast [link](mc2683@cornell.edu or [link](ks2259@cornell.edu)

### **Stack we are using**

-Backend
  - Django (python)
  - ~~gRPC~~ 
  
-Frontend
