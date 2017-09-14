whitelists = {
	'api.revisions': ['comment','anon','pageid','tags','timestamp','userid','revid','contentformat','contentmodel','extraction_date','parentid','title','_id','size','user','minor'],
	'filter_attributes':['title','pageid','user','userid','tag','size','sizematch','date','datestart','dateend'],
	'mode_attributes':['title','user','size','userid','date']
}

param_type = {
	'pageid': 'int',
	'userid': 'int',
	'revid': 'int',
	'size': 'int',
	'sizematch':'int',
	'userid': 'int'
}

def filter_params(request,whitelist_category=None):
	if whitelist_category==None:
		whitelist_category= request.url_rule.endpoint

	result = {}

	for param in whitelists[whitelist_category]:
		#print(param)
		if request.args.get(param) != None:
			if param in param_type and param_type[param] == 'int':
				result[param] = request.args.get(param, None, int)
			else:
				result[param] = request.args.get(param)

	return result

def mode_param(request):
	result = None
	for param in whitelists['mode_attributes']:
		#print(param)
		if request.args.get('attribute') == param:
			result = param
			break
	return result