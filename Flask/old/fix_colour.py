import pandas as pd
import io
import os
import numpy as np
from string import ascii_lowercase
from werkzeug.utils import secure_filename
from pathlib import Path



def colour(df, rowname, listofcolnames, weightvar=None):
    def sigp(p1, p2, n1, n2):
        if p1 != 0 and p2 != 0 and p1 != p2:
            ppool = (n1 * p1 + n2 * p2) / (n1 + n2)
            se = float((ppool * (1 - ppool) * (1 / n1 + 1 / n2)) ** 0.5)
            se = 1 / se
            z = (p1 - p2) * se
            r = 0
            if z > 1.96:
                r = 1
            else:
                r = 0
            return r
        else:
            return 0

    def producecross1(colname):
        if weightvar is not None:
            cross1 = pd.crosstab(df1[rowname], df1[colname], values=df[weightvar], aggfunc='sum', normalize='columns')
            cross1.loc['sigtest0'] = ''
            df_insert = pd.DataFrame(cross1.loc['sigtest0']).transpose()
            for idx in range(0, 2 * (len(cross1)), 2):
                df_insert = df_insert.rename(index={"sigtest{}".format(idx - 2): "sigtest{}".format(idx)})
                cross1 = pd.concat([cross1.iloc[:idx, ], df_insert, cross1.iloc[idx:, ]])
            for c in range(len(cross1.columns)):
                cross1.iloc[0].iloc[c] = ascii_lowercase[c]
        else:
            cross1 = pd.crosstab(df1[rowname], df1[colname], normalize='columns')
            cross1.loc['sigtest0'] = ''
            df_insert = pd.DataFrame(cross1.loc['sigtest0']).transpose()
            for idx in range(0, 2 * (len(cross1)), 2):
                df_insert = df_insert.rename(index={"sigtest{}".format(idx - 2): "sigtest{}".format(idx)})
                cross1 = pd.concat([cross1.iloc[:idx, ], df_insert, cross1.iloc[idx:, ]])
            for c in range(len(cross1.columns)):
                cross1.iloc[0].iloc[c] = ascii_lowercase[c]
        cross1 = cross1[:-1]
        countscol1 = producecolcount(colname)
        for v in range(1, len(cross1.index), 2):
            for i in range(0, len(countscol1) - 1, 1):
                for j in range(0, len(countscol1) - 1):
                    p1 = cross1.iloc[v].iloc[i]
                    p2 = cross1.iloc[v].iloc[j]
                    letter = cross1.iloc[0].iloc[j]
                    test = sigp(p1, p2, countscol1.iloc[i], countscol1.iloc[j])
                    if test == 1:
                        cross1.iloc[v + 1].iloc[i] = cross1.iloc[v + 1].iloc[i] + letter
        cross1.loc['Total'] = producecolcount(colname)
        return cross1

    def producecross(colname):
        if weightvar is not None:
            cross = pd.crosstab(df1[rowname], df1[colname], values=df[weightvar], aggfunc='sum')
            cross.loc['sigtest0'] = ''
            df_insert = pd.DataFrame(cross.loc['sigtest0']).transpose()
            for idx in range(0, 2 * (len(cross)), 2):
                df_insert = df_insert.rename(index={"sigtest{}".format(idx - 2): "sigtest{}".format(idx)})
                cross = pd.concat([cross.iloc[:idx, ], df_insert, cross.iloc[idx:, ]])
            for c in range(len(cross.columns)):
                cross.iloc[0].iloc[c] = ascii_lowercase[c]
        else:
            cross = pd.crosstab(df1[rowname], df1[colname])
            cross.loc['sigtest0'] = ''
            df_insert = pd.DataFrame(cross.loc['sigtest0']).transpose()
            for idx in range(0, 2 * (len(cross)), 2):
                df_insert = df_insert.rename(index={"sigtest{}".format(idx - 2): "sigtest{}".format(idx)})
                cross = pd.concat([cross.iloc[:idx, ], df_insert, cross.iloc[idx:, ]])
            for c in range(len(cross.columns)):
                cross.iloc[0].iloc[c] = ascii_lowercase[c]
        cross = cross.round()
        cross = cross[:-1]
        return cross

    def producecolcount(colname):
        if weightvar is not None:
            cross = pd.crosstab(df1[rowname], df1[colname], margins=True, values=df[weightvar], aggfunc='sum')
            countscol1 = cross.loc['All']
            countscol1 = countscol1[:-1]
        else:
            cross = pd.crosstab(df1[rowname], df1[colname], margins=True)
            countscol1 = cross.loc['All']
            countscol1 = countscol1[:-1]
        countscol1 = countscol1.round()
        return countscol1

    def cul(cross, countscol1):
        fun = np.empty([len(cross.index) + 1, len(countscol1.index)])
        for v in range(1, len(cross.index), 2):
            for i in range(0, len(countscol1), 1):
                pr1 = cross.iloc[v].iloc[i] / countscol1.iloc[i]
                pr2 = (cross.iloc[v, :].sum() - cross.iloc[v].iloc[i]) / (countscol1.sum() - countscol1.iloc[i])
                fun[v][i] = sigp(pr1, pr2, countscol1.iloc[i], countscol1.sum() - countscol1.iloc[i])
        trim = fun[:-1, :]
        fun1 = pd.DataFrame(trim, index=cross.index, columns=cross.columns)
        fun1[fun1 == 1] = "background-color:yellow;number-format:.0%"
        fun1 = fun1.astype(str)
        fun1[fun1 == "0.0"] = "number-format:.0%"
        for v in range(0, len(cross.index), 2):
            fun1.iloc[v] = ""
        fun1.loc['Total'] = ""
        return fun1

    df1 = df[df[rowname] != ' ']
    numbreaks = len(listofcolnames)
    my_vars = {}
    my_othercross = {}
    my_countcross = {}
    combcrosses = {}

    for i in range(0, numbreaks):
        cross1_name = "cross1%d" % i
        cross_name = "cross%d" % i
        colcount_name = "colcount%d" % i
        my_vars[cross1_name] = producecross1(listofcolnames[i])
        my_othercross[cross_name] = producecross(listofcolnames[i])
        my_countcross[colcount_name] = producecolcount(listofcolnames[i])
        combcross_name = "combcross%d" % i
        combcrosses[combcross_name] = cul(my_othercross[cross_name], my_countcross[colcount_name])

    crossfinal = pd.concat(my_vars.values(), axis=1, keys=listofcolnames)
    crossfinal = crossfinal.rename_axis(rowname)

    def comb(x):
        combdf = pd.concat(combcrosses.values(), axis=1, keys=listofcolnames)
        return combdf

    return crossfinal.style.apply(comb, axis=None)

filepath=Path(r"C:\Users\Owner\Documents\Dev\StatsTables\Flask\uploads\ExampleValueLabels.csv")
df=pd.read_csv(filepath)
print(df.head())

df1=colour(df,"B5_1_P2W5_HIGH",["PUPIL","REGION"],"W5WEIGHT1PU")

print(df1)

writer = pd.ExcelWriter("tableoutput.xlsx", engine='xlsxwriter')
df1.to_excel(writer)
writer.close()
