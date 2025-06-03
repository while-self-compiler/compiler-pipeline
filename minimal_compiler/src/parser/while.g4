grammar while;


// Parser rules

prog: stmt? EOF;

stmt: assignment                    # assignmentStmt
    | stmt SEMI stmt                # sequenceStmt
    // | LOOP VAR DO stmt END          # loopStmt
    | WHILE condition DO stmt END   # whileStmt
    ;

assignment: VAR ASSIGN VAR (PLUS | MINUS) CONST;
condition: VAR GREATER CONST;


// Lexer rules

VAR: 'x' NUM;
CONST: NUM;
NUM: /*'-'?*/ [1-9][0-9]* | '0';

DO: 'DO' | 'Do' | 'do';
END: 'END' | 'End' | 'end';
WHILE: 'WHILE' | 'While' | 'while';
// LOOP: 'LOOP' | 'Loop' | 'loop';

GREATER: '>';
ASSIGN: '=';

PLUS: '+';
MINUS: '-';

SEMI: ';';
WS: [ \t\r\n]+ -> skip ;

// allow comments with ;; to end of line
// this is not in the original grammar but helps for debugging and documentation 
COMMENT: '/' ~[\r\n]* -> skip;
BLOCK_COMMENT : '/*' ( BLOCK_COMMENT | . )*? '*/'  -> skip ;