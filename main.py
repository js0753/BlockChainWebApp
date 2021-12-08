from flask import Flask,render_template,request
from livereload import Server
from services import blockchain as bc
app = Flask(__name__)
# app = create_app()
app.debug = True
server = Server(app.wsgi_app)
"""
#When two same app.route("/") first one counts  
@app.route("/")
def hello1():
   return render_template('aboutus.html')

"""
@app.route("/")
def hello():
   return render_template('index.html',msg="Hello User")

@app.route("/InitChain")
def initChain():
   bc.UTXO_DB={}
   bc.mempool=[]
   bc.last_block_hash=""
   bc.difficulty=1
   bc.block_chain={}
   bc.total_blocks=0
   bc.accepted_block_reward=50
   bc.block_no=0
   bc.mining=False
   bc.users_list=bc.create_userslist()
   return render_template('index.html',msg="Chain initialised",cred=bc.users_list["6"])


# @app.route("/movieIn",methods=['POST'])
# def movieIn():
#    #print("here")
#       return render_template('movies.html',sim_mov=sim_mov,img_list=img_list,link=link,releaseDate=releaseDate,overview=overview,voteAverage=voteAverage,genres=genres,runTime=runTime)
    
@app.route("/ViewChain")
def viewChain():
   return render_template('index.html',msg="Viewing Chain",chain=bc.block_chain)

@app.route("/ViewMempool")
def viewMempool():
   #print("Len mempool :",len(bc.mempool))
   return render_template('index.html',msg="Viewing Mempool",mempool=bc.mempool)

@app.route("/ViewUTXO")
def viewUTXO():
   return render_template('index.html',msg="Viewing UTXO DB",utxodb=bc.UTXO_DB)


@app.route("/ViewCred")
def genCred():
   return render_template('index.html',msg="Viewing Credentials",cred=bc.users_list["6"])

@app.route("/Transact")
def transact():
   return render_template('index.html',msg="Perform Transaction")

@app.route("/TransactionCreated")
def transactionCreated():
   receiver=request.args['receiver']
   val=request.args['amount']
   bc.gen_transaction(bc.users_list["6"],receiver,int(val))
   return render_template('index.html',msg="Transaction added to mempool")

@app.route("/Mine")
def mine():
   bc.mining=True
   msg=bc.mine_script()
   return render_template('index.html',msg=msg)

@app.route("/ViewBlock")
def viewBlock():
   blockHash=request.args['blockHash']
   return render_template('blockviewer.html',block_chain=bc.block_chain,blockHash=blockHash)

# @app.route("/StopMining")
# def stopMining():
#    bc.mining=False
#    return render_template('miner.html',msg="Mining Stopped")

if __name__ == '__main__':
   #  app.run(debug=True)
   server.serve(debug=True)