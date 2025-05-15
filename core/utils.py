def iter_to_iterator(items_it, iter_item_func=None):
    for item in items_it:
        item_it = iter_item_func(item) if iter_item_func is not None else item
        for item_elem in item_it:
            yield item_elem


def seek_pattern(text, ordered_patterns, return_mode=None):
    assert (isinstance(ordered_patterns, list))

    assert (return_mode in ["ind_aft", None])
    f = None
    for p in ordered_patterns:
        if p in text:
            f = p
            break

    if return_mode is None:
        return f is not None
    elif return_mode == "ind_aft":
        return text.index(f) + len(f) if f is not None else -1