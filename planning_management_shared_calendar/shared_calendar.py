# -*- coding: utf8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
from openerp.osv import fields, osv, expression
from datetime import datetime, timedelta
import time

## This class contains the shared calendar object and the copy of external object 
#
#
class shared_calendar(osv.osv):
    _name = "shared.calendar"
    _description = "Shared Calendar"

    _columns = {
        'name' : fields.char('Name', size=50, required=True),
        'description' : fields.text('Description'),
        'responsible' : fields.many2one('res.users','Responsible'),
        'startingdate' : fields.datetime('Starting Date', required=True),
        'endingdate':fields.datetime('Ending Date'),
        'duration':fields.float('Duration'),
        'type':fields.char('Type', size = 50, readonly=True),
        'id':fields.integer('ID'),
        'object_id': fields.integer('Original id'),
        'mod':fields.char('Model',size = 50),
        'resp_name' : fields.char('Name responsible', size=50, readonly=True),
        'location' : fields.char('Location', size=50, readonly=True),
        'attendee' : fields.char('Attendee', size=50, readonly=True),
        'mail' : fields.char('Mail', size=50, readonly=True),
    }
      
    _defaults = {
        'startingdate': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'Shared calendar',
        'mod': 'shared.calendar',
        'responsible' : lambda obj, cr, uid, context: uid,
    }
    
    def write_on_original(self,cr,uid,ids,vals,type,idobj,conf_rec,context=None):
        if vals.get('name') and conf_rec[0].name.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].name.name: vals.get('name')}, context=None)  
        if vals.get('description') and conf_rec[0].description.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].description.name: vals.get('description')}, context=None)
        if vals.get('responsible') and conf_rec[0].responsible.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].responsible.name: vals.get('responsible')}, context=None) 
        if vals.get('startingdate') and conf_rec[0].startingdate.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].startingdate.name: vals.get('startingdate')}, context=None) 
        if vals.get('endingdate') and conf_rec[0].endingdate.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].endingdate.name: vals.get('endingdate')}, context=None) 
        if vals.get('duration') and conf_rec[0].duration.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].duration.name: vals.get('duration')}, context=None)
        if vals.get('location') and conf_rec[0].location.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].location.name: vals.get('location')}, context=None) 
        if vals.get('attendee') and conf_rec[0].attendee.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].attendee.name: vals.get('attendee')}, context=None)    
        if vals.get('mail') and conf_rec[0].mail.name:
            self.pool.get(type).write(cr, uid , idobj,{conf_rec[0].mail.name: vals.get('mail')}, context=None)
        return True
    
    ## Surcharge write method for save data in original object
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def write(self, cr, uid, ids, vals, context=None):
        if 'update' not in context:
            obj=self.browse(cr, uid, ids[0], context=context)
            conf_obj = self.pool.get('shared.calendar.conf.information')
            conf_ids = conf_obj.search(cr,uid,[('object','=',obj.type)])
            conf_rec = conf_obj.browse(cr, uid, conf_ids)
            o_obj = self.pool.get(obj.type)
            o_ids = o_obj.search(cr,uid,[])
            o_rec = o_obj.browse(cr, uid, o_ids)
            for objor in o_rec:
                if objor.id == obj.object_id:
                    if 'state' in objor:
                        if objor.state != 'done': 
                            self.write_on_original(cr,uid,ids,vals,obj.type,objor.id,conf_rec,context)
                    if 'stage_id' in objor:
                        if objor.stage_id.name != 'done':
                            self.write_on_original(cr,uid,ids,vals,obj.type,objor.id,conf_rec,context)
        return super(shared_calendar,self).write(cr, uid, ids, vals, context=context)    
   
    ## Method to check the original object 
    #  @param self The object pointer.  
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #  method to check the original object      
    def check_original_object(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)
        idobj = obj.object_id
         
        return {
            'name':'Edit original object',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': None,
            'res_model': obj.type,
            'res_id': idobj,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'context':context,
        }
shared_calendar()

## This class contains the configuration information
#
#
class shared_calendar_conf(osv.osv):
    _name = "shared.calendar.conf"
    _description = "Capacity Planning" 
    
    ## Call of button configuration
    #  @param self The object pointer.
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def check_update_calendar(self, cr, uid ,ids, context=None):
        self.pool.get('shared.calendar.conf').check_cron(cr, uid, 'shared.calendar.conf')      
        return True  
    
    _columns = {   
        'id':fields.integer('ID'),
        'name':fields.char('Name',size=30, required=True,help="The name of the configuration."),
        'conf_info':fields.one2many('shared.calendar.conf.information', 'conf_id', 'conf info'),
        'cron':fields.many2one('ir.cron','Cron', required=True, ondelete='cascade'),
        'periode_start':fields.integer('Before'),
        'periode_end':fields.integer('After'),
    }
    
    _defaults = {
        'periode_start': 1,
        'periode_end': 3,
    }
    
    ## Method for update the shared calendar with new object
    #  @param self The object pointer.    
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param context The optional dictionary of contextual parameters such as user language
    #   
    def check_cron(self, cr, uid, context=None):
        calendar_conf_obj = self.pool.get('shared.calendar.conf.information')
        calendar_conf_ids = calendar_conf_obj.search(cr,uid,[('object','!=',None)])
        calendar_conf_rec = calendar_conf_obj.browse(cr,uid,calendar_conf_ids)      
        
        calendar_obj = self.pool.get('shared.calendar')
        context={
            'update': True,
        }
        #delete
        calendar_ids = calendar_obj.search(cr,uid,[])
        calendar_rec=calendar_obj.browse(cr,uid,calendar_ids)
        ids_temp=[]
        for c in calendar_rec:
            tmp=False
            for ccr in calendar_conf_rec:
                if c.type == ccr.object.model:
                    tmp=True
            if not tmp:
                ids_temp.append(c.id)
        self.pool.get('shared.calendar').unlink(cr,uid,ids_temp)
        
        #calculation period to synchronize
        conf_obj = self.pool.get('shared.calendar.conf')
        conf_ids = conf_obj.search(cr,uid,[])
        conf_rec = conf_obj.browse(cr,uid,conf_ids)
        periode_bef=False
        periode_after=False
        for c in conf_rec:
            periode_bef=c.periode_start
            periode_after=c.periode_end
            
        date_now = datetime.now()
        before_month=date_now.month - periode_bef
        month=date_now.month
        
        if before_month <= 0:
            before_month=month
            while periode_bef != 0:
                before_month=before_month-1
                if before_month==0:
                    before_month=12
                periode_bef=periode_bef-1
            date_before = date_now.replace(month=before_month,year=date_now.year-1,day=15)
        else:    
            date_before = date_now.replace(month=before_month,day=15)
  
        after_month=date_now.month + periode_after
        month=date_now.month
        if after_month >= 12:
            after_month=month
            while periode_after != 0:
                after_month=after_month+1
                if after_month==13:
                    after_month=1
                periode_after=periode_after-1
            date_after = date_now.replace(month=after_month,year=date_now.year+1,day=15)
        else:    
            date_after = date_now.replace(month=after_month,day=15)
           
        for c in calendar_conf_rec:
            o_obj = self.pool.get(c.object.model)
            o_ids = o_obj.search(cr,uid,[(str(c.startingdate.name),'>=',date_before.strftime('%Y-%m-%d %H:%M:%S')),(str(c.startingdate.name),'<=',date_after.strftime('%Y-%m-%d %H:%M:%S'))])
            o_rec = o_obj.browse(cr, uid, o_ids)
            
            for o in o_rec:                
                results=self.pool.get(c.object.model).read(cr,uid,o.id,[c.name.name,c.description.name,c.responsible.name,c.startingdate.name,c.endingdate.name,c.duration.name,c.location.name,c.attendee.name,c.mail.name])
                if "-" in str(o.id):
                    tmp=str(o.id).split('-')
                    id=tmp[0]
                else:
                    id=o.id
                id_temp=self.pool.get('shared.calendar').search(cr,uid,[('object_id','=',id),('type','=',c.object.model)])
                if id_temp:
                    try:
                        resp_tmp=results[c.responsible.name][0]
                    except:
                        resp_tmp=None
                    if c.name.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'name': results[c.name.name] or ''}, context) 
                        except:
                            print "Error update name"                  
                    if c.description.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'description': results[c.description.name]}, context)
                        except:
                            print "Error update description" 
                    if c.responsible.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'responsible': resp_tmp}, context)
                        except:
                            print "Error update responsible"  
                    if c.startingdate.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'startingdate':results[c.startingdate.name]}, context)
                        except:
                            print "Error update start date"   
                    if c.endingdate.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'endingdate':results[c.endingdate.name]}, context)
                        except:
                            print "Error update end date"  
                    if c.duration.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'duration':results[c.duration.name]}, context)
                        except:
                            print "Error update duration" 
                    if c.location.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'location':results[c.location.name]}, context)
                        except:
                            print "Error update location"  
                    if c.attendee.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'attendee':results[c.attendee.name]}, context)
                        except:
                            print "Error update attendee"    
                    if c.mail.name:
                        try:
                            self.pool.get('shared.calendar').write(cr, uid , id_temp,{'mail':results[c.mail.name]}, context)
                        except:
                            print "Error update email" 
                else:
                    try:
                        resp_tmp=results[c.responsible.name][0]
                    except:
                        resp_tmp=None
                    i=self.pool.get('shared.calendar').create(cr, uid ,{'name': results[c.name.name] or '','startingdate':results[c.startingdate.name],'responsible': resp_tmp,'object_id':id,'type':c.object.model}, context=None)
                    '''if c.description.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'description': results[c.description.name]}, context=None)
                    if c.responsible.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'responsible': results[c.responsible.name][0]}, context=None)  
                    if c.endingdate.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'endingdate':results[c.endingdate.name]}, context=None) 
                    if c.duration.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'duration':results[c.duration.name]}, context=None)
                    if c.location.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'location':results[c.location.name]}, context=None) 
                    if c.attendee.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'attendee':results[c.attendee.name]}, context=None)   
                    if c.mail.name:
                        self.pool.get('shared.calendar').write(cr, uid , i,{'mail':results[c.mail.name]}, context=None)'''    
              
        return True
    
    ## Method for clean the shared calendar  
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def clean_shared_calendar(self, cr, uid, ids, context=None):       
        #clean obect of share calendar except object of type shared calendar
        calendar_obj = self.pool.get('shared.calendar')
        calendar_ids = calendar_obj.search(cr,uid,[('type','!=', 'shared calendar')])
        calendar_obj.unlink(cr,uid,calendar_ids)
        
        return True
    
    ## Method for clean the configuration of shared calendar  
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #    
    def clean_shared_calendar_conf(self, cr, uid, ids, context=None):
        #drop the configuration
        calendar_obj = self.pool.get('shared.calendar.conf.information')
        calendar_ids = calendar_obj.search(cr,uid,[])
        calendar_obj.unlink(cr,uid,calendar_ids)       

        return True 
    
    ## Surcharge of unlink method for delete information configuration when the configuration is delete
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param delall optional parameter
    #  
    def unlink(self, cr, uid, ids,delall = None, *args, **kwargs):
        o_obj = self.pool.get('shared.calendar.conf.information')
        o_ids = o_obj.search(cr,uid,[])
        o_obj.unlink(cr,uid,o_ids) 
        
        return super(shared_calendar_conf,self).unlink(cr, uid, ids,*args, **kwargs) 

    ## Surcharge of create method to verify existence of the configuration
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #   
    def create(self, cr, uid, vals, context=None):
        obj_ids=self.pool.get('shared.calendar.conf').search(cr,uid,[])  
        if obj_ids:
            raise osv.except_osv('Error !','The configuration already exists.')
        
        return super(shared_calendar_conf, self).create(cr, uid, vals, context=context)
    
shared_calendar_conf()

## This class contains different types objects that will be synchronize in the calendar  
#
#  
class shared_calendar_conf_information(osv.osv):
    _name = "shared.calendar.conf.information"
    _description = "Information"
    
    _columns = {
        'conf_id': fields.many2one('shared.calendar.conf', 'Configuration',ondelete='cascade', readonly=True, invisible=True),
        'object': fields.many2one('ir.model','Object',required=True),
        'name': fields.many2one('ir.model.fields','Name', domain="['&',('ttype', '=', 'char'),('model_id','=',object)]",required=True),
        'description': fields.many2one('ir.model.fields','Description', domain="['&',('ttype', '=', ['char','text']),('model_id','=',object)]"),
        'responsible': fields.many2one('ir.model.fields','Responsible', domain="['&',('ttype', '=', 'many2one'),('model_id','=',object)]"),
        'startingdate': fields.many2one('ir.model.fields','Start date', required=True, domain="['&',('ttype', '=', 'datetime'),('model_id','=',object)]"),
        'endingdate': fields.many2one('ir.model.fields','End date', domain="['&',('ttype', '=', 'datetime'),('model_id','=',object)]"),
        'duration': fields.many2one('ir.model.fields','Duration', domain="['&',('ttype', '=', 'float'),('model_id','=',object)]"),
        'location': fields.many2one('ir.model.fields','Location', domain="['&',('ttype', '=', 'char'),('model_id','=',object)]"),
        'attendee': fields.many2one('ir.model.fields','Attendee', domain="['&',('ttype', '=', 'char'),('model_id','=',object)]"),
        'mail': fields.many2one('ir.model.fields','Mail', domain="['&',('ttype', '=', 'char'),('model_id','=',object)]"),
    }
    
    def on_change_object(self, cr, uid, ids, object_id, context=None):
        if not object_id:
            return False      
        obj = self.pool.get('ir.model').browse(cr, uid, object_id, context=context).model
        name_tmp=None
        responsible_tmp=None
        description_tmp=None
        start_date_tmp=None
        end_date_tmp=None
        location_tmp=None
        attendee_tmp=None
        mail_tmp=None
        duration_tmp=None
        #name
        ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","name")])
        if ids_field:
            name_tmp = ids_field[0]
        #reponsible
        ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","user_id")])
        if ids_field:
            responsible_tmp = ids_field[0] 
        #description
        ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","description")])
        if ids_field:    
            description_tmp = ids_field[0] 
        #start date
        if obj == "project.task":
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","date_start")])
            if ids_field:    
                start_date_tmp = ids_field[0]
            #end date
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","date_end")])
            if ids_field:    
                end_date_tmp = ids_field[0]
        elif obj in ("project.issue","crm.case.stage"):
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","create_date")])
            if ids_field:    
                start_date_tmp = ids_field[0]
        elif obj == "hr.holidays":        
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","date_from")])
            if ids_field:    
                start_date_tmp = ids_field[0]
            #end date
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","date_to")])
            if ids_field:    
                end_date_tmp = ids_field[0]                
        else:
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","date")])
            if ids_field:    
                start_date_tmp = ids_field[0]
        #location
        if obj == "calendar.event":
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","location")])
            if ids_field:    
                location_tmp = ids_field[0]      
            #date
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","start_datetime")])
            if ids_field:    
                start_date_tmp = ids_field[0]  
        #attendee
        
        #mail
        if obj == "calendar.event":
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","email_from")])
            if ids_field:    
                mail_tmp = ids_field[0]          
        #duration
        if obj in ("calendar.event","crm.phonecall"):
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","duration")])
            if ids_field:    
                duration_tmp = ids_field[0]
        elif obj == "project.task":
            ids_field = self.pool.get('ir.model.fields').search(cr, uid, [("model","=",obj),("name","=","planned_hours")])
            if ids_field:
                duration_tmp = ids_field[0]        
        
        values = {
            'name': name_tmp,
            'responsible': responsible_tmp,
            'description': description_tmp,
            'startingdate': start_date_tmp,
            'endinddate': end_date_tmp,
            'location': location_tmp,
            'mail': mail_tmp,
            'duration': duration_tmp,
        }
        
        return {'value' : values}

shared_calendar_conf_information()
