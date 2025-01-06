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
            # Генерация выражения
            expression = self.generate_expression(node.children[2])
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
