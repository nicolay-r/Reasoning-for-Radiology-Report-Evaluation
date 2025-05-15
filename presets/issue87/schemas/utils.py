def manual_terms_split(line, separators=None, clean_comma=True, clean_brackets=True):
    # Several reports might be taken in brackets.
    if clean_brackets:
        if len(line) > 0 and line[0] == '(' and line[-1] == ')':
            line = line[1:-1]

    separators = [' ', '_', '/'] if separators is None else separators
    entries = []

    # Assessing frequency of separator appearances.
    template = ""
    while len(line) > 0 and template is not None:

        template = None
        min_ind = len(line) + 1

        for s in separators:
            if s in line:
                entry_ind = min(min_ind, line.index(s))
                if entry_ind < min_ind:
                    template = s
                    min_ind = entry_ind

        if template is None:
            break

        entries.append(line[:min_ind])
        line = line[min_ind + len(template):]

    if len(line) > 0:
        entries.append(line[:min_ind])

    # clean empty entries.
    entries = [e for e in entries if len(e) > 0]

    # optionally clean commas in the end.
    if clean_comma:
        entries = [e[:-1] if e[-1] == ',' else e for e in entries]

    return entries
