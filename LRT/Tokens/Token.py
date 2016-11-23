import sys
import os
import ConfigParser
import pdb
import itertools

if 'couchdb' not in sys.modules:
    import couchdb
from couchdb.design import ViewDefinition


class Token_Handler:
    def __init__(self, t_type="token", srv="https://picas-lofar.grid.sara.nl:6984", uname="", pwd="", dbn=""):
        self.t_type = t_type
        self.Picas_User = uname
        self.Picas_DB = dbn
        self.Picas_Passwd = pwd
        self.server = srv
        self.db = self.get_db(self.Picas_User, self.Picas_Passwd, self.Picas_DB, self.server)
        self.views = {}
        self.tokens = {}

    def get_db(self, uname, pwd, dbn, srv):
        """Logs into the Couchdb server and returns the database requested
        """
        server = couchdb.Server(srv)
        server.resource.credentials = (uname, pwd)
        db = server[dbn]
        return db

    def create_token(self, keys={}, append="", attach=[]):
        '''Creates a token, appends string to token ID if requested and adds
            user requested keys through the dict keys{}
            ie t1.create_token(keys = {"OBSID":"L123458","freq_res":4,"time_res":4,},append="L123458")
            attach is [file_handle,"name of attachment"]
        '''
        default_keys = {
            '_id': 't_'+self.t_type+"_",
            'type': self.t_type,
            'lock': 0,
            'done': 0,
            'hostname': '',
            'scrub_count': 0,
            'output': ""
        }
        keys = dict(itertools.chain(keys.iteritems(), default_keys.iteritems()))
        self.append_id(keys, append)
        self.tokens[keys["_id"]] = keys
        self.db.update([keys])
        if attach:
            self.add_attachment(keys['_id'], attach[0], attach[1])
        return keys['_id']  # returns the token ID

    def append_id(self, keys, app=""):
        keys["_id"] += app

    def get_views(self):
        """Helper function to get the current views on the database
        """
        db_views = self.db.get("_design/"+self.t_type)
        self.views = db_views["views"]

    def delete_tokens(self, view_name="test_view", key=["", ""]):
        """Deletes tokens from view view_name
            exits if the view doesn't exist
            User can select which tokens within the view to delete
            t1.delete_tokens("todo",["OBSID","L123456"])
            t1.delete_tokens("error")
        """
        v = self.list_tokens_from_view(view_name)
        for x in v:
            document = self.db[x['key']]
            if key[0] == "":
                pass
            else:
                if not document[key[0]] == key[1]:
                    continue
            print "Deleting Token "+x['id']
            self.db.delete(document)
        #    self.tokens.pop(x['id'])
        # TODO:Pop tokens from self

    def add_view(self, v_name="test_view", cond='doc.lock > 0 && doc.done > 0 && doc.output < 0 '):
        """Adds a view to the db, needs a view name and a condition. Emits all tokens with
            the type of the current Token_Handler
        """
        generalViewCode = '''
        function(doc) {
           if(doc.type == "%s") {
            if(%s) {
              emit(doc._id, doc._id);
            }
          }
        }
        '''
        view = ViewDefinition(self.t_type, v_name, generalViewCode % (self.t_type, cond))
        self.views[v_name] = view
        view.sync(self.db)

    def add_overview_view(self):
        overviewMapCode = '''
function(doc) {
   if(doc.type == "%s") {
       if (doc.lock == 0 && doc.done == 0){
          emit('todo', 1);
       }
       if(doc.lock > 0 && doc.status=='downloading') {
          emit('downloading', 1);
       }
       if(doc.lock > 0 && doc.status=='done') {
          emit('done', 1);
       }
       if(doc.lock > 0 && doc.status=='error') {
          emit('error', 1);
       }
       if(doc.lock > 0 && doc.status=='launched') {
          emit('waiting', 1);
       }
       if(doc.lock > 0 && "starting_generic_pipeline" in doc.times && doc.status!='done' && doc.status!='error' && doc.status!='downloading' ) {
          emit('running', 1);
       }
   }
}
'''
        overviewReduceCode = '''
function (key, values, rereduce) {
   return sum(values);
}
'''
        overview_total_view = ViewDefinition(self.t_type, 'overview_total',
                                             overviewMapCode % (self.t_type),
                                             overviewReduceCode)
        self.views['overview_total'] = overview_total_view
        overview_total_view.sync(self.db)

    def del_view(self, v_name="test_view"):
        '''Deletes the view with view name from the _design/${token_type} document
            and from the token_Handler's dict of views
        '''
        db_views = self.db.get("_design/"+self.t_type)
        db_views["views"].pop(v_name, None)
        self.views.pop(v_name, None)
        self.db.update([db_views])

    def remove_Error(self):
        '''Removes all tokens in the error view
        '''
        cond = "doc.lock > 0 && doc.done > 0 && doc.output > 0"
        self.add_view(v_name="error", cond=cond)
        self.delete_token("error")

    def reset_tokens(self, view_name="test_view", key=["", ""], del_attach=False):
        """ resets all tokens in a view, optionally can reset all tokens in a view
            who have key-value pairs matched by key[0],key[1]
            t1.reset_token("error")
            t1.reset_token("error",key=["OBSID","L123456"])
            t1.reset_token("error",key=["scrub_count",6])
        """
        v = self.list_tokens_from_view(view_name)
        to_update = []
        for x in v:
            document = self.db[x['key']]

            if key[0] != "" and document[key[0]] != key[1]:  # make it not just equal
                continue
            try:
                document['status'] = 'todo'
            except KeyError:
                pass
            document['lock'] = 0
            document['done'] = 0
            document['scrub_count'] += 1
            document['hostname'] = ''
            document['output'] = ''
            if del_attach:
                    if "_attachments" in document:
                        del document["_attachments"]
            to_update.append(document)
        self.db.update(to_update)
        return (to_update)

    def add_attachment(self, token, filehandle, filename="test"):
        self.db.put_attachment(self.db[token], filehandle, filename)

    def list_attachments(self, token):
        return self.db[token]["_attachments"].keys()

    def get_attachment(self, token, filename, savename=None):
        try:
            attach = self.db.get_attachment(token, filename).read()
        except AttributeError:
            print "error getting attachment"
            return ""
        if "/" in filename:
            savename = filename.replace("/", "_")
        if not savename:
            savename = filename
        with open(savename, 'w') as f:
            for line in attach:
                f.write(line)
        return os.path.abspath(filename)

    def list_tokens_from_view(self, view_name):
        self.get_views()
        if view_name in self.views:
            view = self.views[view_name]
        else:
            print "View Named "+view_name+" Doesn't exist"
            return
        v = self.db.view(self.t_type+"/"+view_name)
        return v

    def set_view_to_status(self, view, status):
        """Sets the status to all tokens in 'view' to 'status
            eg. Set all locked tokens to error or all error tokens to todo
        """
        v = self.list_tokens_from_view(view)
        to_update = []
        for x in v:
            document = self.db[x['key']]
            document['status'] = str(status)
            document['lock'] = 1
            to_update.append(document)
        self.db.update(to_update)


class View(object):
    def __init__(self, t_type='test', srv="https://picas-lofar.grid.sara.nl:6984", uname="", pwd="", dbn="", name="test_view"):
        self.name = name
        self.t_type = t_type
        self.Picas_User = uname
        self.Picas_DB = dbn
        self.Picas_Passwd = pwd
        self.server = srv
        self.db = self.get_db(self.Picas_User, self.Picas_Passwd, self.Picas_DB, self.server)
        self.condition = "doc.lock==0"
        self.emit = "doc._id"

    def get_db(self, uname, pwd, dbn, srv):
        """Logs into the Couchdb server and returns the database requested
        """
        server = couchdb.Server(srv)
        server.resource.credentials = (uname, pwd)
        db = server[dbn]
        return db

    def set_condition(self, condition):
        self.condition = condition

    def set_emit(self, emit):
        self.emit = emit

    def build_Map_Code(self, mapcode=""):
        if mapcode == "":
            mapcode = '''function(doc) {
   if(doc.type == "%s") {
       if (doc.lock == 0 && doc.done == 0){
          emit('todo', 1);
       }
       if(doc.lock > 0 && doc.status=='downloading') {
          emit('downloading', 1);
       }
       if(doc.lock > 0 && doc.status=='done') {
          emit('done', 1);
       }
       if(doc.lock > 0 && doc.status=='error') {
          emit('error', 1);
       }
       if(doc.lock > 0 && doc.status=='launched') {
          emit('waiting', 1);
       }
       if(doc.lock > 0 && "launched" in doc.times && doc.status!='done' && doc.status!='error' && doc.status!='downloading' ) {
          emit('running', 1);
       }
   }
}'''
        self.mapcode = str(mapcode % (self.t_type))

    def build_reduce_code(self, reduce_code=""):
        self.reducecode = reduce_code
