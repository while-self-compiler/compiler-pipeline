from transpiler.src.parser.generated_ewhile_parser.ewhileParser import ewhileParser
from transpiler.src.parser.generated_ewhile_parser.ewhileListener import ewhileListener
from transpiler.config import TEMP_VARIABLE_REUSE_SAME_SCOPE

class SymbolTable: # one symbol table per scope
    def __init__(self, parent=None, global_scope=None):
        self.variables = {}  
        self.parent = parent # parent scope
        self.children = [] # child scopes
        self.order = 0 
        self.global_scope = global_scope
        self.temp_variables = set() # local temp variables

    def find_declared_scope(self, name, leaf_scope, current_scope): # scope climbing (scope inheritance)
        # Example:
        # Scope 1: {a -> 1, Scope 2 -> 2, b -> 3, c -> 4}, Scope 2: {a -> 1, b -> 2}
        # => the variable a will be inherited from Scope 1 and will have the same id
        # => the variable b will not be inherited from Scope 1 and will have a new id (because it is declared after Scope 2 is created)
        # Attention: Order matters! If a variable is declared in a parent scope after a child scope is created, the child scope will not inherit the variable

        if TEMP_VARIABLE_REUSE_SAME_SCOPE:
            if name in self.variables and self.variables[name]["decl"]:
                if not self.variables[name].get("recycled", False):
                    return self
        else:
            if name in self.variables and self.variables[name]["decl"] and self == leaf_scope:
                return self
        # if name in self.variables and self.variables[name]["decl"]:
        #     return self

        # TODO: Check if in same scope decl before use
        if name in self.variables and self.variables[name]["decl"] and self.find_order_of_scope(current_scope) > self.variables[name]["order"]:
            return self

        # also check if variable is a transpiled variable (id)
        for var_name in self.variables:
            if "id" in self.variables[var_name] and self.variables[var_name]["id"] == name:
                return self

        if self.parent: # if there is a parent scope
            return self.parent.find_declared_scope(name, leaf_scope, self)

        return None
    
    def find_order_of_scope(self, scope):
        if scope.parent is None:
            return 0 # global scope

        for i, (child, order) in enumerate(scope.parent.children):
            if child == scope:
                return order

        return None
    
    def add_child(self, child):
        self.children.append((child, self.order))
        self.order += 1

    def get_children(self):
        return self.children
    
    def is_global_var(self, name):
        return name[0] == "x" and name[1:].isdigit()

    def add_variable(self, name, declaration=False, temp=False):
        is_declared = self.find_declared_scope(name, self, self)

        if TEMP_VARIABLE_REUSE_SAME_SCOPE:
            if temp:
                self.temp_variables.add(name)
                
                if not is_declared:
                    self.variables[name] = {
                        "used": False, 
                        "assigned": False, 
                        "order": self.order, 
                        "decl": declaration, 
                        "global": False,
                        "temp": True 
                    }
                    self.order += 1
                return

            _global = self.is_global_var(name)

            if not is_declared and _global:
                self.global_scope.variables[name] = {
                    "used": False, 
                    "assigned": False, 
                    "order": self.order, 
                    "decl": declaration, 
                    "global": _global
                }
                self.global_scope.order += 1
            elif not is_declared and declaration:
                self.variables[name] = {
                    "used": False, 
                    "assigned": False, 
                    "order": self.order, 
                    "decl": declaration, 
                    "global": _global
                }
                self.order += 1
            elif is_declared and declaration:
                raise Exception(f"SemanticError: Variable {name} is already declared in this or parent scope.")
            elif not is_declared and not declaration:
                raise Exception(f"SemanticError: Variable {name} is not declared in this or parent scope.")
        else:
            if temp and not is_declared:
                self.variables[name] = {"used": False, "assigned": False, "order": self.order, "decl": declaration, "global": False}
                self.order += 1

            _global = self.is_global_var(name) # temp vars get skipped

            if not is_declared and _global:
                self.global_scope.variables[name] = {"used": False, "assigned": False, "order": self.order, "decl": declaration, "global": _global}
                self.global_scope.order += 1
            elif not is_declared and declaration:
                self.variables[name] = {"used": False, "assigned": False, "order": self.order, "decl": declaration, "global": _global}
                self.order += 1
            elif is_declared and declaration:
                raise Exception(f"SemanticError: Variable {name} is already declared in this or parent scope.")
            elif not is_declared and not declaration:
                raise Exception(f"SemanticError: Variable {name} is not declared in this or parent scope.")

    def mark_used(self, name):
        dec_scope = self.find_declared_scope(name, self, self)

        if dec_scope:
            dec_scope.variables[name]["used"] = True

    def mark_assigned(self, name):
        dec_scope = self.find_declared_scope(name, self, self)
        if dec_scope:
            dec_scope.variables[name]["assigned"] = True

    def mark_recycled(self, name, recycled=True):
        dec_scope = self.find_declared_scope(name, self, self)
        if dec_scope and name in dec_scope.variables:
            dec_scope.variables[name]["recycled"] = recycled
            return True
        return False

    def is_used(self, name):
        dec_scope = self.find_declared_scope(name, self, self)

        if dec_scope:
            return dec_scope.variables[name]["used"]
        
        return False
    
    def is_assigned(self, name):
        dec_scope = self.find_declared_scope(name, self, self)

        if dec_scope:
            return dec_scope.variables[name]["assigned"]
        
        return False
    
    def get_transpiled_name(self, name):
        dec_scope = self.find_declared_scope(name, self, self)

        if dec_scope:
            return dec_scope.variables[name]["id"]
        
        return None
    

class SymbolTableManager: 
    def __init__(self, global_scope):
        self.global_scope = global_scope
        self.counter = 1
        self.constant_zero = 0
        self.temp_counter = 1 # temp variable 1 is always used as constant 0 to reset a temp variable (invariant)
        self.not_declared = True
        
        self.scope_stack = [(global_scope, 0)] # (scope, next_child_index)

        self.temp_variable_pool = {}  # scope_id -> list of available temp vars in that scope
        self.global_temp_pool = []    # Global pool for any temp vars that can be used anywhere

    def prepare(self):
        self.declare_ids()

        self.not_declared = False
        self.temp_counter += self.counter
        self.constant_zero += self.counter 

    def declare_ids(self):
        # 1) Declare all "xi" variables with the same global id
        self.counter = self.declare_xi(self.global_scope) + 1

        # 2) Declare all other variables with unique ids
        self.counter = self.declare_variable(self.global_scope, self.counter)

    def declare_xi(self, scope):
        highest_id = 0
        for var_name in scope.variables:
            if scope.variables[var_name]["global"]:
                scope.variables[var_name]["id"] = var_name

                var_id = int(var_name[1:])
                if var_id > highest_id:
                    highest_id = var_id

        for child in scope.get_children():
            highest_id = max(highest_id, self.declare_xi(child[0]))

        return highest_id
    
    def declare_variable(self, scope, counter):
        for var_name in scope.variables: 
            if "id" not in scope.variables[var_name]:
                if scope.variables[var_name]["decl"]:
                    scope.variables[var_name]["id"] = f"x{counter}"
                    counter += 1
                else:
                    # inherit id from parent scope or current scope
                    declared_scope = scope.find_declared_scope(var_name, scope, scope)

                    if declared_scope:
                        scope.variables[var_name]["id"] = declared_scope.variables[var_name]["id"]
                    else:
                        raise Exception(f"SemanticError: Variable {var_name} is not declared in this or parent scope. (This should never happen, there is maybe a bug in the Transpiler)")

        for child in scope.get_children():
            counter = self.declare_variable(child[0], counter)

        return counter
    
    def get_constant_zero(self):
        if self.not_declared:
            raise Exception("SemanticError: Ids are not declared yet. You must call prepare() before using constant zero.")
        
        return f"x{self.constant_zero}"

    def get_global_scope(self):
        return self.global_scope
    
    def get_current_scope(self):
        return self.scope_stack[-1][0]
    
    def _get_scope_id(self, scope):
        return id(scope)
    
    def go_next_scope(self):
        current_scope, child_index = self.scope_stack[-1]
        children = current_scope.get_children()
        if child_index < len(children):
            next_scope = children[child_index][0]
            self.scope_stack[-1] = (current_scope, child_index + 1)
            self.scope_stack.append((next_scope, 0))

            if TEMP_VARIABLE_REUSE_SAME_SCOPE:
                # init local temp variable pool 
                scope_id = self._get_scope_id(next_scope)
                if scope_id not in self.temp_variable_pool:
                    self.temp_variable_pool[scope_id] = []
        else:
            raise Exception("SemanticError: No more scopes left.")
        
    def _sync_counter_with_pools(self):
        # Idea: Sync the temp_counter with the temp variable pools
        # so that the temp_counter is always the highest temp variable id

        all_temps = set(self.global_temp_pool)
        for pool in self.temp_variable_pool.values():
            all_temps.update(pool)

        max_suffix = 0
        for name in all_temps:
            try:
                num = int(name.lstrip("x"))
                max_suffix = max(max_suffix, num)
            except ValueError:
                continue

        self.temp_counter = max(self.temp_counter, max_suffix + 1)
    
    def go_previous_scope(self):
        if len(self.scope_stack) > 1:
            if TEMP_VARIABLE_REUSE_SAME_SCOPE:
                current_scope = self.scope_stack[-1][0]
                scope_id = self._get_scope_id(current_scope)

                if scope_id in self.temp_variable_pool and self.temp_variable_pool[scope_id]:
                    self.global_temp_pool.extend(self.temp_variable_pool[scope_id]) # add temp vars to global pool when leaving scope (go up)
                    self.temp_variable_pool[scope_id] = [] # important: clear the pool for reentry of the scope

            self.scope_stack.pop()  # back to parent scope
            # self._sync_counter_with_pools()
        else:
            raise Exception("SemanticError: Already at the global scope.")
        
    def put_temp_variable_in_pool(self, temp_var, put_global=True):
        if self.not_declared:
            raise Exception("SemanticError: Ids are not declared yet. You must call prepare() before using temp variables.")
        
        current_scope = self.get_current_scope()
        scope_id = self._get_scope_id(current_scope)

        if current_scope.mark_recycled(temp_var):
            if scope_id not in self.temp_variable_pool:
                self.temp_variable_pool[scope_id] = []
            
            if temp_var not in self.temp_variable_pool[scope_id]:
                self.temp_variable_pool[scope_id].append(temp_var)
        else:
            if put_global:
                if temp_var not in self.global_temp_pool:
                    self.global_temp_pool.append(temp_var)
    
    def put_list_of_temp_variables_in_pool(self, temp_vars, put_global=True):
        for temp_var in temp_vars:
            if temp_var == self.get_constant_zero(): # skip constant zero 
                continue 
            self.put_temp_variable_in_pool(temp_var, put_global=put_global)
    
    def get_temp_variable(self):
        """
        Main idea of temp variable reusing:
        - Scopes help to reuse temp variables in different scopes by encapsulating them
        - If TEMP_VARIABLE_REUSE_SAME_SCOPE is set to True, temp variables can also be reused in the same scope saving a lot of extra temp variables
          The temp variable reuse strategy follows this order:
                1. Try to reuse a temp var from the current scope
                2. Try to reuse from the global pool
                3. Create a new temp var if needed
           => Temp variable pools for each scope in transpiler enabling tempvar recycling in same scope
        """
        if self.not_declared:
            raise Exception("SemanticError: Ids are not declared yet. You must call prepare() before using temp variables.")
        
        # self._sync_counter_with_pools()

        current_scope = self.get_current_scope()

        if TEMP_VARIABLE_REUSE_SAME_SCOPE:
            scope_id = self._get_scope_id(current_scope)
            
            if scope_id in self.temp_variable_pool and self.temp_variable_pool[scope_id]:
                temp_var = self.temp_variable_pool[scope_id].pop(0)
                current_scope.mark_recycled(temp_var, False)
                return temp_var
                
            if self.global_temp_pool:
                temp_var = self.global_temp_pool.pop(0)
                current_scope.add_variable(temp_var, declaration=True, temp=True)
                return temp_var
        
        # check if temp var can be reused in the current scope, when its used just in a disjoint scope (i.e. not in current or parent scope)
        for i in range(self.constant_zero + 1, self.temp_counter):
            temp_name = f"x{i}"
            if not current_scope.find_declared_scope(temp_name, current_scope, current_scope):
                # check if temp variable is also not in current scope:
                if temp_name not in current_scope.temp_variables:
                    current_scope.add_variable(temp_name, declaration=True, temp=True)
                    return temp_name
        
        # create a new temp variable because all temp variables are used
        temp_name = f"x{self.temp_counter}"
        self.temp_counter += 1
        current_scope.add_variable(temp_name, declaration=True, temp=True)
        return temp_name
    
    def get_every_temp_variable_from_scope(self, scope):
        return list(scope.get_temp_variables())
    
    def get_all_scopes(self):
        return [scope for scope, _ in self.scope_stack]
    
    def search_scopes_dfs(self, name, scope):  
        found_scopes = []
        
        children = scope.get_children()
        for child in children:
            found_scope = self.search_scopes_dfs(name, child[0])
            if found_scope is not None:
                found_scopes += found_scope
        
        return found_scopes

class SymbolTableBuilder(ewhileListener):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.symbol_table.global_scope = self.symbol_table
        self.global_scope = self.symbol_table

    def _is_constant(self, token_text):
        return token_text.isdigit()

    def enterAssignment(self, ctx: ewhileParser.AssignmentContext):
        var_name = ctx.varTarget.text
        expr = ctx.expression()

        self.symbol_table.add_variable(var_name)
        self.symbol_table.mark_assigned(var_name)

        if expr.left:
            left_text = expr.left.text
            if not self._is_constant(left_text):
                self.symbol_table.add_variable(left_text)
                self.symbol_table.mark_used(left_text)
                
        if expr.right:
            right_text = expr.right.text
            if not self._is_constant(right_text):
                self.symbol_table.add_variable(right_text)
                self.symbol_table.mark_used(right_text)

    def enterDeclaration(self, ctx: ewhileParser.DeclarationContext): # bind a variable to a scope
        i = 0

        while ctx.VAR(i) is not None:
            var_name = ctx.VAR(i).getText()
            self.symbol_table.add_variable(var_name, declaration=True)

            # For debugging:
            # print("Declaration:", var_name, "in scope", id(self.symbol_table))

            i += 1
                   
    def enterWhileStmt(self, ctx: ewhileParser.WhileStmtContext):
        cond_expr = ctx.condition()

        # new scope
        parent_scope = self.symbol_table
        self.symbol_table = SymbolTable(self.symbol_table, self.global_scope)
        parent_scope.add_child(self.symbol_table)

        # cond_expr.left op cond_expr.right

        if cond_expr.left:
            left_symbol = cond_expr.left.left.text

            if not self._is_constant(left_symbol):
                self.symbol_table.add_variable(left_symbol)
                self.symbol_table.mark_used(left_symbol)

            if cond_expr.left.right:
                right_symbol = cond_expr.left.right.text
                if not self._is_constant(right_symbol):
                    self.symbol_table.add_variable(right_symbol)
                    self.symbol_table.mark_used(right_symbol)
        if cond_expr.right:
            left_symbol = cond_expr.right.left.text
            
            if not self._is_constant(left_symbol):
                self.symbol_table.add_variable(left_symbol)
                self.symbol_table.mark_used(left_symbol)

            if cond_expr.right.right:
                right_symbol = cond_expr.right.right.text
                if not self._is_constant(right_symbol):
                    self.symbol_table.add_variable(right_symbol)
                    self.symbol_table.mark_used(right_symbol)

    def exitWhileStmt(self, ctx: ewhileParser.WhileStmtContext):
        self.symbol_table = self.symbol_table.parent

    def enterIfStmt(self, ctx: ewhileParser.IfStmtContext):
        cond_expr = ctx.condition()

        # new scope for if
        parent_scope = self.symbol_table
        self.symbol_table = SymbolTable(parent_scope, self.global_scope)
        parent_scope.add_child(self.symbol_table)

        if cond_expr.left:
            left_symbol = cond_expr.left.left.text

            if not self._is_constant(left_symbol):
                self.symbol_table.add_variable(left_symbol)
                self.symbol_table.mark_used(left_symbol)

            if cond_expr.left.right:
                right_symbol = cond_expr.left.right.text
                if not self._is_constant(right_symbol):
                    self.symbol_table.add_variable(right_symbol)
                    self.symbol_table.mark_used(right_symbol)
        if cond_expr.right:
            left_symbol = cond_expr.right.left.text
            
            if not self._is_constant(left_symbol):
                self.symbol_table.add_variable(left_symbol)
                self.symbol_table.mark_used(left_symbol)

            if cond_expr.right.right:
                right_symbol = cond_expr.right.right.text
                if not self._is_constant(right_symbol):
                    self.symbol_table.add_variable(right_symbol)
                    self.symbol_table.mark_used(right_symbol)

        # print("If Stmt:", id(self.symbol_table), id(parent_scope))

    def enterElseStmt(self, ctx):
        if_scope = self.symbol_table
        parent_scope = if_scope.parent # Parent is needed because else is defined inside if block

        self.symbol_table = SymbolTable(parent_scope, self.global_scope)
        parent_scope.add_child(self.symbol_table)

        # print("Else Stmt:", id(self.symbol_table), id(parent_scope))

    def exitElseStmt(self, ctx):
        self.symbol_table = self.symbol_table.parent
    
    def exitIfStmt(self, ctx: ewhileParser.IfStmtContext):
        # just go back if else stmt not already executed (no else stmt exists)
        if ctx.elseStmt() is None:
            self.symbol_table = self.symbol_table.parent
    
    def get_symbol_table(self):
        return self.symbol_table
    
    def get_global_scope(self):
        return self.global_scope