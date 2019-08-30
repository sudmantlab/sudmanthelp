import pandas as pd
import numpy as np
from stats import *

def stack_df(input_list, output_name, save=True, dropna=False, index_col=0, header=0, **kwargs):
    if input_list is None:
        return pd.DataFrame()
    df_inputs = [pd.read_csv(name, sep='\t', index_col=index_col, header=header) for name in input_list]
    df = pd.concat(df_inputs, **kwargs)
    if dropna:
        df = df.dropna(axis=0, how='all')

    if save:
        df.to_csv(output_name, sep='\t')
    return df


def _df_find_cards(template, string, constraints='.*', ignore_case=True):
    """
    This is a copy of find_cards in io.py
    find the wildcard values in a given template
    according to a given string
    """
    wildkeys = [re.sub('{|}', '', card).split(':')[0] for card in re.findall("{[^{}]*}", template)]
    wildcards = _get_constraints(wildkeys, constraints=constraints)
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(template.format(**wildcards), flags=flags)
    re_match = re.match(pattern, string)
    if re_match:
        return dict(zip(wildkeys, list(re_match.groups())))
    else:
        return dict()


def stack_tidy(input_list, output_name, input_pattern=None, index_col=None, header=0):
    """
    stack data frames in input_list
    add corresponding
    """
    df_inputs = []
    for name in input_list:
        df_input = pd.read_csv(name, sep='\t', index_col=index_col, header=header)
        if len(df_input) == 0:
            continue
        if input_pattern is None:
            wildcard_info = dict()
        else:
            wildcard_info = _df_find_cards(input_pattern, name)
        for k, v in wildcard_info.items():
            while k in df_input:
                k = k + "_1"
            df_input[k] = v
        df_inputs.append(df_input)
    df = pd.concat(df_inputs)
    save_index = index_col is not None
    save_header = header is not None
    df.to_csv(output_name, sep='\t', index=save_index, header=save_header)


def analyze(info, expr, x_col, output, func, metrics=None, **kwargs):
    df_info = pd.read_csv(info, compression='gzip', sep='\t', index_col=0, header=0)
    df_expr = pd.read_csv(expr, sep='\t', index_col=0, header=0)
    df_info_this = df_info.loc[df_info.index.isin(df_expr.columns.values)]
    df_x = df_info_this[x_col]

    result_tuples = []
    is_empty = True
    for i, expr_row in df_expr.iterrows():
        df = pd.concat([df_x, expr_row], axis=1, sort=True)
        x = df.iloc[:,0].values
        y = df.iloc[:,1].values
        if df.empty:
            result_tuples.append(func([np.nan], [np.nan], **kwargs))
        else:
            result_tuples.append(func(x, y, **kwargs))
        is_empty = False

    df_output = pd.DataFrame(np.asarray(result_tuples), index=df_expr.index, columns=metrics)
    df_output.to_csv(output, sep='\t')

    return df_output


def find_cutoff(pos, neg, FDR=0.05, reverse=True):
    """
    find the cutoff for a given False Discovery Rate (FDR)
    input arguments have to be numpy arrays
    """
    sorted_values = np.sort(np.concatenate((pos[np.logical_not(np.isnan(pos))], neg[np.logical_not(np.isnan(neg))]), axis=None), axis=None)
    if reverse:
        sorted_values = sorted_values[::-1]
    for value in sorted_values:
        pos_count = np.sum(pos <= value)
        neg_count = np.sum(neg <= value)
        fdrs = neg_count /( neg_count + pos_count )
        if fdrs <= FDR:
            return value
    return np.nan
