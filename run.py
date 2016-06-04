# Trigger emacs to run this script using the "compile" command
# ;;; Local Variables: ***
# ;;; compile-command: "run.py" ***
# ;;; end: ***
#import os
#print os.getcwd()
from opparse.parse import nodes
from opparse.misc import fs, timer
import importlib

PARSERS = ["obin"]


def execute_parser(parser_name):
    path = "parsers.{0}.{0}_parser".format(parser_name)
    parser_module = importlib.import_module(path)
    # print dir(parser_module)
    # exit()
    parser_dir = fs.join("parsers", parser_name)
    syntax_path = fs.join(parser_dir, parser_name + ".syntax")
    ast_path = fs.join(parser_dir, parser_name + ".json")

    source = fs.load_file(syntax_path)
    ast, scope = parser_module.parse(source)
    print "************************** OPERATORS **************"
    print scope.operators
    print "************************** AST *********************"
    data = nodes.node_to_string(ast)
    fs.write_file(ast_path, data)


def execute_parsers(parsers):
    with timer.Timer("All parsers time") as tm_all:
        for parser_name in parsers:
            with timer.Timer("%s  parser time" % parser_name) as tm:
                execute_parser(parser_name)

execute_parsers(PARSERS)
