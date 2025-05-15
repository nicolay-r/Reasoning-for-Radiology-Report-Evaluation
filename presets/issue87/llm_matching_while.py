def do_while_not_true(line, params, handle=None):
    assert (isinstance(params, list))
    for f, r in params:
        if f(line):
            return r

    if handle is not None:
        handle(f"---\nNON TERMINATED STATE: \n{line}\n{params}")
