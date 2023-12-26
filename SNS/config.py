# -*- coding: utf-8 -*-
import argparse

parser = argparse.ArgumentParser(description='Configuration file')
arg_lists = []


def add_argument_group(name):
    arg = parser.add_argument_group(name)
    arg_lists.append(arg)
    return arg

# artistic Data
# data_arg = add_argument_group('Data')
# data_arg.add_argument('--point_num', type=int, default=20, help='point num')
# data_arg.add_argument('--zone_num', type=int, default=4, help='zone num')
# data_arg.add_argument('--individual_num', type=int, default=14, help='individual num')
# data_arg.add_argument('--iter_num', type=int, default=35, help='generation num')
# data_arg.add_argument('--mutate_prob', type=float, default=0.35, help='probability of mutate')


# realData
data_arg = add_argument_group('Data')
data_arg.add_argument('--point_num', type=int, default=338, help='point num')
data_arg.add_argument('--zone_num', type=int, default=8, help='zone num')
data_arg.add_argument('--individual_num', type=int, default=50, help='individual num')
data_arg.add_argument('--iter_num', type=int, default=30, help='generation num')
data_arg.add_argument('--mutate_prob', type=float, default=0.45, help='probability of mutate')


def get_config():
    config, unparsed = parser.parse_known_args()
    return config

