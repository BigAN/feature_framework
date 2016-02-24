#!/usr/env/bin python
# coding=utf8
"""
copy from https://github.com/benhamner/Metrics/blob/master/Python/ml_metrics/auc.py
"""


def tied_rank(x):
    """
    Computes the tied rank of elements in x.

    This function computes the tied rank of elements in x.

    Parameters
    ----------
    x : list of numbers, numpy array

    Returns
    -------
    score : list of numbers
            The tied rank f each element in x

    """
    sorted_x = sorted(zip(x, range(len(x))))
    r = [0 for k in x]
    cur_val = sorted_x[0][0]
    last_rank = 0
    for i in range(len(sorted_x)):
        if cur_val != sorted_x[i][0]:
            cur_val = sorted_x[i][0]
            for j in range(last_rank, i):
                r[sorted_x[j][1]] = float(last_rank + 1 + i) / 2.0
            last_rank = i
        if i == len(sorted_x) - 1:
            for j in range(last_rank, i + 1):
                r[sorted_x[j][1]] = float(last_rank + i + 2) / 2.0
    return r


def auc(actual, posterior):
    """
    Computes the area under the receiver-operater characteristic (AUC)

    This function computes the AUC error metric for binary classification.

    Parameters
    ----------
    actual : list of binary numbers, numpy array
             The ground truth value
    posterior : same type as actual
                Defines a ranking on the binary numbers, from most likely to
                be positive to least likely to be positive.

    Returns
    -------
    score : double
            The mean squared error between actual and posterior

    """
    r = tied_rank(posterior)
    num_positive = len([0 for x in actual if x == 1])
    num_negative = len(actual) - num_positive
    sum_positive = sum([r[i] for i in range(len(r)) if actual[i] == 1])
    auc = ((sum_positive - num_positive * (num_positive + 1) / 2.0) /
           (num_negative * num_positive))
    return auc


def auc_liblinear_predict(predict_file):
    """
    计算由liblinear predict得到的输出对应的AUC值
    修改predict.c的140行：
    fprintf(output,"%g",target_label);   // 增加真实label的结果
    fprintf(output," %g",predict_label);
    从新make之后运行

    其格式例如：
    ********************
    labels 1 -1
    1 -1 0.162033 0.837967
    -1 -1 0.006508 0.993492
    ...
    ********************
    第一行是列说明
    """
    with open(predict_file) as f:
        lines = f.readlines()
    actual = []
    posterior = []
    for one in lines[1:]:
        ss = one.split()
        actual.append(1 if ss[0] == '1' else 0)
        posterior.append(float(ss[2]))
    return auc(actual, posterior)


if __name__ == '__main__':
    import sys
    predict_file = sys.argv[1]
    print auc_liblinear_predict(predict_file)