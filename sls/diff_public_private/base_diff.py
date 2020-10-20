
# -*- coding:utf-8 -*-

import json
import os
from optparse import OptionParser

from base import execute_activity
from command_executor import exec_cmd
from logging_helper import get_logger


def get_options():
    parser = OptionParser()
    (options, args) = parser.parse_args()
    return options


def _to_debug(debug_flag,func,mode="order",*args,**kwargs):
    if mode == "order" :
        if debug_flag == "True":
            func(*args,**kwargs)
    elif mode == "reverse" :
        if debug_flag != "True":
            func(*args,**kwargs)
    else:
        pass



def subtraction_list(first, second):
    second = set(second)
    return [item for item in first if item not in second]


def get_file_dir_list(ane_dir):
    a_dir_file_list = []
    a_dir_dir_list = []
    a_dir_list = os.listdir(ane_dir)
    for i in a_dir_list:
        j = os.path.join(ane_dir, i)
        if os.path.isfile(j):
            a_dir_file_list.append(i)
        elif os.path.isdir(j):
            a_dir_dir_list.append(i)
    return a_dir_dir_list, a_dir_file_list


def add_list_into_total(a_list, total_list, absolute_path):
    if a_list:
        for i in a_list:
            total_list.append(os.path.join(absolute_path, i))


def diff_catalogue(a_dir, b_dir):
    unilateral_dirs = []
    unilateral_files = []
    common_file_list = []
    def _inner_diff_catalogue(a_dir, b_dir):

        a_dir_dir_list, a_dir_file_list = get_file_dir_list(a_dir)
        b_dir_dir_list, b_dir_file_list = get_file_dir_list(b_dir)

        a_b_dir_list = subtraction_list(a_dir_dir_list, b_dir_dir_list)
        a_b_file_list = subtraction_list(a_dir_file_list, b_dir_file_list)
        b_a_dir_list = subtraction_list(b_dir_dir_list, a_dir_dir_list)
        b_a_file_list = subtraction_list(b_dir_file_list, a_dir_file_list)

        add_list_into_total(a_b_file_list, unilateral_files, a_dir)
        add_list_into_total(b_a_file_list, unilateral_files, b_dir)
        add_list_into_total(a_b_dir_list, unilateral_dirs, a_dir)
        add_list_into_total(b_a_dir_list, unilateral_dirs, b_dir)

        inner_common_dir_list = subtraction_list(
            list(set((a_dir_dir_list + b_dir_dir_list))), (a_b_dir_list + b_a_dir_list))
        inner_common_file_list = subtraction_list(
            list(set((a_dir_file_list + b_dir_file_list))), (a_b_file_list + b_a_file_list))

        for i in inner_common_file_list:
            new_a_file = os.path.join(a_dir, i)
            new_b_file = os.path.join(b_dir, i)
            common_file_list.append([new_a_file, new_b_file])

        for i in inner_common_dir_list:
            new_a_dir = os.path.join(a_dir, i)
            new_b_dir = os.path.join(b_dir, i)
            _inner_diff_catalogue(new_a_dir, new_b_dir)

    _inner_diff_catalogue(a_dir, b_dir)
    _unilateral_dirs = [i[(i.index("/") + 1):] for i in unilateral_dirs]
    _unilateral_files = [i[(i.index("/") + 1):] for i in unilateral_files]

    # _unilateral_files = [[i[0][(i[0].index("/") + 1):], i[1][(i[1].index("/") + 1):]] for i in unilateral_files]
    return _unilateral_dirs, _unilateral_files, common_file_list


def diff_content(common_file_list):
    sums_same_filename = []

    def _inner_diff_content(common_file_list):
        for i in common_file_list:
            assert i[0] and i[1], "this is error,dont exist the same file_name"
            diff_cmd = "diff -Bbu %s %s" % (str(i[0]), str(i[1]))
            _, stdout, _ = exec_cmd(diff_cmd, throw=False)
            if stdout:
                sums_same_filename.append(i)
    _inner_diff_content(common_file_list)
    return sums_same_filename


def write_dict_into_file(dict_name, file_name):
    with open(file_name, "w+") as f:
        for i in dict_name:
            f.write(str(i)+'\n')

def save_diff(sums_same_filename, service_path, save_path):
    save_path_src = os.path.join(save_path, "src")
    if not os.path.exists(save_path_src):
        exec_cmd("mkdir -p %s" % save_path_src)
    save_path_src = save_path_src + '/'
    for i in [os.path.join(service_path, i) for i in["unilateral_dirs", "unilateral_files", "common_file_list", "sums_same_filename"]]:
        exec_cmd("mv %s %s" % (i, save_path_src))
    diff_contents_same_filename = save_path_src + "diff_contents_same_filename"
    if not os.path.exists(diff_contents_same_filename):
        exec_cmd("mkdir %s" % diff_contents_same_filename)
    for i in sums_same_filename:
        assert i[0] and i[1], "this is error,dont exist the same file_name"
        diff_cmd = "diff -Bbu %s %s" % (str(i[0]), str(i[1]))
        _, stdout, _ = exec_cmd(diff_cmd, throw=False)
        if stdout:
            # file_name = i[0].replace(service_path, "")
            file_name = i[0][(i[0].index("/") + 1):]
            file_name = file_name[(file_name.index("/") + 1):]
            file_name = file_name.replace("/", "-")
            file_name = diff_contents_same_filename + "/" + file_name
            with open(file_name, "w+") as f:
                f.write(str(stdout)+'\n')


def diff_new_and_already(new_path, already_path):
    for i in ["unilateral_dirs",
              "unilateral_files",
              "sums_same_filename",
              "diff_contents_same_filename",
              "common_file_list"]:
        new_path_src = os.path.join(new_path, "src")
        new_path_fixed = os.path.join(new_path, "fixed")
        if not os.path.exists(new_path_fixed):
            exec_cmd("mkdir %s" % new_path_fixed)

        def write_file(new_path_src, already_path, file_name, new_path_fixed):
            diff_cmd = "diff -BbT -w -W 300 --ignore-matching-lines='---' --ignore-matching-lines='+++' -y --suppress-common-lines %s %s" % (
                os.path.join(new_path_src, i), os.path.join(already_path, file_name))
            # diff_cmd = "diff -Bbu --ignore-matching-lines='---' --ignore-matching-lines='+++' %s %s" % (os.path.join(new_path_src,i),os.path.join(already_path,file_name))
            _, stdout, _ = exec_cmd(diff_cmd, throw=False)
            fixed_file_name = os.path.join(new_path_fixed, file_name)
            if stdout:
                with open(fixed_file_name, "w") as f:
                    f.write(str(stdout)+'\n')

        if i == "diff_contents_same_filename":
            new_path_src_file_content = os.path.join(
                new_path_src, "diff_contents_same_filename")
            already_path_file_content = os.path.join(
                already_path, "diff_contents_same_filename")
            new_path_fixed_file_content = os.path.join(
                new_path_fixed, "diff_contents_same_filename")
            if not os.path.exists(new_path_fixed_file_content):
                exec_cmd("mkdir %s" % new_path_fixed_file_content)
            _, new_path_src_file_content_list = get_file_dir_list(
                new_path_src_file_content)
            if not os.path.exists(already_path_file_content):
                print "ERROR, there is no %s" % already_path_file_content
                continue
            _, already_path_file_content_list = get_file_dir_list(
                already_path_file_content)
            content_common_file_list = subtraction_list(
                new_path_src_file_content_list, already_path_file_content_list)
            content_common_file_list = subtraction_list(
                new_path_src_file_content_list, content_common_file_list)
            for i in content_common_file_list:
                write_file(new_path_src_file_content,
                           already_path_file_content, i, new_path_fixed_file_content)
        else:
            write_file(new_path_src, already_path, i, new_path_fixed)
