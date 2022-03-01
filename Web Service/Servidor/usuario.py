class Usuario():
    def __init__(self, nome, rg, matricula, endereco, senha):
        self.__nome = nome
        self.__rg = rg
        self.__matricula = matricula
        self.__endereco = endereco
        self.__senha = senha

    def getNome(self):
        return self.__nome

    def setNome(self, nome):
        self.__nome = nome

    def getRG(self):
        return self.__rg

    def setRG(self, rg):
        self.__rg = rg

    def getMatricula(self):
        return self.__matricula

    def setMatricula(self, matricula):
        self.__matricula = matricula

    def getEndereco(self):
        return self.__endereco

    def setEndereco(self, endereco):
        self.__endereco = endereco

    def getSenha(self):
        return self.__senha

    def setSenha(self, senha):
        self.__senha = senha