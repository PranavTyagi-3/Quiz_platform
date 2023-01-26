from flask import Flask,render_template,request,redirect,url_for,session
import secrets
import string
import pickle
import itertools
import base64

def encrypt(text):
            # Encode the text using Base64
            encoded_text = base64.b64encode(text.encode())
            # Decode the encoded text to a string
            encrypted_text = encoded_text.decode()
            return encrypted_text

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')


@app.route('/make.html',methods=("GET","POST"))
def make():
    if request.method=="POST":

        

        while True:
            code = str(''.join(secrets.choice(string.ascii_uppercase + string.digits)for i in range(5)))
            master=encrypt(code)[:-1]
            rec=[]
            try:
                f=open('keys.bin','rb')
                f.close()
            except:
                f=open('keys.bin','wb')
                f.close()
                break
            with open('keys.bin','rb') as f:
                while True:
                    try:
                        rec.append(pickle.load(f))
                    except:
                        break
            if code not in rec:
                break
        
        q=request.form['questions']
        print(q)
        print(type(q))
        f=open('question.txt','a')
        f.write("@@@@@\n")
        f.write(code+'\n')
        f.write(q)
        f.close()
        with open('key.bin','ab') as f:
            pickle.dump(code,f)
        return render_template('make.html',m='Success',code=code,master=master)
        
    return render_template('make.html')


@app.route('/take.html',methods=("GET","POST"))
def take():
    if request.method=="POST":
        q_id=request.form['qcode']
        return redirect(f'/test.html/{q_id}')
    return render_template('take.html')

@app.route('/test.html/<q_id>',methods=("GET","POST"))
def test(q_id):

    if request.method=="POST":
        global subm
        subm=list(request.form.listvalues())
        subm = list(itertools.chain(*subm))
        print(subm)
        return redirect(url_for('res',q_id=q_id))
    try:
        f=open('question.txt','r')
        f.close()
    except:
        return render_template('/test.html',message='not found')
    f=open('question.txt','r')
    li=f.read().split("@@@@@")[1:]
    f.close()
    counter=0
    for quiz in li:
        id=quiz.strip()[0:5]
        if id==q_id:
            counter+=1
            break
    if counter==0:
        return render_template('/test.html',message='not found')
    else:
        question_list=quiz.strip().split("***")
        del(question_list[0])
        mydict={}
        for q in question_list:
            q=q.strip()
            final=q.split("\n\n")
            temp=[]
            for i in final[1:]:
                if i.strip()[-1:-4:-1]=="###":
                    temp.append(i[0:-3])
                else:
                    temp.append(i)
            mydict[final[0]]=temp
        return render_template('/test.html',mydict=mydict)

@app.route('/res.html')
def res():
    q_id = request.args.get('q_id')
    print(subm)
    f=open('question.txt','r')
    li=f.read().split("@@@@@")[1:]
    f.close()
    for quiz in li:
        id=quiz.strip()[0:5]
        if id==q_id:
            break
    question_list=quiz.strip().split("***")
    del(question_list[0])
    final=[]
    for q in question_list:
        q=q.strip()
        for i in q.split("\n\n")[1:]:
            if i.strip()[-1:-4:-1]=="###":
                final.append(i.replace('###',' ').strip())
    
    name=subm.pop(0)
    score=0
    for i in range(len(subm)):
        if subm[i].strip()==final[i].strip():
            score+=1
    print(score)
    print(final)
    try:
        f=open('result.bin','rb')
        f.close()
    except:
        f=open('result.bin','wb')
        f.close()
    f=open('result.bin','rb')
    while True:
        try:
            res=pickle.load(f)
            if name in res:
                f.close()
                return render_template('/res.html',err='Already exist',old_sc=res[name])
        except:
            break

    f=open('result.bin','ab')
    pickle.dump([q_id,name,score,subm],f)
    f.close()
    return render_template('/res.html',name=name,score=score,total=len(final))

@app.route('/chk.html/<master_id>')
def chk(master_id):
    f=open('key.bin','rb')
    print('read')
    c=0
    while True:
        try:
            code=pickle.load(f)
            print(code)
            m=encrypt(code.strip())[:-1]
            print(m)
            if m == master_id:
                c=1
                break
            print(c)
        except:
            break
    
    if c==0:
        return render_template('/chk.html',message="Incorrect Code")
    else:
        f=open('result.bin','rb')
        data=[]
        while True:
            try:
                rec=pickle.load(f)
                if code==rec[0]:
                    data.append(rec[1:])
            except:
                break
        print(data)
        return render_template('/chk.html',data=data,length=len(data))


if __name__=="__main__":
    app.run(debug=True)
