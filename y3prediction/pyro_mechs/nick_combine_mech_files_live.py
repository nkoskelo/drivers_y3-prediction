import numpy as np
import importlib

from arraycontext.parameter_study import(
    pack_for_parameter_study,
    ParameterStudyAxisTag,
)

from mirgecom.thermochemistry import get_pyrometheus_wrapper_class


def combine_multiple_pyro_files_into_one(pyfiles_to_import, actx, zero_level, temperature_niter):


    libs = [importlib.import_module(f"y3prediction.pyro_mechs.{file}") for file in pyfiles_to_import] # The file names are just the last portion.
    classes = [get_pyrometheus_wrapper_class(lib.Thermochemistry, temperature_niter=temperature_niter, zero_level=zero_level)(actx.np) for lib in libs]

    comb_class = get_pyrometheus_wrapper_class(libs[0].Thermochemistry, temperature_niter=temperature_niter, zero_level=zero_level)(actx.np)

    assert len(classes) > 0
    # We are assuming all the classes have the same structure here.
    for attr in dir(classes[0]):
        if "pre_expfactor" in attr:
            # This is something we want to combine
            # because it is what we are varying, the Arrhenius coefficient.
            setattr(comb_class, attr,
                    pack_for_parameter_study(actx,
                                             ParameterStudyAxisTag, 
                                             *[actx.from_numpy(np.array(getattr(myclass, attr))) \
                                        for myclass in classes]))

    return comb_class
