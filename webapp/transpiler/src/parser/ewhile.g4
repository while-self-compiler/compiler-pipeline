grammar ewhile;


// Parser rules

prog: stmt? EOF;

stmt: 
      declaration                               # declarationStmt
    | assignment                                # assignmentStmt
    | PRINT (X_VAR | VAR)                       # printStmt
    | stmt SEMI stmt                            # sequenceStmt
    | WHILE condition DO stmt END               # whileStmt
    | IF condition THEN stmt (elseStmt)? END    # ifStmt
    | macroStmt (stmt)?                         # macroExtensionStmt          
    | MACRO_ACCESS VAR                          # macroAccessStmt
    ;

elseStmt: ELSE stmt 
    ; // this explicit rule is needed for symboltable building

macroStmt: MACRO VAR START stmt FINISH
    ;
declaration: LET VAR (MULTI_DELIM VAR)*;
assignment: varTarget= (X_VAR | VAR) ASSIGN expression;
// TODO: Multiple expressions in one assignment (precedence)
expression: (left=(X_VAR | VAR | CONST) (op=(PLUS | MINUS | TIMES | DIV | MODULO | SHIFTLEFT | SHIFTRIGHT | POWER | MAX | MIN) right=(X_VAR | VAR | CONST))?);
condition: left=expression op=(GREATER | EQUALS | NOTEQUALS) right=expression;

// TODO: Add functions
// https://softwareengineering.stackexchange.com/questions/279004/general-way-to-convert-a-loop-while-for-to-recursion-or-from-a-recursion-to-a


// Lexer rules

DO: 'DO' | 'Do' | 'do';
END: 'END' | 'End' | 'end';
WHILE: 'WHILE' | 'While' | 'while';
LET: 'LET' | 'Let' | 'let';
MACRO: 'MACRO' | 'Macro' | 'macro';
START: '{';
FINISH: '}';
PRINT: 'ECHO' | 'Echo' | 'echo'; // used for debugging the self-compiler

MULTI_DELIM: ',';

GREATER: '>';
ASSIGN: '=';
EQUALS: '==';
NOTEQUALS: '!=';

MAX: '^?';
MIN: 'v?';
PLUS: '+';
MINUS: '-';
TIMES: '*';
DIV: '/';
MODULO: '%';
SHIFTLEFT: '<<';
SHIFTRIGHT: '>>';
POWER: '^';

IF: 'IF' | 'If' | 'if';
ELSE: 'ELSE' | 'Else' | 'else';
ELIF: 'ELIF' | 'Elif' | 'elif';
THEN: 'THEN' | 'Then' | 'then';

MACRO_ACCESS: 'USE' | 'Use' | 'use';

// attention: keywords must be defined before VAR
X_VAR: 'x' NUM; // "special" variables
VAR: [a-zA-Z]+; // ID
CONST: NUM;
NUM: /*'-'?*/ [1-9][0-9]* | '0';

SEMI: ';';
WS: [ \t\r\n]+ -> channel(HIDDEN) ; // Important: Channel HIDDEN is used for preprocessor 

COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT : '/*' ( BLOCK_COMMENT | . )*? '*/'  -> skip ;