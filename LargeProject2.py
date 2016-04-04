# --------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.  Modified by Erik M. Buck
# READ THE PLY DOCUMENTATION AND WORK THROUGH THE PLY TUTORIAL(s).
# http://www.dabeaz.com/ply/ply.html
# THE DOCUMENTATION IS EXCELLENT AND EXPLAINS THE CONCEPTS AS WELL AS
# THE SPECIFICS OF PLY. THE DOCUMENTATION IS EQUALLY VALUABLE FOR
# Lex, YACC, Flex, and Bison.
# IF YOU HAVEN'T READ THE DOCUMENTATION AND COMPLETED A TUTORIAL, I
# WILL ASSUME YOU ARE NOT TAKING THIS CLASS SERIOUSLY!
# --------------------------------------------------------------------

import sys
sys.path.insert(0,"../..")

if sys.version_info[0] >= 3:
    raw_input = input

######################################################################
######################################################################
# Scanner generation
tokens = ('NAME','NUM',)

literals = ['+','*', '-', '/','(',')', '=', '{', '}', ';']
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUM(t):
    r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    t.value = float(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lex.lex()

######################################################################
######################################################################
# Parser generation and parse tree creator

######################################################################
# A Node class to represent each node in a parse tree
class Node:
   # dictionary of names->value pairs
   symbols = { }
   
   def __init__(self):
      """ Initializes self to an invalid state """
      self.children = []
      self.text = "invalid"
      self.function = lambda node: node.text
   
   def interp(self):
      """ Interprets the parse tree rooted at self """
      return self.function(self)

######################################################################
# Helper functions for interpreting parse tree
def block_interp_helper(node):
    result = 0
    for child in node.children :
        result = child.interp()
    return result

def set_symbol_value_helper(node):
    Node.symbols[node.children[0]] = node.children[1].interp()
    return Node.symbols[node.children[0]]

def get_symbol_value_helper(node):
   try:
      return Node.symbols[node.text]
   except LookupError:
      print("Undefined name '%s'" % node.text)
      return 0


######################################################################
## Sample BNF Grammar for expressions
##
## <statement> ::= <expr> ";"
##             | "{" <block_item_list> "}"
##             | "{" "}"
##
## <block_item_list> ::= <statement>
##                   | <block_item_list> <statement>
##
## <expr> ::= <term> ADD <expr>
##        |  <term> SUBTRACT <expr>
##        | <term>
##        | NAME = <expr>
##
## <term> ::= <factor> MULTIPLY <term>
##        |  <factor> DIVIDE <term>      
##        | <factor>
##
## <factor> ::= LPAREN <expr> RPAREN
##          | NUM
##          | NAME
##
######################################################################
def p_statement_a(p):
    ' statement : expr ";" '
    p[0] = p[1] # Return a Node instance (p[1] is already a Node)

def p_statement_b(p):
    ' statement : "{" "}" '
    p[0] = Node()  # Return a Node instance
    p[0].text = "block"
    p[0].children = []
    p[0].function = lambda node: 0

def p_statement_c(p):
    ' statement : "{" block_item_list "}" '
    p[0] = Node()  # Return a Node instance
    p[0].text = "block"
    p[0].children = p[2]
    p[0].function = lambda node: block_interp_helper(node)

def p_block_item_list_a(p):
    ' block_item_list : statement '
    p[0] = [ p[1] ]  # Return a list of Node instances (p[1] is already a Node)

def p_block_item_list_b(p):
    ' block_item_list : block_item_list statement '
    p[0] = p[1]
    p[0].append(p[2]) # Return a list of Node instances (p[1] is already a list and p[2] is already a Node instance))

def p_expr_a(p):
    'expr : term "+" expr'
    p[0] = Node() # Return a Node instance
    p[0].text = "+"
    p[0].children = [p[1], p[3]]
    p[0].function = lambda node: node.children[0].interp() + node.children[1].interp()

def p_expr_b(p):
    'expr : term "-" expr'
    p[0] = Node() # Return a Node instance
    p[0].text = "-"
    p[0].children = [p[1], p[3]]
    p[0].function = lambda node: node.children[0].interp() - node.children[1].interp()

def p_expr_c(p):
    'expr : term'
    p[0] = p[1] # Return a Node instance (p[1] is already a Node)

def p_expr_d(p):
    'expr : NAME "=" expr'
    p[0] = Node() # Return a Node instance
    p[0].text = '='
    p[0].children = [p[1],p[3]]
    p[0].function = lambda node: set_symbol_value_helper(node)

def p_term_a(p):
    '''term : factor '*' term '''
    p[0] = Node() # Return a Node instance
    p[0].text = "*"
    p[0].children = [p[1], p[3]]
    p[0].function = lambda node: node.children[0].interp() * node.children[1].interp()

def p_term_b(p):
    '''term : factor '/' term '''
    p[0] = Node() # Return a Node instance
    p[0].text = "/"
    p[0].children = [p[1], p[3]]
    p[0].function = lambda node: node.children[0].interp() / node.children[1].interp()

def p_term_c(p):
    '''term : factor'''
    p[0] = p[1] # Return a Node instance (p[1] is already a Node)

def p_factor_a(p):
    '''factor : "(" expr ")"'''
    p[0] = p[2] # Return a Node instance (p[2] is already a Node)

def p_factor_b(p):
    '''factor : NUM'''
    p[0] = Node() # Return a Node instance
    p[0].text = str(p[1])
    tmp = p[1]
    p[0].function = lambda node: tmp

def p_factor_c(p):
   '''factor : NAME'''
   p[0] = Node() # Return a Node instance
   p[0].text = p[1]
   p[0].function = lambda node: get_symbol_value_helper(node)

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()

######################################################################
######################################################################
# Test driver
while 1:
    try:
        s = raw_input('calc > ')
    except EOFError:
        break
    if not s: continue
    rootNode = yacc.parse(s+'\n') # parse() returns None upon error
    if None != rootNode:
        print rootNode.interp()   # print result of interpreting the entire node tree
