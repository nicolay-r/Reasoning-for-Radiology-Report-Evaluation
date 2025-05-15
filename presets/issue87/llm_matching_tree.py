from core.utils import seek_pattern


def do_pattern_tree_matching(text, tree, handle=None):
    """ Parsing LLM responses using the tree-based pattern matching.
    """

    # Setup initial state.
    state = "__init__"

    while state in tree:

        next_states = []

        # Extracting parameters.
        params = tree[state]
        handler_type = params[0]
        states = params[1:]

        assert isinstance(handler_type, str), "The handler type is unknown!"

        if handler_type == "if-else":
            assert (len(states) == 2)
            if_true_patterns, if_true_state = states[0]
            ind_aft = seek_pattern(text, if_true_patterns, return_mode="ind_aft")
            next_states = [(if_true_state, ind_aft) if ind_aft >= 0 else (states[-1], 0)]

        elif handler_type == "choice":
            for patterns_list, new_state in states:

                if patterns_list is None and len(next_states) == 0:
                    # This is the exceptional case when we can't find anything else.
                    ind_aft = 0
                else:
                    ind_aft = seek_pattern(text, patterns_list if patterns_list is not None else [], return_mode="ind_aft")

                if not ind_aft >= 0:
                    continue
                # Result is presented.
                next_states.append((new_state, ind_aft))
        else:
            raise Exception(f"Handler type is not supported: `{handler_type}`")

        if len(next_states) > 1:
            if handle is not None:
                handle(f"---\nMULTIPLE CHOICES: `{next_states}`\n{text}")
            state = None
            break

        if len(next_states) == 0:
            if handle is not None:
                handle(f"---\nNON TERMINATED STATE: `{state}`\n{text}")
            state = None
            break

        # OK, go further.
        new_state, next_text_from = next_states[0]
        state = new_state

        # Remove text part before.
        text = text[next_text_from:]

    return state
