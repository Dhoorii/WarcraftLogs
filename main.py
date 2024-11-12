import json
import xlsxwriter
import requests

from playerData import playerData

publiURL = "https://www.warcraftlogs.com/api/v2/client"
tokenURL = "https://www.warcraftlogs.com/oauth/token"
url = "https://www.warcraftlogs.com/reports/KRwc1f7JNgvmz8yp#fight=66"
clientID = #insert clientID here
secret = #insert secret here

##function to get token for API
def get_token(store : bool = True):
    data = {"grant_type":"client_credentials"}
    auth = (clientID,secret)
    with requests.Session() as sesion:
        response = sesion.post(tokenURL, data= data, auth=auth)
    if store and response.status_code == 200:
        store_token(response)
    return response

##function to store token
def store_token(response):
    try:
        with open (".credentials.json",mode="w+",encoding="utf-8") as f:
            json.dump(response.json(),f)
    except OSError as e:
        print(e)
        return None
def read_token():
    try:
        with open (".credentials.json",mode="r+",encoding="utf-8") as f:
            access_token = json.load(f)
        return access_token.get("access_token")
    except OSError as e:
        print(e)
        return None

def retrive_header()-> dict[str,str]:
    return {"Authorization": f"Bearer {read_token()}"}

##query to return bosses name,hp procesnt, id of fight
queryFight = """query($code:String){
            reportData{
                report(code:$code){
                fights(difficulty:5){
                name
                bossPercentage
                kill
                id
                }
                }}
                }"""
##query to retrive main page of warcraft logs for $code as a ID of fight
queryPerBattle = """query($code:String,$idvalue:Int){
            reportData{
                report(code:$code){
                table(fightIDs:[$idvalue])
                }}
                }"""
## query to get latest fight code
queryGuildCode = """query($idvalue:Int){
            reportData{
                reports(guildID:$idvalue){
                data{
                code
                }
                }}
                }"""

##function to get data from responce
def get_data(query: str,**kwargs):
    data = {"query":query,"variables":kwargs}
    with requests.Session() as session:
        session.headers = retrive_header()
        response = session.get(publiURL,json=data)
        return response.json()


## function to retrive if player used Hstones and battle potions
def getPotionsAndHStones(playerClass):
        potionUsed = playerClass.get("potionUse")
        hsused = playerClass.get("healthstoneUse")
        playerName = playerClass.get("name")
        player = playerData(playerName, potionUsed, hsused)
        return player


def write_tabls_excel(workbook,fightID,bossName,list):
    sheet = workbook.add_worksheet(bossName+" ID " +str(fightID))
    iteration = 2
    format = workbook.add_format({'bg_color': 'red'})
    sheet.write('A1', "Player Name")
    sheet.write('B1', "number of battle potions used")
    sheet.write('C1', "number of HS used")
    for player in list:
        sheet.write('A' + str(iteration),player.name)
        if player.potion == 0:
            sheet.write('B' + str(iteration), player.potion,format)
        else:
            sheet.write('B' + str(iteration), player.potion)
        if player.HS == 0:
            sheet.write('C' + str(iteration), player.HS,format)
        else:
            sheet.write('C' + str(iteration), player.HS)
        iteration = iteration+1



def main():
    print("End of Process")


if __name__ == "__main__":
    token = read_token()##270563
    var = input("put guild ID for logs: ")
    responce = get_data(queryGuildCode,idvalue = int(var))
    codeList = responce.get("data").get("reportData").get("reports").get("data")
    i = int(0)
    while i < 5:
        print(str(i)+":"+str(responce.get("data").get("reportData").get("reports").get("data")[i].get("code")))
        i = i +1
    var = input("pick what log to choose:")
    code = responce.get("data").get("reportData").get("reports").get("data")[int(var)].get("code")
    responce = get_data(queryFight, code=code)
    listoffightID = responce.get("data").get("reportData").get("report").get("fights")
    workbook = xlsxwriter.Workbook("output/"+code + ".xlsx")
    for fightID in listoffightID:
        ID = fightID.get("id")
        list = []

        responce = get_data(queryPerBattle, code=code,idvalue = int(ID))
        listOfPlayers = responce.get("data").get("reportData").get("report").get("table").get("data").get("playerDetails")
        for playerclass in listOfPlayers.get("dps"):
            list.append(getPotionsAndHStones(playerclass))
        for playerclass in listOfPlayers.get("tanks"):
            list.append(getPotionsAndHStones(playerclass))
        for playerclass in listOfPlayers.get("healers"):
            list.append(getPotionsAndHStones(playerclass))
        bossName = fightID.get("name")
        write_tabls_excel(workbook,ID,bossName.split()[0],list)
    workbook.close()
    main()