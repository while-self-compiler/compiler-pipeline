import re
from typing import Dict, Optional, List, Tuple
from minimal_compiler.src.optimiser.base_optimiser import BaseOptimiser
from minimal_compiler.src.optimiser.ir_classes import *
import copy
from minimal_compiler.src.optimiser.ast import build_ast, unflatten_ast, print_ast_structure

class StructuralTreePatternMatchingOptimiser(BaseOptimiser):
    # Note: Global zero constant check is not necessary for this optimiser, as the minimal compiler does not use a global zero constant (as the transpiler does).
    
    PATTERNS = [ # (pattern, replacement ast (post condition / invariant)) (Order matters!)

        # Div
        (
            """
                x4 = x1 + 0;
                x5 = x2 + 0;
                x6 = x3 + 0;
                x7 = x1 + 0; 
                while x7 > 0 do
                    x6 = x6 + 1;
                    x7 = x3 + 0
                end;
                x0 = x3 + 0;
                while x5 > 0 do
                    x4 = x4 - 1;
                    x5 = x5 - 1
                end;
                while x6 > 0 do
                    x4 = x4 + 1;
                    while x4 > 0 do
                        x5 = x2 + 0;
                        while x5 > 0 do
                            x4 = x4 - 1;
                            x5 = x5 - 1
                        end;
                        x0 = x0 + 1
                    end;
                    x6 = x3 + 0
                end
            """,
            SequenceNode([
                AssignmentNodeTwoVar("x0", "x1", "/", "x2", 1, 1),
                SequenceNode([
                    AssignmentNodeTwoVar("x4", "x4", "-", "x4", 1, 1),
                    SequenceNode([
                        AssignmentNodeTwoVar("x5", "x5", "-", "x5", 1, 1),
                        SequenceNode([
                            AssignmentNodeTwoVar("x6", "x6", "-", "x6", 1, 1),
                            AssignmentNodeTwoVar("x7", "x7", "-", "x7", 1, 1),
                        ])
                    ])
                ])
            ])
        ),

        # Modulo
        (
            """
                x0 = x1 + 0;
                x3 = x0 + 1;
                x4 = x2 + 0;
                while x4 > 0 do
                    x3 = x3 - 1;
                    x4 = x4 - 1
                end;
                while x3 > 0 do
                    x4 = x2 + 0;
                    while x4 > 0 do
                        x0 = x0 - 1;
                        x4 = x4 - 1
                    end;
                    x3 = x0 + 1;
                    x4 = x2 + 0;
                    while x4 > 0 do
                        x3 = x3 - 1;
                        x4 = x4 - 1
                    end
                end
            """,
            SequenceNode([
                AssignmentNodeTwoVar("x0", "x1", "%", "x2", 1, 1),
                SequenceNode([
                    AssignmentNodeTwoVar("x3", "x3", "-", "x3", 1, 1), # x3 is 0 because of x3 > 0 in second loop (it can be inferred that x3 is 0)
                    AssignmentNodeTwoVar("x4", "x4", "-", "x4", 1, 1)
                ])
            ])
        ),

        # Bitshift Left
        (
            """
                x9 = x9 + 1; 
                x0 = x1 + 0;   
                x3 = x2 + 0; 
                x4 = x9 + 0; 
                while x3 > 0 do
                    x6 = x4 + 0; 
                    while x6 > 0 do
                        x6 = x6 - 1;
                        x4 = x4 + 1
                    end;
                    x3 = x3 - 1
                end;
                x5 = x4 + 0;
                x10 = x7 + 0; 
                while x5 > 0 do
                    x8 = x1 + 0; 
                    while x8 > 0 do
                        x10 = x10 + 1;
                        x8 = x8 - 1
                    end;
                    x5 = x5 - 1
                end;
                x4 = x5 + 0;
                x0 = x10 + 0
            """,
            SequenceNode([
                AssignmentNodeTwoVar("x0", "x1", "<<", "x2", 1, 1),
                SequenceNode([
                    AssignmentNodeTwoVar("x3", "x3", "-", "x3", 1, 1),
                    SequenceNode([
                        AssignmentNodeTwoVar("x5", "x5", "-", "x5", 1, 1),
                        SequenceNode([
                            AssignmentNode("x10", "x0", "+", 0),
                            SequenceNode([
                                AssignmentNodeTwoVar("x6", "x6", "-", "x6", 1, 1), # because x6 is 0 we can use it as a temp variable to hold 1
                                SequenceNode([
                                    AssignmentNodeTwoVar("x8", "x8", "-", "x8", 1, 1),
                                    SequenceNode([
                                        AssignmentNode("x9", "x9", "+", 1),
                                        AssignmentNode("x4", "x5", "+", 0)
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ),
        

        # Bitshift Right
        (
            """
                x1 = x2 + 0; 
                x3 = x4 + 0;  
                while x1 > 0 do
                    x5 = x6 + 0;
                    x7 = x3 + 0;
                    x8 = x7 - 1;
                    while x8 > 0 do
                        x7 = x7 - 2;
                        x5 = x5 + 1;
                        x8 = x7 - 1
                    end;
                    x3 = x5 + 0;
                    x1 = x1 - 1
                end;
                x9 = x3 + 0
            """,
            SequenceNode([
                AssignmentNodeTwoVar("x9", "x4", ">>", "x2", 1, 1),
                SequenceNode([
                    AssignmentNodeTwoVar("x1", "x1", "-", "x1", 1, 1),
                    SequenceNode([
                        AssignmentNode("x3", "x9", "+", 0),
                        SequenceNode([
                            AssignmentNode("x5", "x3", "+", 0), 
                            SequenceNode([
                                AssignmentNodeTwoVar("x9", "x9", "-", "x9", 1, 1), # because x3 is same as x9 we can use x9 as a temp variable to hold 2 for the modulo operation
                                SequenceNode([
                                    AssignmentNode("x9", "x9", "+", 2),
                                    SequenceNode([
                                        AssignmentNodeTwoVar("x7", "x3", "%", "x9", 1, 1),
                                        SequenceNode([
                                            AssignmentNode("x9", "x3", "+", 0), # reset x9 to closed form solution
                                            AssignmentNodeTwoVar("x8", "x8", "-", "x8", 1, 1)
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ),

        # Mul
        (
            """
                x4 = x1 + 0; 
                x5 = x2 + 0; 
                x6 = x5 + 0;
                x0 = x3 + 0; 
                while x4 > 0 Do
                    x4 = x4 - 1;
                    while x5 > 0 Do
                        x5 = x5 - 1;
                        x0 = x0 + 1
                    end;
                    x5 = x6 + 0
                end
            """,
            SequenceNode([
                AssignmentNodeTwoVar("x0", "x1", "*", "x2", 1, 1),
                SequenceNode([
                    AssignmentNodeTwoVar("x4", "x4", "-", "x4", 1, 1),
                    SequenceNode([
                        AssignmentNode("x6", "x5", "+", 0),
                        AssignmentNode("x5", "x6", "+", 0)
                    ])
                ])
            ])
        ),
        
        # 2 Variable Assignment
        (
            """
            while x1 > 0 do
                x1 = x1 - 1;
                x2 = x2 + 1
            end
            """
            ,
            SequenceNode([
                AssignmentNodeTwoVar("x2", "x2", "+", "x1", 1, 1),
                AssignmentNodeTwoVar("x1", "x1", "-", "x1", 1, 1) # TODO: Add global zero constant (via SymbolTable)
            ])
        ),
        (
            """
            while x1 > 0 do
                x1 = x1 - 1;
                x2 = x2 - 1
            end
            """
            ,
            SequenceNode([
                AssignmentNodeTwoVar("x2", "x2", "-", "x1", 1, 1),
                AssignmentNodeTwoVar("x1", "x1", "-", "x1", 1, 1) # TODO: Add global zero constant (via SymbolTable)
            ])
        ),
        (
            """
            while x1 > 0 do
                x2 = x2 + 1;
                x1 = x1 - 1
            end
            """
            ,
            SequenceNode([
                AssignmentNodeTwoVar("x2", "x2", "+", "x1", 1, 1),
                AssignmentNodeTwoVar("x1", "x1", "-", "x1", 1, 1) # TODO: Add global zero constant (via SymbolTable)
            ])
        ),
        (
            """
            while x1 > 0 do
                x2 = x2 - 1;
                x1 = x1 - 1
            end
            """
            ,
            SequenceNode([
                AssignmentNodeTwoVar("x2", "x2", "-", "x1", 1, 1),
                AssignmentNodeTwoVar("x1", "x1", "-", "x1", 1, 1) # TODO: Add global zero constant (via SymbolTable)
            ])
        )        
    ]

    def optimise(self, node):
        current_ast = node.stmt
        # print_ast_structure(current_ast, 0) 
        for pattern, replacement in self.PATTERNS:
            pattern_ast = build_ast(pattern).stmt
            current_ast = self.replace_matches_in_sequence(pattern_ast, replacement, current_ast)

        return ProgramNode(unflatten_ast(current_ast))

    def is_placeholder(self, s: str) -> bool:
        return isinstance(s, str) and re.fullmatch(r"x\d+", s) is not None
    
    def has_match_in_structure(self, pattern: Node, node: Node, bindings: Dict[str, str] = None) -> Optional[Dict[str, str]]:
        if bindings is None:
            bindings = {}

        temp_bindings = bindings.copy()

        if type(pattern) != type(node):
            return None

        for key, p_val in pattern.__dict__.items():
            if key not in node.__dict__:
                return None

            n_val = node.__dict__[key]

            if isinstance(p_val, str) and self.is_placeholder(p_val):
                if p_val in temp_bindings:
                    if temp_bindings[p_val] != n_val:
                        return None
                else:
                    # prevent different placeholders from mapping to the same register 
                    # if n_val in temp_bindings.values():
                        # return None
                    temp_bindings[p_val] = n_val

            elif isinstance(p_val, Node):
                if not isinstance(n_val, Node):
                    return None

                nested_bindings = self.has_match_in_structure(p_val, n_val, temp_bindings)
                if nested_bindings is None:
                    return None
                temp_bindings = nested_bindings

            elif isinstance(p_val, list):
                if not isinstance(n_val, list) or len(p_val) != len(n_val):
                    return None

                for i in range(len(p_val)):
                    result = self.has_match_in_structure(p_val[i], n_val[i], temp_bindings)
                    if result is None:
                        return None
                    temp_bindings = result

            elif p_val != n_val:
                return None

        return temp_bindings
    
    def find_all_matches(self, pattern: Node, root: Node) -> List[Tuple[Node, Dict[str, str]]]:
        results = []

        bindings = self.has_match_in_structure(pattern, root)
        if bindings is not None:
            results.append((root, bindings))

        if isinstance(root, SequenceNode):
            sub_nodes = root.statements
            p_len = len(pattern.statements) if isinstance(pattern, SequenceNode) else 1
            for i in range(len(sub_nodes) - p_len + 1):
                sub_slice = SequenceNode(sub_nodes[i:i+p_len])
                bindings = self.has_match_in_structure(pattern, sub_slice)
                if bindings is not None:
                    results.append((sub_slice, bindings))

        for key, value in root.__dict__.items():
            if isinstance(value, Node):
                results.extend(self.find_all_matches(pattern, value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        results.extend(self.find_all_matches(pattern, item))

        return results

    def apply_bindings(self, node: Node, bindings: Dict[str, str]) -> Node:
        node_copy = copy.deepcopy(node)

        for key, value in node_copy.__dict__.items():
            if isinstance(value, str) and self.is_placeholder(value):
                if value in bindings:
                    setattr(node_copy, key, bindings[value])
            elif isinstance(value, Node):
                setattr(node_copy, key, self.apply_bindings(value, bindings))
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, Node):
                        new_list.append(self.apply_bindings(item, bindings))
                    else:
                        new_list.append(item)
                setattr(node_copy, key, new_list)

        return node_copy
    
    def replace_matches_in_sequence(self, pattern: Node, replacement: Node, root: Node) -> Node:
        bindings = self.has_match_in_structure(pattern, root)
        if bindings:
            return self.apply_bindings(replacement, bindings)

        if isinstance(root, SequenceNode) and isinstance(pattern, SequenceNode):
            new_statements = []
            i = 0
            while i < len(root.statements):
                window = root.statements[i:i + len(pattern.statements)]
                if len(window) == len(pattern.statements):
                    sub_seq = SequenceNode(window)
                    bindings = self.has_match_in_structure(pattern, sub_seq)
                    if bindings:
                        replaced = self.apply_bindings(replacement, bindings)
                        new_statements.append(replaced)
                        i += len(pattern.statements)
                        continue
                new_statements.append(self.replace_matches_in_sequence(pattern, replacement, root.statements[i]))
                i += 1
            return SequenceNode(new_statements)
        
        for key, value in root.__dict__.items():
            if isinstance(value, Node):
                setattr(root, key, self.replace_matches_in_sequence(pattern, replacement, value))
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, Node):
                        new_list.append(self.replace_matches_in_sequence(pattern, replacement, item))
                    else:
                        new_list.append(item)
                setattr(root, key, new_list)
        
        return root