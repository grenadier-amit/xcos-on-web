import os
import re

sci=""
with open("andblk.sci", 'r') as content_file:
	for line in content_file:
		contentLine=line.strip()
		if contentLine:
			contentLine=contentLine.split("//")
			contentLine=contentLine[0]
			
			if contentLine.endswith(".."):
				contentLine=contentLine.strip("..\n")
				sci=sci+contentLine
			elif contentLine:
				sci=sci+contentLine+'\n'
func_name=re.search("(\w+)\(job,arg1,arg2",sci)
print "function %s () {\n" %func_name.group(1)
sci=sci.split("\"define\" then\n")
sci=sci[1]
sci=sci.split("\nend\n")[0]
sci=sci.split('\n')

#print sci

varList=[]


def scilabString(token):
	print '\t%s = new ScilabString(%s);' %(token[0],token[1])
	

def scilabBoolean(token):
	token[1]=token[1].replace("%t","true")
	token[1]=token[1].replace("%f","false")
	print '\t%s = new ScilabBoolean(%s);' %(token[0],token[1])
	

def scilabDouble(token):
	print '\t%s = new ScilabDouble(%s);' %(token[0],token[1])



def tokenAnalyser(token):
	if token[1][1]=="\"":
		scilabString(token)
	elif token[1][1]=="%":
		scilabBoolean(token)
	else:
		scilabDouble(token)


def Analyser(token):
	if token[1].endswith(','):
		token[1]=token[1][:-1]
	if token[1][0]=="\"":
		token[1]='['+token[1]+']'
		scilabString(token)
	elif token[1][0]=="%":
		token[1]='['+token[1]+']'
		scilabBoolean(token)
	elif token[1][0].isdigit():
		token[1]='['+token[1]+']'
		scilabDouble(token)
	elif token[1][0]=="[":
		tokenAnalyser(token)
	else:
		print token



	


for line in sci:
	token=line.split("=")
	token2=token[0].split(".")
	if token2[0] not in varList:
		print "\n\tvar %s = %s;" %(token2[0],token[1])
		varList.append(token2[0])
	else:
		if not token[1].endswith(';'):
			token[1]=token[1].replace(";","],[")
		Analyser(token)


