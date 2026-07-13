import os,wave,time,json,numpy as np,mido
from flask import Flask,request,jsonify,render_template_string,send_from_directory
app=Flask(__name__)
VOWEL={'A':[(730,80),(1090,90),(2440,120)],'E':[(530,60),(1840,80),(2480,100)],'I':[(270,50),(2290,80),(3010,100)],'O':[(570,70),(840,80),(2410,110)],'U':[(300,50),(870,70),(2240,100)]}
for p in ['static/downloads','my_singing_dataset/wavs']:os.makedirs(p,exist_ok=True)
def res(x,f,b,fs):t=2*np.pi*f/fs;r=np.exp(-np.pi*b/fs);b1=-2*r*np.cos(t);b2=r*r;a=(1-r)*np.sqrt(1-2*r*np.cos(2*t)+r*r);y=np.zeros_like(x);y1=y2=0
 for i in range(len(x)):yv=a*x[i]-b1*y1-b2*y2;y[i]=yv;y2=y1;y1=yv
 return y
def exc(d,p,fs,vr=6,vd=0.015,nm=0.08):t=np.arange(int(d*fs))/fs;v=1+vd*np.sin(2*np.pi*vr*t);ph=2*np.pi*p*np.cumsum(v)/fs;e=np.zeros_like(t)
 for h in range(1,13):e+=np.sin(h*ph)/h;n=np.random.normal(0,0.5,len(t));return (1-nm)*e+nm*n
def vowel(t,ly):w=[w.upper() for w in ly.split() if w];w=w[int(t/0.6)%len(w)] if w else 'A';return next((c for c in w if c in 'AEIOU'),'A')
def synth(ly,notes,fs=22050,pf=None):
 if not notes:w=[w for w in ly.split() if w] or ["ZSD","Brain"];notes=[{'pitch':[60,62,64,67,69][i%5],'start':i*0.6,'duration':0.5} for i,_ in enumerate(w)]
 mt=max(n['start']+n['duration'] for n in notes)+0.5;out=np.zeros(int(mt*fs));fm=VOWEL.copy()
 vr,vd=pf.get('vibrato_rate',6),pf.get('vibrato_depth',0.015) if pf and pf.get('trained') else (6,0.015)
 if pf and 'formants' in pf:fm.update(pf['formants'])
 for n in notes:
  hz=440*2**((n['pitch']-69)/12);si=int(n['start']*fs);ex=exc(n['duration'],hz,fs,vr,vd);fn=np.zeros_like(ex);bs=int(0.05*fs)
  for b in range(0,len(ex),bs):v=vowel(n['start']+b/fs,ly);tmp=ex[b:b+bs];
   for f,bw in fm.get(v,fm['A']):tmp=res(tmp,f,bw,fs)
   fn[b:b+bs]=tmp
  fl=min(200,len(fn)//10);fn[:fl]*=np.linspace(0,1,fl);fn[-fl:]*=np.linspace(1,0,fl);ei=min(si+len(fn),len(out));out[si:ei]+=fn[:ei-si]
 return out
def write(fn,fs,s):s=np.clip(s,-1,1);w=wave.open(fn,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(fs);w.writeframes((s*32767).astype(np.int16).tobytes());w.close()
@app.route('/',methods=['GET','POST'])
def home():
 if request.method=='POST':ly=request.form.get('lyrics','music');audio=synth(ly,[]);fn=f"zsd_{int(time.time())}.wav";write(f"static/downloads/{fn}",22050,audio)
  return jsonify({"status":"success","download_url":f"/static/downloads/{fn}"})
 vs="Default";return render_template_string("<body style=background:#000;color:#fff><h1 style=color:orange>ZSD BRAIN</h1><form method=post><textarea name=lyrics></textarea><button>Generate</button></form></body>",voice_status=vs)
@app.route('/static/downloads/<path:f>')
def dl(f):return send_from_directory('static/downloads',f,as_attachment=True)
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',3000)))
