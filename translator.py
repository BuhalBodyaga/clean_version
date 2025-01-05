import re
from typing import List


class Token:
    def __init__(self, token, lexeme, row, column):
        self.token = token
        self.lexeme = lexeme
        self.row = row
        self.column = column

    def __str__(self):
        return f'Токен: {self.token} Лексема: {self.lexeme}'


class LexicalAnalyzer:
    # Token row
    lin_num = 1

    def tokenize(self, code):
        rules = [
            ('P1', r'#include'),
            ('P2', r'#define'),
            ('K1', r'break'),
            ('K2', r'const'),
            ('K3', r'continue'),
            ('K4', r'while'),
            ('K5', r'do'),
            ('K6', r'if'),
            ('K7', r'else'),
            ('K8', r'for'),
            ('K9', r'class'),
            ('K10', r'this'),
            ('K11', r'using'),
            ('K12', r'return'),
            ('K13', r'namespace'),
            ('K14', r'this'),
            ('K15', r'bool'),
            ('k16', r'char'),
            ('K17', r'int'),
            ('K18', r'float'),
            ('K19', r'double'),
            ('K20', r'void'),
            ('K21', r'true'),
            ('K22', r'string'),
            ('K23', r'false'),
            ('K24', r'cout'),
            ('K25', r'cin'),
            ('K26', r'std'),
            ('K27', r'new'),
            ('K28', r'null'),
            ('K29', r'private'),
            ('K30', r'protected'),
            ('K31', r'public'),
            ('K32', r'main'),
            # ('Q1', r'\''),            # '
            # ('Q2', r'\"'),            # "
            ('D1', r'\.'),            # .
            ('D2', r','),
            ('D3', r';'),
            ('D4', r'\{'),            # {
            ('D5', r'\}'),            # }
            ('D6', r'\('),            # (
            ('D7', r'\)'),            # )
            ('D8', r'\['),            # [
            ('D9', r'\]'),            # ]
            ('D10', r'[ \t]+'),       # SPACE and TABS

            ('O2', r'\+\+'),          # ++
            ('O3', r'\+='),           # +=
            ('O1', r'\+'),            # +
            ('O4', r'-'),
            ('O5', r'--'),
            ('O6', r'-='),
            ('O8', r'\*='),           # *=
            ('O7', r'\*'),            # *
            ('O10', r'\/='),          # /=
            ('O9', r'\/'),            # /
            ('O12', r'\%='),          # %=
            ('O11', r'\%'),           # %
            ('O14', r'\|\|'),         # ||
            ('O13', r'\|'),           # |
            ('O16', r'&&'),
            ('O15', r'&'),
            ('O17', r'!'),
            ('O18', r'!='),
            ('O26', r'>>'),
            ('O20', r'>='),
            ('O25', r'<<'),
            ('O22', r'<='),
            ('O24', r'=='),
            ('O21', r'<'),
            ('O19', r'>'),
            ('O23', r'\='),            # =
            ('O27', r'::'),
            ('O28', r'\n'),               # NEW LINE
            ('O29', r':'),
            ('N3', r'\"\w*\"'),           # String
            ('N4', r'\'\w\''),           # char
            ('ID', r'[a-zA-Z]\w*'),       # IDENTIFIERS
            ('N2', r'\d(\d)*\.\d(\d)*'),  # FLOAT
            ('N1', r'\d(\d)*'),           # INT
            ('NONAME', r'.'),            # noname


        ]

        tokens_join = '|'.join('(?P<%s>%s)' % x for x in rules)
        lin_start = 0

        # Lists of output for the program
        token = []
        lexeme = []
        row = []
        column = []

        # It analyzes the code to find the lexemes and their respective Tokens
        for m in re.finditer(tokens_join, code):
            token_type = m.lastgroup
            token_lexeme = m.group(token_type)

            if token_type == 'NEWLINE':
                lin_start = m.end()
                self.lin_num += 1
            elif token_type == 'SKIP':
                continue
            elif token_type == 'MISMATCH':
                raise RuntimeError('%r unexpected on \
line %d' % (token_lexeme, self.lin_num))
            else:
                col = m.start() - lin_start
                column.append(col)
                token.append(token_type)
                lexeme.append(token_lexeme)
                row.append(self.lin_num)
                # To print information about a Token
#                 print('Token = {0}, Lexeme = \'{1}\', Row = {2}, \
# Column = {3}'.format(token_type, token_lexeme, self.lin_num, col))
        return token, lexeme, row, column


class Buffer:
    def load_buffer(self):
        arq = open('program.cpp', 'r')
        text = arq.readline()

        buffer = []
        cont = 1

        # The buffer size can be changed by changing cont
        while text != "":
            buffer.append(text)
            text = arq.readline()
            cont += 1

            if cont == 10 or text == '':
                # Return a full buffer
                buf = ''.join(buffer)
                cont = 1
                yield buf

                # Reset the buffer
                buffer = []

        arq.close()


class Node:
    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None
    
    def consume(self, expected_type):
        if self.position < len(self.tokens) and self.tokens[self.position].token == expected_type:
            self.position += 1
        else:
            raise Exception(f'Expected token type {expected_type}')

    def parse_program(self):
        node = Node('Program')
        while self.position < len(self.tokens):
            node.add_child(self.parse_declaration())
        return node

    def parse_declaration(self):
        token = self.current_token()
        if token.token in ['K17', 'K18', 'K22']:  # Включите другие типы по мере необходимости
            var_node = Node('VariableDeclaration')
            var_type = token.lexeme
            self.consume(token.token)
            var_node.add_child(Node('Type', var_type))
            var_node.add_child(self.parse_identifier())
            self.consume('O23')  # '='
            var_node.add_child(self.parse_expression())
            self.consume('D3')  # ';'
            return var_node
        raise Exception('Unexpected token')

    def parse_identifier(self):
        token = self.current_token()
        if token.token == 'ID':
            id_node = Node('Identifier', token.lexeme)
            self.consume('ID')
            return id_node
        raise Exception('Expected identifier')
    
    def parse_expression(self):
        # Здесь вы можете реализовать допустимые выражения
        token = self.current_token()
        if token.token == 'N1':
            value_node = Node('Integer', token.lexeme)
            self.consume('N1')
            return value_node
        raise Exception('Expected expression')
    

class CodeGenerator:
    def __init__(self):
        self.code = []

    def generate(self, node):
        if node.node_type == 'Program':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'VariableDeclaration':
            var_type = node.children[0].value  # Тип переменной
            identifier = node.children[1].value  # Имя переменной
            expression = self.generate_expression(node.children[2])  # Генерация выражения
            self.code.append(f"{var_type} {identifier} = {expression};")
        elif node.node_type == 'Identifier':
            return node.value
        elif node.node_type == 'Integer':
            return node.value
        else:
            raise Exception(f'Unknown node type: {node.node_type}')

    def generate_expression(self, node):
        if node.node_type == 'Integer':
            return node.value
        # Здесь следует обработать другие типы выражений, если они будут
        return ''

    def get_code(self):
        return "\n".join(self.code)


# class Syntax_Analyzer:
#     debug = True

#     def __init__(self, tokens):
#         self.tokens = tokens

#     def show(self, indent, name, spp):
#         if self.debug:
#             print(indent + name + '("', end=' ')
#             j = len(self.tokens)
#             for i in range(spp, j):
#                 print(self.tokens[i], sep="", end=" ")
#             print('")', end='\n')
#             return
#         else:
#             return

#     def checkTokensList(self, spp, tokenlist):
#         for i in tokenlist:
#             if self.tokens[spp] != i:
#                 return False, spp
#             if spp < len(self.tokens):
#                 spp += 1
#             else:
#                 return False, spp
#         return True, spp

#     def prog(self, spp, indent):
#         self.show(indent, 'prog', spp)
#         indent = indent+' '
#         thistokenlist = ['P1', 'O21', 'ID', 'O19', 'O28']
#         res, spp = self.checkTokensList(spp, thistokenlist)
#         if res:
#             return self.mainFunc(spp, indent)
#         return False, spp

#     def mainFunc(self, spp, indent):
#         self.show(indent, 'main', spp)
#         indent = indent+' '
#         # spp1 = spp
#         thistokenlist = ['K17', 'K32', 'D6', 'D7', 'D4']
#         res, spp = self.checkTokensList(spp, thistokenlist)
#         if res:
#             res, spp = self.body(spp, indent)
#             return (tokens[spp] == 'D5'), spp
#         return False, spp

#     def body(self, spp, indent):
#         self.show(indent, 'body', spp)
#         indent = indent+' '
#         spp1 = spp
#         res, spp = self.codeBlock(spp, indent)
#         if res:
#             while tokens[spp] != 'D5' and res:
#                 res, spp = self.codeBlock(spp, indent)
#             return res, spp
#         return False, spp1

#     def codeBlock(self, spp, indent):
#         # show(indent, 'codeBlock', spp)
#         indent = indent+' '
#         spp1 = spp
#         res, spp = self.var(spp, indent)
#         if res:
#             return res, spp
#         res, spp = self.outBlock(spp, indent)
#         if res:
#             return res, spp
#         return False, spp1

#     def outBlock(self, spp, indent):
#         indent = indent+' '
#         spp1 = spp
#         if self.tokens[spp] == 'K24':
#             if spp < len(self.tokens):
#                 spp += 1
#             if self.tokens[spp] == 'O25':
#                 if spp < len(self.tokens):
#                     spp += 1
#                 if self.tokens[spp] == 'ID' or self.tokens[spp] == 'N1' or self.tokens[spp] == 'N2' or self.tokens[spp] == 'N3':
#                     if spp < len(self.tokens):
#                         spp += 1
#                     if self.tokens[spp] == 'D3':
#                         self.show(indent, 'outBlock', spp1)
#                         return True, spp+1
#         return False, spp1

#     def var(self, spp, indent):

#         indent = indent+' '
#         spp1 = spp
#         if self.tokens[spp] == 'K17' or self.tokens[spp] == 'K18' or self.tokens[spp] == 'K22':
#             if spp < len(self.tokens):
#                 spp += 1
#             if self.tokens[spp] == 'ID':
#                 if spp < len(self.tokens):
#                     spp += 1
#                 if self.tokens[spp] == 'D3':
#                     self.show(indent, 'var', spp1)
#                     return True, spp+1
#                 elif self.tokens[spp] == 'O23':
#                     if spp < len(self.tokens):
#                         spp += 1
#                     if self.tokens[spp] == 'N1' or self.tokens[spp] == 'N2' or self.tokens[spp] == 'N3':
#                         if spp < len(self.tokens):
#                             spp += 1
#                         if self.tokens[spp] == 'D3':
#                             self.show(indent, 'var', spp1)
#                             return True, spp+1
#         return False, spp1


def preproc(pretokens):
    # tokens = []
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

    # syn_an = Syntax_Analyzer(tokens)

    # print(syn_an.prog(0, ''))

    parser = Parser(tokens)
    program_node = parser.parse_program()  # Получаем дерево
    # generator = CodeGenerator()
    # generator.generate(program_node)      
    # java_code = generator.get_code()       
    # print(java_code)      
