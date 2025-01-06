from lex_analizer import Buffer, LexicalAnalyzer
from typing import List
from syntax_analaizer import Parser, Token


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

    # generator = CodeGenerator()
    # generator.generate(program_node)      
    # java_code = generator.get_code()       
    # print(java_code)      
