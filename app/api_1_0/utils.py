whitelists = {
	'api.revisions': ['comment','anon','pageid','tags','timestamp','userid','revid','contentformat','contentmodel','extraction_date','parentid','title','_id','size','user','minor'],
	'api.count':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.avg':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.mode':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.articles': ['title','ns','first_extraction_date','last_extraction_date','last_revision_extracted'],
	'mode_attributes':['title','pageid' ,'user','userid','size','userid','date']
}

param_type = {
	'pageid': 'int',
	'userid': 'int',
	'revid': 'int',
	'size': 'int',
	'sizematch':'int',
	'userid': 'int',
	'ns': 'int'
}

#This function will use the whitelist based on the name of the enpoint, and compare 
#the parameters included in the request with it. The function will return a dictionary containing
#the arguments and values that belong to the request and are whitelisted
def filter_params(request):
	result = {}

	for param in whitelists[request.url_rule.endpoint]:
		#print(param)
		if request.args.get(param) != None:
			if param in param_type and param_type[param] == 'int':
				result[param] = request.args.get(param, None, int)
			else:
				result[param] = request.args.get(param)

	return result

#This function will use the whitelist mode_attribute and compare the attribute parameter of the request 
#The function will return the name of the attribute in case is whitelisted, or None otherwise.
def mode_param(request):
	param= request.args.get('attribute')
	if param in whitelists['mode_attributes']:
		return param
	else:
		return None