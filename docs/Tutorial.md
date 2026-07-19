# Interactive Tutorial: Vibe Coding with NIA

Welcome to the future of software development. **Vibe Coding** allows you to describe a problem, and NIA’s `CodeAgent` will autonomously write, test, and execute the solution locally on your machine.

---

## What is Vibe Coding?
Instead of writing syntax, you describe the "vibe" or the outcome you want. NIA translates this intent into functioning Python or JavaScript, executes it, reads the terminal output, and iterates if there are errors.

## Step-by-step Guide

### 1. Activating Vibe Mode
1. Open the NIA Dashboard (`http://localhost:3000/hub`).
2. Look at the **Command Bar** at the bottom of the screen.
3. Click the purple **`< > Vibe`** toggle. The input placeholder will change to *"Describe what to build... NIA will vibe-code it."*

### 2. Giving a Command
With Vibe mode active, you are talking directly to the `CodeAgent` backend.

**Try typing this command:**
> *"Write a python script that organizes all my downloaded images into folders based on their creation year."*

### 3. Watching the Execution
Once you hit **Execute**:
1. Check the **Vision Stream** (Left Panel). You will see the agent's thought process in real-time.
2. The `CodeAgent` will generate the script locally in the `agent-core` workspace.
3. It will execute the script using `subprocess.run()`.
4. If it encounters a missing dependency (e.g., `Pillow`), NIA will automatically run `pip install`, update its memory, and retry the execution.

### 4. Advanced: Visual UI Debugging
If you are building front-end components, you can use **Visual Grounding**. 
Ask NIA:
> *"Vibe code a login form, then use your vision to tell me if the button is properly aligned."*

NIA will write the code, render it, and use the `VisionModule` to capture its own screen, map the coordinates, and verify the UI alignment.

---

*Enjoy building at the speed of thought. You are now a Sovereign Developer.*
