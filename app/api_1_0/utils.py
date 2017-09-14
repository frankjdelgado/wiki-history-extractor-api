whitelists = {
	'api.revisions': ['comment','anon','pageid','tags','timestamp','userid','revid','contentformat','contentmodel','extraction_date','parentid','title','_id','size','user','minor'],
	'api.count':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.avg':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.mode':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'api.articles': ['title','ns','first_extraction_date','last_extraction_date','last_revision_extracted'],
	'mode_attributes':['title','user','size','userid','date']
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

def mode_param(request):
	param= request.args.get('attribute')
	if param in whitelists['mode_attributes']:
		return param
	else:
		return None