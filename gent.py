#!/usr/bin/python3
'''
Docstring for tools.gentest
line 1:name of a generated file
line 2 or more: list used variable and value or seg of it
the next: structure of a generated file
next: list subtask
'''
inputfile='''
#test.gt
TREE.INP
struct{
    n;
    n{a,}
}
lim{
    a=1:1e9,n=1:1e9
}
sub{
    #subtask1 2 test
    2{a=-10:10,n=2}
    #subtask2 3 testTestRunner
    3{n=50:100}
}
'''
import os
import argparse
import sys
import colorama
colorama.init(autoreset=True)

def debugprint(*content,**keys):
    print(F"{colorama.Fore.CYAN}debug:",*content,F"{colorama.Fore.CYAN}|",**keys)
    # print(F"{colorama.Fore.YELLOW}{"-"*20}")

class scope:
    def __init__(self,express:str="root"):
        self.expression=express
        self.command=list()

    def check_new(char:str):
        if('a'<=char<='z' or 'A'<=char<='Z' or '0'<=char<='9' or char in '\'\"()[]{}'):
            res=True
        return res
    
    # def __list__
    
    def parse(self,content:str):
        scope_stack=[self.command]
        stack=[]
        express=' '
        def add():
            nonlocal express
            if(express!=' '):
                scope_stack[-1].append(express.strip())
            express=' '
        def chung(char):
            nonlocal express
            if(express[-1]==' '):
                if(scope.check_new(char)):
                    add()
            if(char in '\'\"[('):
                stack.append(char)
            express+=char
        for char in content:
            if(len(stack)==0):
                if(char=='{'):
                    scope_stack[-1].append(scope(express))
                    scope_stack.append(scope_stack[-1][-1].command)
                    express=' '
                elif(char=='}'):
                    add()
                    scope_stack.pop()
                elif(char in ',;'):
                    add()
                    scope_stack[-1].append(char)
                elif(char=='\n'):
                    add()
                elif(char==' '):
                    if(scope.check_new(express[-1])):
                        express+=char
                else:
                    chung(char)
            elif(stack[-1] in '\'\"'):
                if(char==stack[-1]):
                    if(express[-1]!='\\'):
                        stack.pop()
                express+=char
            elif(char==']'):
                if(stack[-1]=='['):
                    stack.pop()
                else:
                    return Exception("scope error")
                express+=char
            elif(char==')'):
                if(stack[-1]=='('):
                    stack.pop()
                else:
                    return Exception("scope error")
                express+=char
            elif(char=='}'):
                if(stack[-1]=='{'):
                    stack.pop()
                else:
                    return Exception("scope error")
                express+=char
            else:
                chung(char)
        add()


    def __repr__(self):
        if(self.expression!=None):
            return F"{self.expression}:{list(self.command)}"

class generator:
    """
    Random input generator
    """
    def __init__(self):
        pass

    def parse_minimal(lines:list[str]):
        """
        Delete comments and handle slashes
        """
        lines.insert(0,'\\')
        # debugprint(lines)
        i=1
        while(i<len(lines)):
            li=lines[i].rstrip()
            debugprint(lines)
            # debugprint(F"{i}:{li}")
            if(lines[i-1][-1]=='\\'):
                lines.pop(i)
                lines[i-1]=lines[i-1][0:-1]+li
                # debugprint(lines[i-1])
            else:
                lines[i-1]=lines[i-1].split('#')[0].strip()
                if(lines[i-1]==''):
                    del lines[i-1]
                    i-=1
                if(len(li)>0):
                    lines[i]=li.lstrip()
                i+=1
            # debugprint(F"{len(lines)}-{i}:{li}")

    def parse_scope(conntent:str)->dict:
        scope={}
        stack=[]
        scope_name=''
        for char in conntent:
            if(len(stack)==0):
                if(char=='{'):
                    stack.append('{')
                    scope_name=scope_name.strip()
                    scope[scope_name]=''
                else:
                    scope_name+=char
            else:
                if(stack[-1] in '\'\"'):
                    if(char==stack[-1]):
                        if(scope[scope_name][-1]!='\\'):
                            stack.pop()
                elif(char=='}'):
                    if(stack[-1]=='{'):
                        stack.pop()
                        if(len(stack)==0):
                            scope_name=''
                            continue
                    else:
                        
                        print(F"{colorama.Fore.RED}scope error")
                        exit(1)
                elif(char in ']'):
                    if(stack[-1]=='['):
                        stack.pop()
                    else:
                        print(F"{colorama.Fore.RED}scope error")
                        exit(1)
                elif(char in ')'):
                    if(stack[-1]=='('):
                        stack.pop()
                    else:
                        print(F"{colorama.Fore.RED}scope error")
                        exit(1)
                elif(char in '\'\"{[('):
                    stack.append(char)

                scope[scope_name]+=char

        return scope

    def load(self,FilenamOrContent:str):
        """
        Read the description from the file

        :param filename: name of the description file
        :return True if read sucessfully
        """
        #check  var is filename
        lines=FilenamOrContent.split('\n')
        if(len(lines)==1):
            lines=open(lines[0],'r').readlines()
        # lines=[x.rstrip() for x in lines]
        generator.parse_minimal(lines)
        debugprint(F"connent of file:\n{lines}")
        content=''
        for i in lines:content+=i+'\n'
        debugprint("after parse minimal:",'\n'+content)
        sps=scope()
        sps.parse(content)
        self.generated_file=sps.command[0]
        debugprint(sps)




def main(arguments:list):
    parser=argparse.ArgumentParser()
    parser.add_argument("file",type=str,help="description file",default="example.gt")
    parser.add_argument("-od",dest="outdir",default='.',type=str,help="output directory (default: .)")
    parser.add_argument('-n',dest="num",help="the numbar of input",default=1,type=int)
    parser.add_argument("-c",dest="command",default="echo created successfully",help="command to solve",type=str)
    config=parser.parse_args(arguments)
    maingen=generator()
    maingen.load(config.file)

if(__name__=="__main__"):
    main(sys.argv[1:])

# print(generator.__doc__)
# print(type(sys.argv))