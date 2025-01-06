from lex_analizer import Buffer, LexicalAnalyzer
from typing import List
from syntax_analaizer import Parser, Token, Node
from generator import CodeGenerator


def preproc(pretokens):
    tokens: List[Token] = []
    for i in range(len(pretokens)):
        if pretokens[i].token != 'D10':
            # надо еще подумать над тем как убирать переносы строки, так как
            # где-то они должны быть обязательно. с пробелами такой проблемы
            # нет, потому что если лексемы распознались правильно, значит
            # пробелы были там где надо
            if not (pretokens[i].token == 'O28' and pretokens[i - 1].token != 'O19'):
                tokens.append(pretokens[i])
    return tokens


def find_node(root, type):
    found_nodes = []  # Список для хранения найденных узлов

    # Проверяем, совпадает ли значение текущего узла с искомым
    if root.node_type == type:
        found_nodes.append(root)

    # Рекурсивно ищем в дочерних узлах
    for child in root.children:
        found_nodes.extend(find_node(child, type))  # Объединяем результаты

    # Возвращаем список найденных узлов
    return found_nodes


def find_node2(root, value):
    # Проверяем, совпадает ли значение текущего узла с искомым
    if root.value == value:
        return root

    # Рекурсивно ищем в дочерних узлах
    for child in root.children:
        result = find_node2(child, value)
        if result is not None:
            return result

    # Если узел не найден, возвращаем None
    return None


def preproc_cin(program_node):
    finds = find_node(program_node, 'Cin')
    # print(finds)
    if finds:
        for find in finds:
            # print(find.node_type)
            id = find.children[0].value
            node = find.parent.parent
            find2 = find_node2(node, id)
            if find2:
                # print(find2.node_type)
                type = find2.parent.children[0].value
                find.add_child(Node('Type', type))
            else:
                raise Exception('ошибка2')
    else:
        raise Exception('ошибка1')


if __name__ == '__main__':
    buffer = Buffer()
    Analyzer = LexicalAnalyzer()

    fullTokens: List[Token] = []

    token = []
    lexeme = []
    row = []
    column = []

    print(buffer.load_buffer())
    for i in buffer.load_buffer():
        t, lex, lin, col = Analyzer.tokenize(i)
        token += t
        lexeme += lex
        row += lin
        column += col

    for i in range(len(token)):
        fullToken = Token(token[i], lexeme[i], row[i], column[i])
        fullTokens.append(fullToken)

    tokens = preproc(fullTokens)

    for i in range(len(tokens)):
        print(tokens[i])

    parser = Parser(tokens)
    program_node = parser.parse_program()  # Получаем дерево
    parser.print_syntax_tree(program_node)

    preproc_cin(program_node)

    parser.print_syntax_tree(program_node)

    generator = CodeGenerator()
    generator.generate(program_node)
    java_code = generator.get_code()
    print(java_code)
