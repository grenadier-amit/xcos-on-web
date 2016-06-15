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



sci2=[]
line2append=''
flag=0
for line in sci:
	
	if line.find('=')!=-1:
		temp=line.split('=')[1]
	else:
		temp=line
	if flag and temp.endswith("]"):
		flag=0
		line2append+=line
		sci2.append(line2append)
		line2append=''
	elif flag:
		line2append+=line
	elif temp.startswith('[') and not temp.endswith(']'):
		flag=1
		line2append=line
	else:
		sci2.append(line)

sci=sci2

#print sci

varList={'this.x':'scicos_model()'}


def scilabString(token):
	token=token.replace("[]","")
	return 'new ScilabString(%s)' %token
	

def scilabBoolean(token):
	token=token.replace("[]","")
	token=token.replace("%t","true")
	token=token.replace("%f","false")
	return 'new ScilabBoolean(%s)' %token
	

def scilabDouble(token):
	token=token.replace("[]","")
	return 'new ScilabDouble(%s)' %token



def tokenAnalyser(token):
	if token[1][1]=="\"":
		print '\t%s = %s;' %(token[0],scilabString(token[1]))
		
	elif token[1][1]=="%":
		print '\t%s = %s;' %(token[0],scilabBoolean(token[1]))
	else:
		print '\t%s = %s;' %(token[0],scilabDouble(token[1]))



def argAnalyser(token):
	if token[0]=="\"":
		token='['+token+']'
		return scilabString(token)
	elif token[0]=="%":
		token='['+token+']'
		return scilabBoolean(token)
	elif token[0].isdigit() or (token[0] in ('-','+') and token[1].isdigit()):
		token='['+token+']'
		return scilabDouble(token)
	elif token[0]=='[':
		if token[1]=="\"":
			return scilabString(token)
		elif token[1]=="%":
			return scilabBoolean(token)
		elif token[1].isdigit() or (token[2] in ('-','+') and token[3].isdigit()):
			return scilabDouble(token)
		else:
			return token
	else:
		return token

def diagram(token):
	
		temp_str=""
		token[0]=re.sub("(\(\d+\))","",token[0])
		temp_str=temp_str+token[0]
		
		return temp_str

def listCheck(token):
	args=[]
	listType=re.search('(.?list)',token[1])
	arguments=re.search('\((.*)\)',token[1])
	arguments=arguments.group(1).split(",")
					
	if arguments[0] != '':
		for i in arguments:
			if i not in varList:
				args.append(argAnalyser(i))
			else:
				args.append(i)
	args=listType.group(1)+'('+','.join(args)+')'
	return args

def scicosLink(token):
	arguments=re.search('\((.*)\)',token[1])
	arguments=arguments.group(1).replace('=',':')
	args=re.findall('(\w+:[0-9\[\]\.,\-]+)',arguments)
	
	argList=[]
	for i in args:
		temp=re.findall(':([0-9\[\]\.,\-]+)',i)
		temp=temp[0]
		if temp.endswith(','):
			temp=temp[:-1]

		temp2=re.findall('(\w+:)',i)
		temp2=temp2[0]
		argList.append(temp2+' '+argAnalyser(temp))

	return argList

def epsilon(token):
	leftStr=token[0]
	rightStr=token[1]
	pushFlag=0

	if rightStr in varList.keys():
		varType=re.search('(Scilab\w+)',argAnalyser(varList[rightStr]))

		if not varType:
			rightStr=rightStr
		elif varType.group(1)=='ScilabString':
			rightStr='new ScilabString(['+rightStr+"])"
		elif varType.group(1)=='ScilabDouble':
			rightStr='new ScilabDouble(['+rightStr+"])"
		elif varType.group(1)=='ScilabBoolean':
			rightStr='new ScilabBoolean(['+rightStr+"])"


	
	if re.search('(\d)',token[0]):
		pushFlag=1
		leftStr=diagram(token)
	
	elif re.search('.?list',token[1]):
		rightStr=listCheck(token)

	elif re.search('scicos_link',token[1]):
		rightStr="scicos_link({"
		rightStr+=','.join(scicosLink(token))+"})"

	elif re.search('standard_define',token[1]):
		arguments=re.search('\w+\((.*)\)',token[1])
		arguments=arguments.group(1).replace(',',' ',1)
		arguments=arguments.split(',')
		arguments[0]=arguments[0].replace(' ',',')
		arguments[0]=scilabDouble(arguments[0])

		rightStr='standard_define('+','.join(arguments)+")"

		
	if pushFlag:
		print '\t'+leftStr+'.push('+rightStr+');'
	else:
		print '\t'+leftStr+'='+rightStr+';'






def Analyser(token):
	if token[1].endswith(',') or token[1].endswith(';') :
		token[1]=token[1][:-1]
	if token[1][0]=="\"":
		token[1]='['+token[1]+']'
		print '\t%s = %s;' %(token[0],scilabString(token[1]))
	elif token[1][0]=="%":
		token[1]='['+token[1]+']'
		print '\t%s = %s;' %(token[0],scilabBoolean(token[1]))
	elif token[1][0].isdigit() or (token[1][0] in ('-','+') and token[1][1].isdigit()):
		token[1]='['+token[1]+']'
		print '\t%s = %s;' %(token[0],scilabDouble(token[1]))
	elif token[1][0]=="[":
		tokenAnalyser(token)
	else:
		#print token
		epsilon(token)



	


for line in sci:
	token=line.split("=",1)
	token2=token[0].split(".")
	if token2[0] == "x":
		token2[0] ="this.x"
		token[0]='.'.join(token2)
	token[1]=token[1].replace(" ",",")
	if token[1].endswith(';'):
		token[1]=token[1][:-1]
	token[1]=token[1].replace(";","],[")
#	if token[1].startswith("[") and not token[1].endswith("]"):
	if token2[0] not in varList.keys():
		print "\n\tvar %s = %s;" %(token2[0],token[1])
		varList[token2[0]]=token[1]
	else:
		Analyser(token)

print '}'

