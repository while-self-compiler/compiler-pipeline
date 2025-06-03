class BaseOptimiser:
    def optimise(self, node):
        return node.accept(self)

class OptimiserManager:
    def __init__(self, optimisers):
        self.optimisers = optimisers or []
    
    def add_optimiser(self, optimiser):
        self.optimisers.append(optimiser)
    
    def optimise(self, ast):
        for optimiser in self.optimisers:
            ast = optimiser.optimise(ast)  

        return ast