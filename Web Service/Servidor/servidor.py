import http.server
import socketserver
import json
import pandas as pd
import usuario

PORT = 8888
dic_usuarios = {}

class MyHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if len(dic_usuarios) == 0:
            self.recuperar_arquivo()

        valor = self.get_parametros()

        if len(dic_usuarios) == 0:
            self.resposta(200, "Nao existem usuarios cadastrados")
        else:
            dic_retorno = {}
            if valor == None:
                output_json = json.dumps(self.retorna_dic_todos())
                self.resposta(200, output_json)
            elif type(valor) is dict:
                if valor['senhaAtual'] == dic_usuarios[int(valor['rg'])].getSenha():
                    self.resposta(200, "Senha correta.")
                else:
                    self.resposta(200, "Senha incorreta.")
            else:
                user_pesq = dic_usuarios.get(int(valor))
                if user_pesq:
                    dic_retorno = {'nome':str(user_pesq.getNome()),
                    'rg':int(user_pesq.getRG()), 'matricula':int(user_pesq.getMatricula()), 
                    'endereco': str(user_pesq.getEndereco()),
                    'senha': str(user_pesq.getSenha())}

                    output_json = json.dumps(dic_retorno)
                    self.resposta(200, output_json)
                else:
                    self.resposta(200, "Usuario nao encontrado.")

    def get_parametros(self):
        caminho = self.path
        if '?' in caminho:
            lista = caminho.split('?')
            if '&' in caminho:
                dic = {}
                params = lista[1].split('&')
                for i in range(len(params)):
                    key_value = params[i].split('=')
                    dic[key_value[0]] = key_value[1]
                print(dic)
                return dic
            else:
                chave_valor = lista[1].split('=')
                return int(chave_valor[1])
        else:
            return None
    
    def recuperar_arquivo(self): # Pega do arquivo de persistencia e coloca para o dicionario
        global dic_usuarios
        try:
            data = pd.read_csv('arquivo_usuarios.csv')
            dic = {}
            if len(data) !=0:  
                for i in range (len(data)):
                    u = usuario.Usuario(str(data['nome'][i]), 
                    int(data['rg'][i]), int(data['matricula'][i]), 
                    str(data['endereco'][i]),
                    str(data['senha'][i]))

                    dic[data['rg'][i]] = u
            dic_usuarios = dic.copy()
        except:
            pass

    def retorna_dic_todos(self):
        lista = []
        for key,value in dic_usuarios.items():
            dic = {'nome':str(value.getNome()),'rg':int(value.getRG()), 
            'matricula':int(value.getMatricula()), 'endereco': str(value.getEndereco()),
            'senha': str(value.getSenha())}

            lista.append(dic)
        return lista

    def do_POST(self):
        if len(dic_usuarios) == 0:
            self.recuperar_arquivo()

        content_length = int(self.headers['Content-Length'])
        
        if content_length == 0:
            self.resposta(400, "Requisicao mal formada.")
        else:
            input_json = self.rfile.read(content_length)
            data = json.loads(input_json)
            
            existe = dic_usuarios.get(int(data['rg']))
            if existe:
                self.resposta(400, "Usuario ja existe.")
            else:
                novo_usuario = usuario.Usuario(str(data['nome']), 
                int(data['rg']), int(data['matricula']), 
                str(data['endereco']), str(data['senha']))

                dic_usuarios[novo_usuario.getRG()] = novo_usuario
                self.persistir()
                self.resposta(200, "Usuario adicionado.")   
        
    def persistir(self):
        lista_todos = list()
        for key,value in dic_usuarios.items():
            lista = [value.getNome(), value.getRG(), value.getMatricula(), 
            value.getEndereco(), value.getSenha()]
            
            lista_todos.append(lista)

        df = pd.DataFrame(list(lista_todos), columns=['nome', 'rg', 'matricula', 'endereco', 'senha'])
        df.to_csv("arquivo_usuarios.csv", index=False)

    def do_PUT(self):
        if len(dic_usuarios) == 0:
            self.recuperar_arquivo()

        content_length = int(self.headers['Content-Length'])

        valor = self.get_parametros()

        if content_length == 0 or valor == None:
            self.resposta(400, "Requisicao mal formada.")
        else:
            input_json = self.rfile.read(content_length)
            novo_dado = json.loads(input_json)
            usuario = dic_usuarios.get(int(valor))
            if usuario:
                if len(novo_dado) == 2:
                    if novo_dado['senhaAtual'] == usuario.getSenha():
                        self.atualizar(usuario, novo_dado)
                        self.persistir()
                        self.resposta(202, "Senha alterada.")
                    else:
                        self.resposta(401, "Senha atual incorreta.")
                else:
                    self.atualizar(usuario, novo_dado)
                    self.persistir()
                    self.resposta(200, "Informacoes alteradas.")      
            else:
                self.resposta(400, "Usuario nao encontrado.")

    def atualizar(self, usuario, novo_dado):
        dic_usuarios.pop(usuario.getRG())

        if len(novo_dado) == 4:
            usuario.setNome(str(novo_dado['nome']))
            usuario.setRG(int(novo_dado['rg']))
            usuario.setMatricula(int(novo_dado['matricula']))
            usuario.setEndereco(str(novo_dado['endereco']))
        else:
            usuario.setSenha(str(novo_dado['senhaNova'])) 

        dic_usuarios[usuario.getRG()] = usuario

    def do_DELETE(self):
        if len(dic_usuarios) == 0:
            self.recuperar_arquivo()

        valor = self.get_parametros()

        if valor == None:
            self.resposta(400, "Requisicao mal formada") 
        else:
            usuario = dic_usuarios.get(int(valor))
            if usuario:
                dic_usuarios.pop(usuario.getRG())
                self.persistir()
                self.resposta(202, "Usuario removido.")      
            else:
                self.resposta(400, "Usuario nao encontrado.")

    def resposta(self, codigo, mensagem):
        self.send_response(codigo)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write(mensagem.encode('utf-8'))

Handler = MyHandler

server = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
print("Publicando http://0.0.0.0:{}".format(PORT))
server.serve_forever()