import datetime
from config import config, Config
from itertools import chain

class QueryHandler(object):
    
    data={}

    def __init__(self, pageid=None , db=None):
        self.db = db

    def filter_by_size(self,values):
        #values is a list composed by 2 values, the size to filter by, and the order of filtering
        # when the order is greater than 0, it will return the revisions which size are greater than the argument
        # when the order is lesser than 0, it will return the revisions which size are lesser than the argument
        # if the order is 0, it will return the revisions which size are exactly as the argument
        if values[1] > 0:
            data={'size': {'$gt': int(values[0])} }
        elif values[1] < 0:
            data={'size': {'$lt': int(values[0])} }
        else:
            data={'size':int(values[0]) }
        return data


    def filter_by_date(self,values,name='timestamp'):
        date_format = '%Y-%m-%d'
        #values is a list composed by 1 or 2 values: 
        # date arguments must be in format: YYYY-MM-DD
        # 1 value: one date. It will return the revisions made that date.
        # 2 values: two dates. It will return the revisions made between those dates, inclusive
        # 2 values: one date and one integer. 
        # If the integer is -1: It will return the revisions made from the first revision until the date given as argument.
        # If the integer is 1: It will return the revisions made from the date given as argument until the last revision.
        # the strptime convert the string arguments into datetime datatype
        if len(values) == 1:
            date_i=datetime.datetime.strptime(values[0],date_format)
            #it is used 2 dates to extract the revision for the whole day, from 0:0 to 23:59
            date_f=date_i.replace(hour=23,minute=59,second=59)
            data={name: {'$gte':date_i , '$lte':date_f} }
            return data
        elif len(values) == 2:
            #if the second argument is a date:
            if values[1] != 1 and values[1] != -1 :
                date_i=datetime.datetime.strptime(values[0],date_format)
                date_f=datetime.datetime.strptime(values[1],date_format)
                #the date values are adjusted to take into account the day until 23:59
                date_f=date_f.replace(hour=23,minute=59,second=59)
                data={name: {'$gte':date_i , '$lte':date_f} }
                return data
            else:
                if values[1] == 1:
                    date=datetime.datetime.strptime(values[0],date_format)
                    data={name: {'$gte':date} }
                    return data
                else:
                    date=datetime.datetime.strptime(values[0],date_format)
                    #the date values are adjusted to take into account the day until 23:59
                    date=date.replace(hour=23,minute=59,second=59)
                    data={name: {'$lte':date} }
                    return data


    def filter_by(self,arguments):
        query={}
        option=False
        dateDone=False
        sizeDone=False
        for key,value in arguments.items():
            option=True
            #check if the argument is date(to apply the date filter)
            if key in ('date','datestart','dateend'):
                if dateDone == False :
                    dateDone = True
                    if key == 'date':
                        query.update(self.filter_by_date([value]))
                    elif key == 'datestart':
                        if 'dateend' in arguments:
                            query.update(self.filter_by_date([value,arguments.get('dateend')]))
                        else:
                            query.update(self.filter_by_date([value,1]))
                    elif key == 'dateend':
                        if 'datestart' in arguments:
                            query.update(self.filter_by_date([arguments.get('datestart'),value]))
                        else:
                            query.update(self.filter_by_date([value,-1]))

            #check if the argument is size(to apply the size filter)
            elif key in ('size','sizematch'):
                if sizeDone==False:
                    sizeDone=True
                    if key == 'size':
                        if 'sizematch' in arguments:
                            query.update(self.filter_by_size([value,arguments.get('sizematch',None, int)]))
                        else:
                            query.update(self.filter_by_size([value,0]))
                    else:
                        if 'size' in arguments:
                            query.update(self.filter_by_size([ arguments.get('size') , value]))

            elif key in ('first_extraction_date','last_extraction_date'):
                query.update(self.filter_by_date([value],key))

            else:
                query.update({ key : value })

        if option==False:
            print 'Wrong Filter Option'
            return ''
        else:
            return query
        
    def get_count(self,arguments):
        data=self.filter_by(arguments)
        if data!='':
            return self.db.count(data)
        else:
            return None

    #1 for user,2 for tag, 3 for size
    #besides the values required to filter(eg: username for user filtering, size and order for size filtering), it requires 2 values, as with date filtering for 2 dates-interval
    def get_avg(self,values):
        #arguments=values.copy()
        # the filter to set avg is converted in a code with date filtering included
        data=self.filter_by(values)
        date_format = '%Y-%m-%d'
        #the dates are extracted and are calculated the number of days with the .days function (datetime.timedelta library)
        date_i=datetime.datetime.strptime(values.get('datestart'),date_format)
        date_f=datetime.datetime.strptime(values.get('dateend'),date_format)
        days=(date_f-date_i).days +1
        if data!='':
            res= self.db.count(data)
            return res/(days*1.0)


    #function that gets the mode(moda) for an attribute, for now it works with users, size and date, because tags are mostly empty
    #Besides, it supports filter values, to make detailed measures.
    def get_mode(self,values,mode_attribute,per_page=1000):
        data=''
        attribute=mode_attribute
        #it is made the match of the revision, filtering by attributes
        data=self.filter_by(values)
        #then it is created the projection for the query
        projection={'_id':0}
        if attribute == 'date':
            attribute= 'timestamp'
        projection.update({attribute:1})

        #first, we calculate how many revisions will be extracted, to extract them in chunks of 1000
        n_revisions=self.db.count(data)
        total=1+ n_revisions/per_page
        revisions=[]
        #now, the revisions are extracted in chunks, and saved in a cursor
        for page in xrange(1, total+1):
            aux=self.db.paginate_for_query(data,projection,page,per_page)
            #the cursor is concatenated with the revisions cursor
            revisions=[x for x in chain(revisions, aux)]
        valueslist=[]
        repetitionslist=[]
        #after collect the projected revisions, it is checked which values appears most,
        #adding them to a list, and keeping track of their appearances on another list
        if attribute=='timestamp':
            date_format = '%Y-%m-%d'
            for rev in revisions:
                date= rev[attribute].strftime(date_format)
                if not (date in valueslist) :
                    valueslist.append(date)
                    repetitionslist.append(1)
                else:
                    position= valueslist.index(date)
                    repetitionslist[position]=repetitionslist[position]+1
        else:            
            for rev in revisions:
                if not (rev[attribute] in valueslist) :
                    valueslist.append(rev[attribute])
                    repetitionslist.append(1)
                else:
                    position= valueslist.index(rev[attribute])
                    repetitionslist[position]=repetitionslist[position]+1
        
        # it is calculated the value most repeated
        if len(repetitionslist)>0:
            maxi=max(repetitionslist)
            mode=[]
            i=0
            #it is created a list with all values tied as mode
            for r in repetitionslist:
                if r==maxi:
                    if isinstance(valueslist[i],unicode) :
                    #in case of string, it is converted from unicode
                        mode.append(str(valueslist[i]))
                    else:
                        mode.append(valueslist[i])
                i=i+1
            return mode
        else:
            print 'No revisions found'
            return []

    def get_articles_query(self,arguments):
        data=self.filter_by(arguments)
        if data!='':
            return data
        else:
            return {}
