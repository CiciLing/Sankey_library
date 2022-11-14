
import pandas as pd
import sankey as sk

def stacked_df(df,src1,trg1,trg2,val):
    '''
    :param df: original dataframe that contains selected data
    :param src1: factor 1 to investigate, view as source to factor 2
    :param trg1: factor 2 to investigate, view as target to factor 1 & source to factor 2
    :param trg2: factor 3 to investigate, view as target to factor 2
    :param val: count of the grouped columns
    :return: stacked dataframe that combine three factors groups
    '''
    # group factor 1 with factor 2, and factor 2 with factor 3
    df1 = df.groupby([src1, trg1]).size().reset_index(name=val)
    df1.rename(columns={src1: 'Source', trg1: 'Target'}, inplace=True)
    df2 = df.groupby([trg1, trg2]).size().reset_index(name=val)
    df2.rename(columns={trg1: 'Source', trg2: 'Target'}, inplace=True)

    # stake the two dataframe together
    multi = pd.concat([df1, df2], ignore_index=True, axis=0)
    return multi

def extract_local_network(df, col, val, **kwargs):
    '''
    :param df: original dataframe that contains selected data
    :param col: the targets and sources of the sankey diagram
    :param val: the name of grouped count column
    :param kwargs: any other possible factor, eg. minimal count as a filter
    :return: a new dataframe that contain selected factors and their grouped counts
    '''
    # if multi-factors(n > 2), group these factors using stacked_df function
    if len(col) > 2:
        groups = stacked_df(df, col[0],col[1],col[2],val)
    # if only two factors, group the two factors using groupby
    else:
        groups = df.groupby([col[0], col[1]]).size().reset_index(name=val)

    groups.sort_values(val, ascending=False, inplace=True)
    # set a minimal value as a filter so the graph is clearer
    min_val = kwargs.get('min_val', 20)
    groups = groups[groups[val] >= min_val]
    return groups

def execute_sankey(df, col, val):
    '''
    :param df: original dataframe that contains selected data
    :param col: the targets and sources of the sankey diagram
    :param val: the name of grouped count column
    :return: a sankey diagram showing the connections
    '''
    # render the dataset to selected group dataframe
    groups = extract_local_network(df, col, val)

    # if multi-factors(n > 2), refer directly to the renamed source and target
    if len(col) > 2:
        sk.show_sankey(groups, 'Source', 'Target', vals=val)
    # if two factors, refer to the column names
    else:
        sk.show_sankey(groups, col[0], col[1], vals=val)

def main():
    # json file convert to df
    data = pd.read_json('/Users/ciciling/Desktop/DS3500/Artists.json')
    # select only three columns to explore
    artist = data[['Nationality','Gender','BeginDate']]
    print(artist)
    # rename the begindate column
    artist.rename(columns={'BeginDate': 'Decade'}, inplace=True)
    # convert year to decade
    artist['Decade'] = (artist['Decade'] // 10) * 10
    # filter out non-applicable decade
    artist = artist.loc[artist['Decade'] != 0]
    # convert decade from integer to string
    artist['Decade'] = artist['Decade'].astype(str)
    # convert gender to all lower-case
    artist['Gender'] = artist['Gender'].str.lower()

    # relationship with Nationality and Decade
    execute_sankey(artist, ['Nationality','Decade'],'Value')

    # relationship with Nationality and Gender
    execute_sankey(artist, ['Nationality','Gender'],'Value')

    # relationship with Gender and Decade
    execute_sankey(artist, ['Gender', 'Decade'], 'Value')

    # multiple factors
    execute_sankey(artist, ['Nationality','Gender','Decade'], 'Value')

main()
