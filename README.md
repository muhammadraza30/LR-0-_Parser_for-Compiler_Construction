# SimpleLang Parser with Some Urdu Words instead of Coding Words
if --> agar
else --> varna
while --> jabtak
for --> tabtak
print --> dikhao
input --> likho

## The program will first convert the code into the lexems or you can say tokens then it will send it to the parser in which we implemented Recursive Descent Parser also called LR(0) Parser which parser the tokens according to matching the grammar if grammar allows that syntax it wiil successfully parser and move further it grammar doesn't allowed then it will through error and tells you where you did the mistake during writing the code. Also used AST nodes for parser to give successfully parsed expression.