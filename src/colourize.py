import token, tokenize, keyword
import StringIO

class Colourizer(object):

    def __init__(self, linenumber=False):
        self.tokenString = ''
        self.reset(linenumber)
        
    def reset(self, linenumber=False):
        self.beginLine, self.beginColumn = (0, 0)
        self.endOldLine, self.endOldColumn = (0, 0)
        self.endLine, self.endColumn = (0, 0)
        self.tokenType = token.NEWLINE
        self.outputLineNumber = linenumber

#===== Keywords, numbers and operators ===
    def formatName(self, aWord):
        if keyword.iskeyword(aWord.strip()):
            return "<span class='py_keyword'>"
        else:
            return "<span class='py_variable'>"

    def formatNumber(self):
        return "<span class='py_number'>"

    def formatOperator(self):
        return "<span class='py_op'>"

#========= Strings, including comments ====
    def formatString(self):
        if len(self.tokenString) <= 2:
            self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
            return "<span class='py_string'>"
        if self.tokenString[0] == self.tokenString[1] and \
               self.tokenString[1] == self.tokenString[2] and\
               self.tokenString[0] in ["'", '"']:
            return self.formatMultiLineComment()
        else:
            self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
            return "<span class='py_string'>"

    def formatComment(self):
        self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
        return "<span class='py_comment'>"
    
    def changeHTMLspecialCharacters(self, aString):
        aString = aString.replace('&', '&amp;')
        aString = aString.replace('<', '&lt;')
        aString = aString.replace('>', '&gt;')
        return aString

    def formatMultiLineComment(self):
        self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
        if self.outputLineNumber:
            temp_in = self.tokenString.split('\n')
            line_num = self.beginLine
            if line_num == 1:
                prefix = "<span class='py_linenumber'>%3d </span>"%line_num
            else:
                prefix = ''
            temp_out = prefix + temp_in[0]
            for substring in temp_in[1:]:
                line_num += 1
                temp_out += "\n<span class='py_linenumber'>%3d </span>"%line_num \
                            + substring
            self.tokenString = temp_out
        return "<span class='py_comment'>"

    def indent(self):
        self.tokenString = " "*self.beginColumn + self.tokenString

    def spaceToken(self):
        self.tokenString = " "*(self.beginColumn - self.endOldColumn) +  \
                            self.tokenString

# ==================================
    def htmlFormat(self):
        if self.tokenType == token.NAME:
            beginSpan = self.formatName(self.tokenString)
        elif self.tokenType == token.STRING:
            beginSpan = self.formatString()
        elif self.tokenType == tokenize.COMMENT:
            beginSpan = self.formatComment()
        elif self.tokenType == token.NUMBER:
            beginSpan = self.formatNumber()
        elif self.tokenType == token.OP:
            beginSpan = self.formatOperator()
        else:
            beginSpan = "<span>"
    
        if self.tokenString == '\n':
            htmlString = '\n'
        elif self.tokenString == '':
            htmlString = ''
        else:
            htmlString = beginSpan + self.tokenString + "</span>"
        return htmlString

    def processNewLine(self):
        if self.lastTokenType in [tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL]: 
            if self.outputLineNumber:
                self.outp.write("<span class='py_linenumber'>%3d </span>" % self.beginLine) 
        elif self.tokenType != tokenize.DEDENT:  # logical line continues
            self.outp.write("\n")
        else:
            pass  # end of file
            
# inp.readline reads a "logical" line;
# the continuation character '\' is gobbled up.
    def parseListing(self, code):
        self.inp = StringIO.StringIO(code)
        self.outp = StringIO.StringIO()
        for tok in tokenize.generate_tokens(self.inp.readline):
            self.lastTokenType = self.tokenType
            self.tokenType = tok[0]
            self.lastTokenString = self.tokenString
            self.tokenString = tok[1]
            self.beginLine, self.beginColumn = tok[2]
            self.endOldLine, self.endOldColumn = self.endLine, self.endColumn
            self.endLine, self.endColumn = tok[3]

            if self.tokenType == token.ENDMARKER:  
                break
            if self.beginLine != self.endOldLine:
                self.processNewLine()
                self.indent()
            else:
                self.spaceToken()
            self.outp.write("%s" % self.htmlFormat()) 
        code = self.outp.getvalue()
        self.inp.close()
        self.outp.close()
        self.reset()
        return code

