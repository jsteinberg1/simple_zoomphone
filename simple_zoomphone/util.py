def validateparam(parameter, valid_values, error_to_raise):
    if parameter != None:
        if parameter not in valid_values:
            raise ValueError(error_to_raise)