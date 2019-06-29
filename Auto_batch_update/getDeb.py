# -*- coding: UTF-8 -*- 
import os
from flask import Flask, render_template
from flask import request
from AiClothClient import AiClothClient
import subprocess

## 127.0.0.1:7777/factorys_and_machines
#将当前运行的主程序构建成Flask应用,以便接收用户的请求(request)和响应(response)
app = Flask(__name__)



@app.route('/push',methods=['POST','GET'],endpoint='func3')
def show_at_page():
    client = AiClothClient()
    all_deb_list = client.get_al_deb()
    deb_list=[]
    for i in all_deb_list:
        if i.startswith("flaw") or i.startswith("detection"):
            deb_list.append(i)
    deb_xargs='false'
    if request.method == 'POST':     ## request.form(        ## post request.form
        deb_xargs = request.form['deb_xargs']
        deb_xargs = deb_xargs.strip()
        if_to_push_deb = request.form['not_or_yes']

        push_deb_shell = 'python3 auto_push_deb.py --deb '+ deb_xargs +' --env prod'
        #status,out = subprocess.getstatusoutput(push_deb_shell)
        status = os.system(push_deb_shell)
        print(push_deb_shell)
        print(status)

    return render_template("push.html",**locals())

if __name__ == "__main__":
    app.run(
        host = '0.0.0.0',
        port = 7778,    ## 127.0.0.1:7778/push
        debug =False
        )
    # app.run()
###  gunicorn -w 3 -b 0.0.0.0:7778  getDeb:app   
