import json,os,threading,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
events=[]
lock=threading.Lock()
boot=str(uuid.uuid4())
class Handler(BaseHTTPRequestHandler):
    def reply(self,data):
        raw=json.dumps(data,ensure_ascii=True).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        with lock: snapshot=list(events)
        self.reply({"version":"ui-audit-v2","bootId":boot,"events":snapshot})
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get("Content-Length","0")))
        try: data=json.loads(raw)
        except Exception: data={"invalidJSON":True}
        if not isinstance(data,dict):data={"unexpectedBodyType":type(data).__name__}
        allowed={"type","detail","trigger","bucket","key","size","etag","time"}
        event={"path":self.path,"body":{k:v for k,v in data.items() if k in allowed},
               "unexpectedFields":sorted(set(data)-allowed),
               "headers":{k:self.headers.get(k) for k in ("ce-type","ce-source","ce-subject","ce-id","ce-specversion","content-type")}}
        with lock:
            events.append(event)
            del events[:-256]
        print("S3_AUDIT_EVENT "+json.dumps(event,ensure_ascii=True),flush=True)
        self.reply({"accepted":True})
ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","8080"))),Handler).serve_forever()
