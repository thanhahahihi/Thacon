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
    return
    print(F"{colorama.Fore.CYAN}debug:",*content,F"{colorama.Fore.CYAN}|",**keys)
    # print(F"{colorama.Fore.YELLOW}{"-"*20}")

import ast
class varvisitor(ast.NodeVisitor):
    def __init__(self,usedvars:list):
        super().__init__()
        self.vars=[]
        self.usedvarname=usedvars
    def visit_Name(self, node):
        if(not node.id in self.usedvarname):
            self.usedvarname.append(node.id)
            self.vars.append(node.id)

    def __del__(self):
        # self.usedvarname.remove()
        for name in self.vars:
            self.usedvarname.remove(name)

class scope:
    def __init__(self,express:str="root"):
        self.expression=express
        self.command=list()

    def check_new(char:str):
        res=False
        if('a'<=char<='z' or 'A'<=char<='Z' or '0'<=char<='9' or char in '\'\"(['):
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
            if(scope.check_new(char)):
                if(express[-1]==' '):
                    add()
            if(char in '\'\"[('):
                stack.append(char)
            express+=char
        def check_stack():
            nonlocal express
            if(len(stack)==0):
                express+=' '
        for char in content:
            if(len(stack)==0):
                if(char=='{'):
                    scope_stack[-1].append(scope(express.strip()))
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
                else:
                    chung(char)
            else:
                express+=char
                if(stack[-1] in '\'\"'):
                    if(char==stack[-1]):
                        if(express[-1]!='\\'):
                            stack.pop()
                elif(char==']'):
                    if(stack[-1]=='['):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(char==')'):
                    if(stack[-1]=='('):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(char=='}'):
                    if(stack[-1]=='{'):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(char in '\'\"{[('):
                    stack.append(char)
                check_stack()
        add()


    def __repr__(self):
        if(self.expression!=None):
            return F"{self.expression}:{list(self.command)}"
    
    def generate_python(self,prefix:str='',used_vars=[])->str:
        R"""
        brief:generate python code from description by scope
        param prefix:the prefix string before the new python code('\t'*k)
        param used_vars:list varianles have been used in parent scope
        """
        # res=""
        cur_vars=varvisitor(used_vars)#used variable name in this scope
        if(self.expression!=None):
            precommand=prefix+F"for _ in range(int({self.expression})):\n"
            prefix+='\t'
        else:
            precommand=""
        res=prefix+"file.write(F\""
        def endwrite():
            nonlocal res
            if(res[-3:]=="(F\""):
                pass
                res=res[0:-13]+'\n'
            else:
                res+=F"\")\n"
        for cmd in self.command:
            if(type(cmd)==str):
                if(cmd==','):
                    res+=" "
                elif(cmd==';'):
                    res+=F"\\n\")\n{prefix}file.write(F\""
                    # endwrite()
                else:
                    cmd=cmd.strip()
                    res+="{"+cmd+"}"
                    cur_vars.visit(ast.parse(cmd))
            elif(type(cmd)==scope):
                # res+="\")\n"
                endwrite()
                cur_vars.visit(ast.parse(cmd.expression.strip()))
                res+=cmd.generate_python(prefix,used_vars)
                res+=prefix+"file.write(F\""
        # res+="\")\n"
        endwrite()
        if(len(cur_vars.vars)>0):
            res+=prefix+"del "
        precommand+=prefix
        for name in cur_vars.vars:
            precommand+=F"{name}=gen{name}();"
            res+=F"{name},"
        precommand=precommand[0:-1]+'\n'
        res=res[0:-1]+'\n'
        del cur_vars
        return precommand+res


        


class subtask:
    '''
    Subtask in competitive programing with each limits
    '''
    def __init__(self,ls:scope):
        '''
        Constructor of subtask class
        brief: initalize generator string from scope
        syntax:
        for each item of ls:
            it contains a variable name with '=' operator
            after '=' if the value contains ':' it will random from before ':' to after ':'
            else it will be as normal python epression
        for example:
            a=10:1e9 is a=random.ranint(10,int(1e9)) in python
            b=100 then b equall 100,which is a constant
        '''
        self.ratio=float(eval(ls.expression))
        self.funcs={}
        for express in ls.command:
            if(type(express)!=str):
                return Exception("subtask error")
            i=express.find('=')
            if(i<1):continue
            name=express[0:i]
            express=express[i+1:]
            i=0
            stack=[]
            while(i<len(express)):
                if(express[i]==':'):
                    if(len(stack)==0):break
                elif(express[i] in '{[('):
                    stack.append(express[i])
                elif(express[i]=='}'):
                    if(stack[-1]=='{'):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(express[i]==']'):
                    if(stack[-1]=='['):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(express[i]==')'):
                    if(stack[-1]=="("):
                        stack.pop()
                    else:
                        return Exception("scope error")
                elif(express[i] in '\'\"'):
                    if(len(stack)>0):
                        if(stack[-1]==express[i]):
                            if(express[i-1]!='\\'):
                                stack.pop()
                    else:
                        stack.append(express[i])
                i+=1
            if(i<len(express)):
                self.funcs[name]=F"lambda:random.randint(int({express[0:i]}),int({express[i+1:]}))"
            else:
                self.funcs[name]=F"lambda:{express}"
    def __repr__(self):
        return F"{self.ratio}\n{self.funcs}"
    
    def embed(self,fundict:dict,prefix:str="gen"):
        '''
        Function for write generator function for each variable in subtask
        param:prefix ,which is prefix of function name
        '''
        for key,value in self.funcs.items():
            fundict[prefix+key]=eval(value,fundict)

import subprocess
import pathlib
class generator:
    """
    Random input generator
    """
    def __init__(self):
        self.maincode:str=""#python code to write generated input
        self.lim=subtask(scope("0"))#default limits of vars
        self.subtasks=list[subtask]()#each limits per subtask

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
        for cmds in sps.command:
            if(type(cmds)==scope):
                if(cmds.expression=="sub"):
                    self.subtasks=[]
                    for item in cmds.command:
                        self.subtasks.append(subtask(item))
                elif(cmds.expression=="lim"):
                    cmds.expression="0"
                    self.lim=subtask(cmds)
                    cmds.expression="lim"
                elif(cmds.expression=="struct"):
                    cmds.expression=None
                    self.maincode="\nimport random\n"+cmds.generate_python()
                    cmds.expression="struct"
        debugprint(self.lim)
        debugprint(self.subtasks)
        debugprint("main code:"+self.maincode)
    def generate(self,dir:str,num:int,cmd:str):
        """
        Generate inputs
        param dir:  directory contains input folder
        param num:  the number of test case
        param cmd:  command to solve that input
        """
        cur_num=0
        for sub in self.subtasks:
            sandboxvars={}
            self.lim.embed(sandboxvars)
            sub.embed(sandboxvars)
            for _ in range(int(sub.ratio*num)):
                cur_num+=1
                dirname=str(cur_num)
                dirname="test"+'0'*(3-len(dirname))+dirname
                debugprint(F"generating {dirname}")
                dirname=dir+'/'+dirname
                if(not pathlib.Path(dirname).exists()):
                    os.mkdir(dirname)
                sandboxvars["file"]=open(F"{dirname}/{self.generated_file}",'w')
                exec(self.maincode,sandboxvars)
                subprocess.run(
                    cmd,
                    shell=True,
                    cwd=F"{dirname}"
                )
                sandboxvars['file'].close()




def main(arguments:list):
    parser=argparse.ArgumentParser()
    parser.add_argument("file",type=str,help="description file",default="example.gt")
    parser.add_argument("-od",dest="outdir",default=None,type=str,help="output directory (default: .)")
    parser.add_argument('-n',dest="num",help="the numbar of input",default=10,type=int)
    parser.add_argument("-c",dest="command",default="echo created successfully",help="command to solve",type=str)
    config=parser.parse_args(arguments)
    maingen=generator()
    maingen.load(config.file)
    if(config.outdir==None):
        i=max(config.file.rfind('/'),config.file.rfind('\\'))
        debugprint(i)
        if(i==-1):
            config.outdir='.'
        else:
            config.outdir=config.file[0:i]
        
        # exit(0)
    maingen.generate(dir=config.outdir,num=config.num,cmd=config.command)

if(__name__=="__main__"):
    main(sys.argv[1:])

# print(generator.__doc__)
# print(type(sys.argv))