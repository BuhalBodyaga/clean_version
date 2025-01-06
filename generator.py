class CodeGenerator:
    def __init__(self):
        self.code = []

    def generate(self, node):
        if node.node_type == 'Program':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'Headers':
            pass
        elif node.node_type == 'Namespaces':
            pass
        elif node.node_type == 'MainFunction':
            self.code.append("public class Main {")
            self.code.append("public static void main(String[] args) {")
            for child in node.children:
                self.generate(child)
            self.code.append("}")
            self.code.append("}")
        elif node.node_type == 'Body':
            for child in node.children:
                self.generate(child)
            if 'Scanner scanner = new Scanner(System.in);' in self.code:
                self.code.append('scanner.close();')
        elif node.node_type == 'Instruction':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'VariableDeclaration':
            var_type = node.children[0].value  # Тип переменной
            identifier = node.children[1].value  # Имя переменной
            # Генерация выражения
            if len(node.children) > 2:
                self.code.append(f'{var_type} {identifier} = {node.children[2].value};')
            else:
                self.code.append(f'{var_type} {identifier};')
        elif node.node_type == 'Cout':
            self.code.append(f'System.out.println({node.value});')
        elif node.node_type == 'Cin':
            type = node.children[1].value
            if 'import java.util.Scanner;' not in self.code:
                self.code.insert(0, 'import java.util.Scanner;')
            if 'Scanner scanner = new Scanner(System.in);' not in self.code:
                self.code.append('Scanner scanner = new Scanner(System.in);')
            if type == 'string':
                type = 'Line'
            elif type == 'int':
                type = 'Int'
            elif type == 'bool':
                type = 'Boolean'
            elif type == 'float':
                type = 'Double'
            else:
                print('ошибка типа данных при вводе')
            self.code.append(f'{node.children[0].value} = scanner.next{type}();')

        elif node.node_type == 'Identifier':
            return node.value
        elif node.node_type == 'Integer':
            return node.value
        else:
            raise Exception(f'Unknown node type: {node.node_type}')

    def get_code(self):
        return "\n".join(self.code)
