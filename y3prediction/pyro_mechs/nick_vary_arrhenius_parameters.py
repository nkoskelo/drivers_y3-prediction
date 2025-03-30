import yaml

import cantera
import pyrometheus as pyro
import numpy as np
import os

my_file = "sandiego.yaml"
num_samples = 20

sample_range = 0.2 # 20 percent of the nominal value U(0.8 nom, 1.2 nom)

with open(my_file, "r") as stream:

    data = yaml.safe_load(stream)

    new_data = data.copy()

    known_reactions = {}
    params = np.zeros((len(data["reactions"]), num_samples))
    for i, reaction in enumerate(data["reactions"]):
        eqn = reaction["equation"]
        if eqn in known_reactions:
            params[i] = known_reactions[eqn]
        else:
            if "rate-constant" not in reaction:
                continue # We are not changing these.
            tmp = ((np.random.random(num_samples) * (2*sample_range)) + (1 - sample_range))*reaction["rate-constant"]["A"]
            params[i] = tmp
            known_reactions[eqn] = tmp

    fnames = []
    for snum in range(num_samples):
        for i, reaction in enumerate(data["reactions"]):
            if "rate-constant" not in reaction:
                new_data["reactions"][i] = reaction
            else:
                new_data["reactions"][i]["rate-constant"]["A"] = float(params[i, snum])
        new_file = f"sandiego_realization_{snum}.yaml"
        fnames.append(new_file)
        with open(new_file, "w+") as file:
            yaml.dump(new_data, file)

    print(os.listdir())

    # Now we need to build the cantera files.
    for file in fnames:
        sol = cantera.Solution(file, "gas")
        
        # Save to a set of python files.
        from pathlib import Path
        fstem = Path(f"{file}").stem
        with open(f"{fstem}.py", "w") as pyfile:
            code = pyro.codegen.python.gen_thermochem_code(sol)
            print(code, file=pyfile)

