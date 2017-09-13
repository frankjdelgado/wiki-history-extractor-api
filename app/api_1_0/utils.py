whitelists = {
	'api.revisions': ['comment','anon','pageid','tags','timestamp','userid','revid','contentformat','contentmodel','extraction_date','parentid','title','_id','size','user','minor'],
	'api.articles': ['title','ns','first_extraction_date','last_extraction_date','last_revision_extracted']
}

param_type = {
	'pageid': 'int',
	'userid': 'int',
	'revid': 'int',
	'size': 'int',
	'userid': 'int',
	'ns': 'int'
}

def filter_params(request):
	result = {}

	for param in whitelists[request.url_rule.endpoint]:
		print(param)
		if request.args.get(param) != None:
			if param in param_type and param_type[param] == 'int':
				result[param] = request.args.get(param, None, int)
			else:
				result[param] = request.args.get(param)

	return result