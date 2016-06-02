from opparse.parse import parser, nodes
from opparse.misc import fs, timer

PARSERS = ["obin"]

def execute_parser(parser_name):
    parser_dir = fs.join("parsers", parser_name)
    syntax_path = fs.join(parser_dir, parser_name + ".syntax")
    ast_path = fs.join(parser_dir, parser_name + ".json")

    source = fs.load_file(syntax_path)
    ast, scope = parser.parse(source)
    print "************************** OPERATORS ****************************************"
    print scope.operators
    print "************************** AST ****************************************"
    data = nodes.node_to_string(ast)
    fs.write_file(ast_path, data)


def execute_parsers(parsers):
    with timer.Timer("All parsers time") as tm_all:
        for parser_name in parsers:
            with timer.Timer("%s  parser time" % parser_name) as tm:
                execute_parser(parser_name)

execute_parsers(PARSERS)
