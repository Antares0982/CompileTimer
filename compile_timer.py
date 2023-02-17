#!/usr/bin/env python3

import multiprocessing
import os
import shutil
import subprocess
import sys
import time


def getConcurrency():
    return multiprocessing.cpu_count()


class BuildFolder(object):
    def __enter__(self):
        if not os.path.exists("build"):
            os.mkdir("build")
        elif os.listdir("build"):
            print("./build is not empty, please empty it first")
            exit(1)
        os.chdir("build")
        return self

    def __exit__(self, type, value, traceback):
        os.chdir("..")
        shutil.rmtree("build")


def run():
    """
    The script is to time a compile target in cmake by
    calling "cmake --build . --target <target> -j <max_concurrency>"
    where target is defined in sys.argv[2]
    cmake project folder is sys.argv[1]
    also, a config file is supported, which is sys.argv[3]
    """

    if len(sys.argv) < 3:
        print("Usage: python3 compile_timer.py <cmake_project_folder> <target>")
        print(sys.argv[1])
        return 1

    # first generate cmake project folder in workdir/build
    folder = sys.argv[1]
    target = sys.argv[2]
    config = None
    if len(sys.argv) >= 4:
        config = sys.argv[3]
        if not os.path.exists(config):
            print("config file {} does not exist".format(config))
            return 1

    cmake_args = []
    build_args = []
    if config is not None:
        # read config file using ConfigParser
        import configparser
        config = configparser.ConfigParser()
        config.read(sys.argv[3])
        # read cmake arguments and build arguments
        cmake_args = config["settings"]["cmake"].split()
        build_args = config["settings"]["build"].split()

    with BuildFolder():
        # call cmake in ./build, target folder is folder
        commands = ["cmake", folder]+cmake_args
        print(' '.join(commands))
        ret = subprocess.call(
            commands, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ret != 0:
            print("cmake failed")
            return ret

        # get the start time
        start = time.time()

        commands = ["cmake", "--build", ".", "--target",
                    target, "-j", str(getConcurrency())]+build_args
        print(' '.join(commands))
        ret = subprocess.call(
            commands, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ret != 0:
            print("cmake build failed")
            return ret

        # get the end time
        end = time.time()

        # print the time
        print("Time elapsed: {} seconds".format(end - start))


if __name__ == "__main__":
    run()
