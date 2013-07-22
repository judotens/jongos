#!/usr/bin/env python

# JONGOS, JSON rasa MONGOS
# better run with pypy or rewrite on v8 / nodejs

import json
import time
import random, string
import hashlib
import lockfile
from operator import itemgetter

class jongos():
  char_set = string.ascii_uppercase + string.digits
  acak = ''.join(random.sample(char_set*6,6))
  storage = "/tmp/" + acak + ".json"
  changes = 0
  status = None
  elapsed = 0
  saveTrigger = 1
  recordType = type(dict())
  last_results = None

  barisan = {}

  def set_status(self, code, msg):
    self.status = {"status": code, "msg": msg, "elapsed": self.elapsed}

  def newID( *args ):
    t = long( time.time() * 1000 )
    r = long( random.random()*100000000000000000L )
    try:
        a = socket.gethostbyname( socket.gethostname() )
    except:
        a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    data = hashlib.md5(data).hexdigest()

    return data

  def _baca_dotted_field(self, item, label):
    ktmp = label.split(".")
    if len(ktmp) > 0:
        k = ktmp[0]
        ktmp.pop(0)
        try: last = item[str(k)]
        except: last = None

        for kt in ktmp:
            try: last = last[str(kt)]
            except: last = None
        k = last
    else: k = label
    return k

  def load(self, dump=None):
    start = time.time()
    if dump != None: self.storage = dump
    try:
        self.barisan = json.loads(open(self.storage).read())
        self.elapsed = time.time() - start
        self.set_status(200, "%s record(s) loaded from %s!" % ( str(len(self.barisan)), self.storage ))

        self.recordType = type(self.barisan)
    except:
        self.barisan = {}
        self.elapsed = time.time() - start
        if dump != None: self.set_status(500, "Cant load %s as storage!" % str(self.storage))

  def refresh(self,io=None):
    self.load(self.storage)

  def insert(self, baris):
    self.refresh()
    if type(self.barisan) == type(list()): return self.insert_list(baris)
    if type(self.barisan) == type(dict()): return self.insert_dict(baris)

  def insert_dict(self, baris):
    start = time.time()

    try: id = baris["id"]
    except: id = self.newID()

    baris["id"] = id

    try: udah_ada = self.barisan[id]
    except: udah_ada = False

    if udah_ada == True:
        self.set_status(500, "Record ID already on database!")
        return False
    else:
        self.barisan[id] = baris

        self.changes = self.changes + 1

        if self.changes >= self.saveTrigger: self.save()
        self.elapsed = time.time() - start
        return True

  def insert_list(self, baris):
    start = time.time()

    try: self.barisan.append(baris)
    except: pass

    self.changes = self.changes + 1

    if self.changes >= self.saveTrigger: self.save()
    self.elapsed = time.time() - start
    return True

  def save(self,target=None):
    if target == None: target = self.storage
    start = time.time()
    try:
        #open(target,"w").write(json.dumps(self.barisan))
        lock = lockfile.FileLock(target, "w+")
        lock.acquire(timeout=10)
        open(target,"w").write(json.dumps(self.barisan))
        #lock.write(json.dumps(self.barisan))
        lock.release()
        self.elapsed = time.time() - start
        self.set_status(200, "Record(s) has been saved into %s!" % str(target))
        next = 0
        return True

    except Exception as err:
        self.elapsed = time.time() - start
        self.set_status(500, "Cant write into %s!" % str(target))
        next = self.changes

    self.changes = next

  def remove(self, q={}):
    start = time.time()
    tmp = self.query(q)
    for i in tmp:
        try: self.barisan.pop(i)
        except: pass

    self.elapsed = time.time() - start

    self.changes = self.changes + 1
    if self.changes >= self.saveTrigger: self.save()
    return True

  def find(self, q={}):
    start = time.time()

    tmp = self.query(q)
    out = []
    for i in tmp:
        #if self.recordType == type(dict()): isi = self.barisan[str(i)]
        try: isi = self.barisan[i]
        except:
            try: isi = self.barisan[str(i)]
            except: isi = {}
        out.append(isi)

    self.elapsed = time.time() - start
    return Query(results=out)

  def update(self, q={},u=None):
    start = time.time()
    if u == None or type(u) != type(dict()): return False
    tmp = self.query(q)

    partial = False
    try:
      c = u['$set']
      partial = True
    except: partial = False
    try: u.pop("id")
    except: pass

    for i in tmp:
        try:
          isi = self.barisan[i]
          if not partial:
            u["id"] = i
            self.barisan[i] = u
          else:
            for b in c:
              self.barisan[i][b] = c[b]

        except: continue

    self.elapsed = time.time() - start
    self.changes = self.changes + 1
    if self.changes >= self.saveTrigger: self.save()


    return True

  def stats(self, q={}):
    start = time.time()
    out = {"records": len(self.barisan), "memory usage": len(json.dumps(self.barisan)) / 1024, "working_file": self.storage}
    self.elapsed = time.time() - start
    return out

  def count(self, q={}):
    start = time.time()
    tmp = self.query(q)
    return len(tmp)

    self.elapsed = time.time() - start

  def query(self, qw={}):
    self.refresh()
    start = time.time()

    tmp = []
    n = 0
    target = self.barisan
    try:
      for item in target:
        if self.recordType == type(dict()): item = target[item]

        terpenuhi = 0
        for k,v in qw.iteritems():
            k = self._baca_dotted_field(item, k)

            if type(v) == type(str()) or type(v) == type(unicode()) or type(v) == type(0) or type(v) == type(bool()) or type(v) == type(None):
                if k == v: terpenuhi = terpenuhi + 1
            if type(v) == type(dict()):
                s_terpenuhi = 0

                for w,x in v.iteritems():
                    
                    if w == '$eq':
                        if k == x: s_terpenuhi = s_terpenuhi + 1
                    if w == '$ne':
                        if k != x: s_terpenuhi = s_terpenuhi + 1

                    if w == '$like':
                        try:
                            if k.lower().find(x.lower()) > -1: s_terpenuhi = s_terpenuhi + 1
                        except: pass

                    if w == '$likes' and type(x) == type(list()):
                        k = k.lower()
                        t_terpenuhi = 0
                        for xt in x:
                            try:
                                if k.find(xt.lower()) > -1: t_terpenuhi = t_terpenuhi + 1
                            except: pass
                        if t_terpenuhi > 0: s_terpenuhi = s_terpenuhi + 1


                    if w == '$likesAnd' and type(x) == type(list()):
                        k = k.lower()
                        t_terpenuhi = 0
                        for xt in x:
                            try:
                                if k.find(xt.lower()) > -1: t_terpenuhi = t_terpenuhi + 1
                            except: pass
                        if t_terpenuhi == len(x): s_terpenuhi = s_terpenuhi + 1


                    if type(x) == type(int()) or type(x) == type(long()):
                        if w == '$gt':
                            if k > x: s_terpenuhi = s_terpenuhi + 1
                        elif w == '$lt':
                            if k < x: s_terpenuhi = s_terpenuhi + 1
                        elif w == '$gte':
                            if k >= x: s_terpenuhi = s_terpenuhi + 1
                        elif w == '$lte':
                            if k <= x: s_terpenuhi = s_terpenuhi + 1

                    if type(x) == type(list()):
                        if w == '$in':
                            t_terpenuhi = 0
                            for xt in x:
                                if k == xt: t_terpenuhi = t_terpenuhi + 1
                            if t_terpenuhi > 0: s_terpenuhi = s_terpenuhi + 1

                        if w == '$nin':
                            t_terpenuhi = 0
                            for xt in x:
                                if k == xt: t_terpenuhi = t_terpenuhi + 1
                            if t_terpenuhi == 0: s_terpenuhi = s_terpenuhi + 1


                        if w == '$all':
                            t_terpenuhi = 0
                            for xt in x:
                                if k == xt: t_terpenuhi = t_terpenuhi + 1
                            if t_terpenuhi == len(x): s_terpenuhi = s_terpenuhi + 1    
                if s_terpenuhi == len(v): terpenuhi = terpenuhi + 1
        if terpenuhi == len(qw):
            if self.recordType == type(dict()): tmp.append(item["id"])
            else: tmp.append(n)
        n = n + 1
    except: tmp = self.query(qw)

    self.elapsed = time.time() - start
    self.set_status(200, "Query %s has been executed" % json.dumps(qw) )

    return tmp

class Query(object): 
  def __init__(self, results):
    self.results = results

  def __iter__(self): return iter(self.results)
  def __getitem__(self): return self.results

  def all(self,fields=None):
    if fields == None: return self.results
    out = []
    for res in self.results:
        ot = {"id": res["id"]}
        for t in fields:
          t = str(t)
          try: r = self._baca_dotted_field(self.results, t)
          except: r = t

          if r != t: ot[t] = r
          else: ot[t] = res[t]
          out.append(ot)

    self.results = out

    return self.results


  def count(self):
    return len(self.results)

  def orderby(self, key=None,reverse=True):
    if type(self.results) == type(list()):
      if key == None: key = "id"
      self.results = sorted(self.results, key=itemgetter(key), reverse=reverse)
    else:
      self.results = sorted(self.results.iteritems(), key=itemgetter(1), reverse=reverse)
    return Query(results=self.results)

  def groupby(self, kunci=None):
    start = time.time()
    if kunci == None: return False

    tmp = self.results

    out = {}
    for i in tmp:
        try: val = i[str(kunci)]
        except: val = "(None)"

        #if val != None and ( type(val) == type(str()) or type(val) == type(unicode()) ):

        val = str(val)
        try: out[val] = out[val] + 1
        except: out[val] = 1

    self.elapsed = time.time() - start
    return Query(results=out)

  def capture(self,target=None):
    if target == None: return False
    start = time.time()
    try:
        open(target,"w").write(json.dumps(self.results))
        return True
    except: return False


if __name__ == '__main__':
    import sys

    tes = jongos()

    try:
      tes.storage = sys.argv[1]
      print ">", "Please wait while load file", tes.storage

      tes.load()
      print tes.status
    except: pass


    import cmd

    class perintah(cmd.Cmd):
      prompt = "jongos> "
      def default(self, line):
        cmd = out = query = None
        mantra = "db."

        if line.lower()[0:len(mantra)] == mantra:
            cmd =  line.lower()[len(mantra):line.lower().find("(")]
            qw = line.lower()[line.lower().find("(")+1:-1]
            if qw == "" or qw == None: qw = "{}"

            #print ">", cmd, qw

        try: query = json.loads(qw)
        except:
            query = None
            try: print ">", "Your query", qw, "is broken"
            except: pass

        if cmd != None and query != None:
            try:
                try: out = getattr(tes, cmd)(query)
                except: ">", "ERROR:", query

                tes.last_results = out

                try: total = len(out)
                except: total = 1

                if total > 20:
                    try:
                        out = out[0:20]
                        for w in out: print w
                        out = None

                    except:
                        n = 0
                        for w in sorted(out,key=out.get,reverse=True):
                            if n < 20:
                                print {w:out[w]}
                                n = n + 1
                        out = None
                
                if (out != None): print ">", out
                print ">", total, "row(s) matches in", tes.elapsed, "second(s)"
            except: print ">", "Unknown command"


      def do_exit(self, line):
            "> Exit"
            return True

    perintah().cmdloop('> Enter your command:')
