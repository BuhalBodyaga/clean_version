class Token:
    def __init__(self, token, lexeme, row, column):
        self.token = token
        self.lexeme = lexeme
        self.row = row
        self.column = column

    def __str__(self):
        return f'Токен: {self.token} Лексема: {self.lexeme}'


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

    def checkTokensList(self, tokenlist):
        position = self.position # переменная position вводится для того, чтобы не изменять реальную позицию пока мы не убедимся, что последовательность токенов соответствует tokenlist
        for i in tokenlist:
            if self.tokens[position].token != i:
                return False
            if position < len(self.tokens):  # если мы не в конце программы, то все ок, смещаемся дальше
                position += 1
            else:
                return False
        self.position = position  # цикл подошел к концу, теперь можно поменять реальную позицию на нашу
        return True

    def parse_program(self):
        node = Node('Program')
        while self.position < len(self.tokens):
            node.add_child(self.parse_headers())
            token = self.current_token()
            if token.token == 'K11':
                node.add_child(self.parse_namespace())
            else:
                print(token.token)
            node.add_child(self.parse_main())
        return node

    def parse_namespace(self):
        node = Node('Namespaces')
        thistokenlist = ['K11', 'K13', 'K26', 'D3']
        if self.checkTokensList(thistokenlist):
            node.add_child(Node('Namespace', 'std'))
            return node
        else:
            raise Exception('ошибка пространства имен')

    def parse_headers(self):
        token = self.current_token()
        node = Node('Headers')
        while token.token == 'P1':
            thistokenlist = ['P1', 'O21', 'ID', 'O19', 'O28']
            if self.checkTokensList(thistokenlist):
                node.add_child(Node('ID', self.tokens[self.position - 3].lexeme))
            else:
                raise Exception('ошибка объявления заголовка')
            token = self.current_token()
        return node

    def parse_main(self):
        thistokenlist = ['K17', 'K32', 'D6', 'D7', 'D4']
        if self.checkTokensList(thistokenlist):
            node = Node('MainFunction')
            node.add_child(self.parse_body())
            token = self.current_token()
            if token.token == 'D5':
                self.consume('D5')
                return node
            else:
                raise Exception('не закрыта фигурная скобка')
        else:
            raise Exception('ошибка объявления главной функции')

    def parse_body(self):
        node = Node('Body')
        node.add_child(self.parse_code_block())
        while self.position < len(self.tokens) - 1:
            node.add_child(self.parse_code_block())
        return node

    def parse_code_block(self):
        node = Node('Instruction')
        token = self.current_token()
        if token.token in ['K17', 'K18', 'K22']:
            node.add_child(self.parse_declaration())
        elif token.token == 'K24':
            node.add_child(self.parse_cout())
        elif token.token == 'K25':
            node.add_child(self.parse_cin())
        elif token.token == 'ID':
            node.add_child(self.parse_assignment())
        else:
            print('exeption', token.token, token.row, token.column, self.position)
            raise Exception('ошибка в блоке кода')
        return node

    def parse_declaration(self):
        token = self.current_token()
        if token.token in ['K17', 'K18', 'K22']:
            var_node = Node('VariableDeclaration')
            var_type = token.lexeme
            self.consume(token.token)
            var_node.add_child(Node('Type', var_type))
            var_node.add_child(self.parse_identifier())
            token = self.current_token()
            if token.token == 'O23':
                self.consume('O23')  # '='
                var_node.add_child(self.parse_expression())
            token = self.current_token()
            if token.token == 'D3':
                self.consume('D3')  # ';'
            else:
                raise Exception('пропущена точка с запятой')
            return var_node
        raise Exception('Unexpected token')

    def parse_cout(self):
        if self.tokens[self.position].token == 'K24':
            self.consume('K24')
            if self.tokens[self.position].token == 'O25':
                self.consume('O25')
                token = self.tokens[self.position]
                if token.token == 'ID' or token.token == 'N1' or token.token == 'N2' or token.token == 'N3':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cout', token.lexeme)
                        return node
        raise Exception('Ошибка вывода')

    def parse_cin(self):
        if self.tokens[self.position].token == 'K25':
            self.consume('K25')
            if self.tokens[self.position].token == 'O26':
                self.consume('O26')
                token = self.tokens[self.position]
                if token.token == 'ID':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cin', token.lexeme)
                        return node
        raise Exception('Ошибка ввода')

    def parse_identifier(self):
        token = self.current_token()
        if token.token == 'ID':
            id_node = Node('Identifier', token.lexeme)
            self.consume('ID')
            return id_node
        raise Exception('Expected identifier')

    def parse_assignment(self):
        node = Node('Assignment')
        node.add_child(self.parse_identifier())
        token = self.current_token()
        if token.token == 'O23':
            self.consume('O23')
            node.add_child(Node('AssigOperator', token.lexeme))
            token = self.current_token()
            if token.token == 'ID' or token.token == 'N1' or token.token == 'N2' or token.token == 'N3':
                self.consume(token.token)
                node.add_child(Node('Operand', token.lexeme))
                if self.tokens[self.position].token == 'D3':
                    self.consume('D3')
                    return node
                else:
                    raise Exception('ошибка выражения3')
            else:
                raise Exception('ошибка выражения2')
        else:
            raise Exception('ошибка выражения1')

    def parse_expression(self):
        token = self.current_token()
        if token.token == 'N1':
            value_node = Node('Integer', token.lexeme)
            self.consume('N1')
            return value_node
        elif token.token == 'N2':
            value_node = Node('Float', token.lexeme)
            self.consume('N2')
            return value_node
        elif token.token == 'N3':
            value_node = Node('String', token.lexeme)
            self.consume('N3')
            return value_node
        else:
            raise Exception('Expected expression')

    def print_syntax_tree(self, node, level=0):
        """ Рекурсивно выводит синтаксическое дерево. """
        if node is None:
            return
        print("\t" * level + f"{node.node_type}: {node.value if node.value is not None else ''}")
        for child in node.children:
            self.print_syntax_tree(child, level + 1)
