def _concat_constraints(constraints):
    """
    Concatenate a list of constraints to a regrep pattern
    """
    if isinstance(constraints, str):
        return '(' + constraints + ')'
    elif isinstance(constraints, (list, tuple)):
        return '(.*' + '.*|.*'.join(constraints) + '.*)'
    else:
        return '(.*)'


def _get_constraints(wildcards, constraints='.*'):
    """
    Given a old_wildcard, add the constraints, return a new_wildcards
    """
    temp_constraints = {}
    if isinstance(constraints, dict):
        for key in wildcards:
            if key in constraints:
                temp_constraints[key] = _concat_constraints(constraints[key])
            else:
                temp_constraints[key] = '(.*)'
    elif isinstance(constraints, (list, tuple)):
        for i, key in enumerate(wildcards):
            if i < len(constraints):
                temp_constraints[key] = _concat_constraints(constraints[i])
            else:
                temp_constraints[key] = '(.*)'
    else:
        if not isinstance(constraints, str):
            constraints = '(.*)'
        for key in wildcards:
            temp_constraints[key] = '(' + constraints + ')'
    return temp_constraints


def dictArray_to_listDict(dictArray, mesh=False):
    if not dictArray:
        return []
    if mesh:
        import numpy as np
        list_values = [v for _, v in dictArray.items()]
        mesh_values = [nparray.flatten() for nparray in np.meshgrid(*list_values)]
        return_list = []
        for iv in range(mesh_values[0].size):
            temp_dict = {}
            for ik, k in enumerate(dictArray.keys()):
                temp_dict[k] = mesh_values[ik][iv]
            return_list.append(temp_dict)
    else:
        min_length = min([len(v) if isinstance(v, list) else 1 for _, v in dictArray.items()])
        return_list = []
        for i in range(min_length):
            temp_dict = {}
            for k, v in dictArray.items():
                if isinstance(v, list):
                    temp_dict[k] = v[i]
                else:
                    temp_dict[k] = v
            return_list.append(temp_dict)
    return return_list


def get_files(input_name, output_name=None, constraints='.*', ignore_case=True, mesh=False):
    """
    Search in the directory of input_name
    Find the wildcard wildcard values
    Feed wildcard values into output_name and return
    A constraint can be given to find partial matches
    If additional constraints of the output_name wildcards are provided, they will be used in the output to replace those name cards;
    It should be noted that if the additional constraints are lists, a meshgrid or a paired list will be returned depending on the input key word 'mesh'

    Assumptions:
    1. wildcards only contain names but not constraints
    2. no wildcard in the directory of the input name
    """
    import re, os
    if output_name is None:
        output_name = input_name
    dirname = os.path.dirname(input_name) or '.'
    pattern = os.path.basename(input_name)
    old_wildcards = [re.sub('{|}', '', card).split(':')[0] for card in re.findall("{.*?}", input_name)]
    new_wildcards = [re.sub('{|}', '', card).split(':')[0] for card in re.findall("{.*?}", output_name)]
    files = os.listdir(dirname)

    temp_constraints = _get_constraints(old_wildcards, constraints=constraints)

    pattern = pattern.format(**temp_constraints)
    pattern = pattern.encode().decode()
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(pattern, flags=flags)
    filenames = []

    # get extra wildcards
    if isinstance(constraints, dict):
        constraints = dict(constraints)
        for key in list(constraints.keys()):
            if key in old_wildcards or key not in new_wildcards:
                del constraints[key]
        list_constraints = dictArray_to_listDict(constraints)
    else:
        list_constraints = None

    for string in files:
        re_match = re.match(pattern, string)
        if re_match:
            wildcard_values = {}
            for i, key in enumerate(old_wildcards):
                if key in new_wildcards:
                    wildcard_values[key] = re_match.group(i + 1)

            if list_constraints:
                for i, key in enumerate(new_wildcards):
                    if key not in wildcard_values and key not in constraints:
                            wildcard_values[key] = ''
                for extra_constraints in list_constraints:
                    for k, v in extra_constraints.items():
                        wildcard_values[k] = v
                    filenames.append(output_name.format(**wildcard_values))
            else:
                for i, key in enumerate(new_wildcards):
                    if key not in wildcard_values:
                            wildcard_values[key] = '{' + key +'}'
                filenames.append(output_name.format(**wildcard_values))

    return list(set(filenames))


def fill_cards(template, wildvalues):
    """
    set the wildcard values to the wildcards in the template
    """
    import re
    Warning("This function is deprecated")
    wildkeys = [re.sub('{|}', '', card).split(':')[0] for card in re.findall("{[^{}]*}", template)]
    fillcards = {}
    if isinstance(wildvalues, (tuple, list)):
        Warning("The order of wildcard values might not be the same as those in the template")
        for i, k in enumerate(wildkeys):
            if i < len(wildvalues):
                fillcards[k] = wildvalues[i]
            else:
                fillcards[k] = '{' + k + '}'
    elif isinstance(wildvalues, dict):
        for i, k in enumerate(wildkeys):
            if k in wildvalues:
                fillcards[k] = wildvalues[k]
            else:
                fillcards[k] = '{' + k + '}'
    else:
        Warning("No wildcard values are given. Return the template")
        for k in wildkeys:
            fillcards[k] = '{' + k + '}'
    return template.format(**fillcards)


def find_cards(template, string, constraints='.*', ignore_case=True, return_dict=False):
    """
    find the wildcard values in a given template
    according to a given string
    """
    import re
    wildkeys = [re.sub('{|}', '', card).split(':')[0] for card in re.findall("{[^{}]*}", template)]
    wildcards = _get_constraints(wildkeys, constraints=constraints)
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(template.format(**wildcards), flags=flags)
    re_match = re.match(pattern, string)
    if re_match:
        if return_dict:
            return dict(zip(wildkeys, list(re_match.groups())))
        else:
            return re_match.groups()
    else:
        if return_dict:
            return dict()
        else:
            return []


def format_cards(template, mesh=False, **kwargs):
    """
    partially format a given wildcard template
    From: https://stackoverflow.com/questions/11283961/partial-string-formatting
    """
    import string
    class FormatDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"
    list_kwargs = dictArray_to_listDict(kwargs, mesh=mesh)
    return_list = []
    for kwarg in list_kwargs:
        formatter = string.Formatter()
        mapping = FormatDict(**kwarg)
        return_list.append(formatter.vformat(template, (), mapping))
    return return_list


def rm_extension(filename, n=1, delimiter="."):
    """
    iteratively removing the extension
    """
    for i in range(n):
        filename = filename[:filename.rfind(delimiter)]
    return filename
