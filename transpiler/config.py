# this should be true if its sure that every template resets the temp variables it uses. This is the case for all templates in the current implementation.
# this is also especially important because wasm allows to have only 1000 parameters in a function, so if we have a lot of temp variables, we need to reuse them.
TEMP_VARIABLE_REUSE_SAME_SCOPE = True

## this sets the output format with or without comments
ALLOW_COMMENTS = False