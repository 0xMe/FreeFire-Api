import requests, random, hashlib, hmac, json
from urllib.parse import urlencode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def register(region):
    s = b'2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3'
    cid = "100067"
    ua = "GarenaMSDK/4.0.19P9(SM-S908E; Android 11; en; IN)"
    session = requests.Session()
    def e(x):
        k = [0,0,0,2,0,1,7,0,0,0,0,0,2,0,1,7,0,0,0,0,0,2,0,1,7,0,0,0,0,0,2,0]
        return bytes(b ^ k[i % len(k)] ^ 48 for i, b in enumerate(x.encode()))
    
    def aes(h):
        c = AES.new(b"Yg&tc%DEuh6%Zc^8", AES.MODE_CBC, b"6oyZDr22E3ychjM%")
        return c.encrypt(pad(bytes.fromhex(h),16)).hex()
    
    def ev(n):
        r = bytearray()
        while n:
            b = n & 0x7F
            n >>= 7
            r.append(b | (0x80 if n else 0))
        return bytes(r)
    
    def ef(f,v):
        if type(v) == int: return ev((f<<3)|0)+ev(v)
        b = v.encode() if type(v)==str else v
        return ev((f<<3)|2)+ev(len(b))+b
    
    def ep(d):
        p = bytearray()
        for k in sorted(d): p.extend(ef(k,d[k]))
        return p
    
    pwd = str(random.randint(1000000000,9999999999))
    ph = hashlib.sha256(pwd.encode()).hexdigest().upper()
    
    bd = urlencode({'password':ph,'client_type':'2','source':'2','app_id':cid})
    hd = {'User-Agent':ua,'Authorization':f"Signature {hmac.new(s,bd.encode(),hashlib.sha256).hexdigest()}",'Content-Type':'application/x-www-form-urlencoded'}
    
    # Guest Register
    r1 = session.post('https://ffmconnect.live.gop.garenanow.com/oauth/guest/register', data=bd, headers=hd, timeout=10)
    if r1.status_code != 200: 
        session.close()
        return None, None
    
    uid = r1.json().get("uid")
    if not uid: 
        session.close()
        return None, None
    
    # Token Grant
    td = {'uid':str(uid),'password':ph,'response_type':"token",'client_type':"2",'client_secret':s.decode(),'client_id':cid}
    r2 = session.post("https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant", data=td, headers={'User-Agent':ua}, timeout=10)
    if r2.status_code != 200: 
        session.close()
        return None, None
    
    j = r2.json()
    at = j.get("access_token")
    oid = j.get("open_id") or j.get("openId") or j.get("openid")
    if not at or not oid: 
        session.close()
        return None, None
    
    # Major Register
    pf = {1:f"0xMe{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in str(random.randint(1,9999)))}",2:at,3:oid,5:102000007,6:4,7:1,13:1,14:e(oid),15:region,16:1}
    ed = bytes.fromhex(aes(ep(pf).hex()))
    
    hs = {"Authorization":f"Bearer {at}","X-Unity-Version":"2018.4.11f1","X-GA":"v1 1","ReleaseVersion":"OB50","Content-Type":"application/octet-stream","Content-Length":str(len(ed)),"User-Agent":ua,"Host":"loginbp.ggblueshark.com","Connection":"Keep-Alive","Accept-Encoding":"gzip"}
    r3 = session.post('https://loginbp.ggblueshark.com/MajorRegister', data=ed, headers=hs, timeout=10)
    session.close()
    
    if r3.status_code == 200:
        return uid, ph
    return None, None
    

regions = ['IND','SG','RU','ID','TW','US','VN','TH','ME','PK','CIS','BR','BD']
accounts = {r: dict(zip(["uid","password"], register(r))) for r in regions}
with open("../Configuration/AccountConfiguration.json","w") as f:
    json.dump(accounts,f,indent=4)
print("Saved ✅")