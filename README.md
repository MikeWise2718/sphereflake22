# Extension Project SphereFlake Benchmark for Omniverse


Tested and works with Python 3.7 and 3.10 and Omniverse Kit 104 and 105

# To use
- Add it to create or code by adding to the Extension Search Path:  
   - Under `Window/Extensions` then click on the gear (or lately the hamburger menu in the top middle part of the dialog box)
   - in the general case: `(your ext subdir root)/sphereflake22/exts`
   - in my case: `d:/nv/ov/ext/sphereflake22/exts`

# Program Structure
- The core are the objects in the subdir `sfgen`
    - `SphereFlake` - in `sphereflake.py` an object that construcsts sphereflakes in various ways    
    - `SphereMesh` - in `spheremesh.py` an object that constructs a spheremesh when needed
    - `sfut.MatMan` - in `sfut.py` an object that manages the materials, fetching them when needed

- Additionally there are two main control classes
    - `sfwindow` - in `sfwindow.py` and does all the UI and the only file that imports `Omni.ui`
    - `sfcontrol` - in `sfcontrol.py` anddoes all the control logic (it has gotten a bit big)

- For UI there are a number of files organized by tabs
    - `sfwintabs.py` - Most tabs
    - `sfwinsess.py` - the session tab


# Adding UI ELements

## Adding a tab
   - Add tab class, to `sfwintabs` probably, or to its own file if it is large
   - Add invocation to `sfwindow` build function
   - No settings 


## Adding a collapsable frame
   - Example "Ground Settings" collapsable frame
   - `sfwindow.py` -Add variables to class `SfWindow` as member variables
       -  `optgroundframe: ui.CollapsableFrame = None`
       -  `docollapse_optgroundframe = False`
   - `sfwindow.py` - Add load/save functionality to `LoadSettings` and `SaveSettings` for collapsed state
      -   `self.docollapse_optgroundframe = get_setting("ui_opt_groundframe", False)`
      -   `save_setting("ui_opt_logframe", self.optlogframe.collapsed)`
   - `sfwintabspy` - Add frame to tab class
        - `sfw.optgroundframe = ui.CollapsableFrame("Ground Settings", collapsed=sfw.docollapse_optremoteframe)`
   -  `sfwintabspy` - Add additional ui code to tab class:
        - `with sfw.optgroundframe:`

## Adding a button to do something
   - Example "Reset Materials"
   - `sfwindow.py` - Add variables to class `SfWindow` as member variables (not needed here)
   - `sfwintabs.py` - Add button code with lambda function (might need to move it because of width)
```   
            sfw.reset_materials_but = ui.Button(f"Reset Materials",
                                                style={'background_color': sfw.darkpurple},
                                                clicked_fn=lambda: sfc.on_click_resetmaterials())
```                                          
   - Add click function:
```
    def on_click_resetmaterials(self):
        self._matman.Reinitialize()
        nmat = self._matman.GetMaterialCount()
        self.sfw.reset_materials_but.text = f"Reset Materials ({nmat} defined)"      
```   

## Adding a checkbox
   - Example "Add Rand" checkbox
   - Decide if control variable belongs in Controller or in an object (like SphereFlake)
   - Here we are putting it in the Controller "SfControl" class
   - `sfwindow.py` - Add variables to class `SfWindow` as member variables
        - `addrand_checkbox: ui.CheckBox = None`
        - `addrand_checkbox_model: ui.SimpleBoolModel = None`
   - `sfcontrol.py` - Add state variable to class `SfControl` as member variable
        - `p_addrand = False`
   - `sfcontrol.py` - Add load/save functionality for state variable to class `SfControl` in `LoadSettings` and `SaveSettings`
        - `self.p_addrand = get_setting("p_addrand", False)`
        - `save_setting("p_addrand", self.p_addrand)`
   - `sfwindow.py` - Add initialization code for `SimpleBoolModel`
        - self.addrand_checkbox_model = ui.SimpleBoolModel(sfc.p_addrand)
   - `sfwintabs.py` - Add checkbox functionality



## Adding a stringfield


## Adding a combobox


## Adding a slider

