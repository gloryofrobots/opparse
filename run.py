import importlib
import json
from opparse import nodes
from opparse.misc import fs, timer

PARSERS = ["obin"]


def execute_parser(parser_name):
    path = "parsers.{0}.parser".format(parser_name)
    parser_module = importlib.import_module(path)
    # print dir(parser_module)
    # exit()
    parser_dir = fs.join("parsers", parser_name)
    syntax_path = fs.join(parser_dir,  "syntax." + parser_name)
    ast_path = fs.join(parser_dir, "ast.json")
    check_ast_path = fs.join(parser_dir, "check.json")

    source = fs.load_file(syntax_path)
    ast, scope = parser_module.parse(source)
    print "************************** OPERATORS **************"
    print scope.custom_operators
    print "************************** AST *********************"
    data = ast.to_json_string()
    fs.write_file(ast_path, data)

    if fs.isfile(check_ast_path):
        check_source = fs.load_file(check_ast_path)
        if data != check_source:
            print "Test %s failed" % parser_name
        else:
            print "Test %s success" % parser_name


def main(parsers):
    with timer.Timer("All parsers time") as tm_all:
        for parser_name in parsers:
            with timer.Timer("%s  parser time" % parser_name) as tm:
                execute_parser(parser_name)


if __name__ == "__main__":
    main(PARSERS)
