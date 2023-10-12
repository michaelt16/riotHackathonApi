
import json
from flask import Flask, request, jsonify
from mwrogue.esports_client import EsportsClient
import urllib.request
from flask_cors import CORS
from flask import send_file
import ijson

app = Flask(__name__)
CORS(app) 

def get_filename_url_to_open(site: EsportsClient, filename, team, width=None):
    response = site.client.api(
        action="query",
        format="json",
        titles=f"File:{filename}",
        prop="imageinfo",
        iiprop="url",
        iiurlwidth=width,
    )

    print(response)
    image_info = next(iter(response["query"]["pages"].values()))["imageinfo"][0]

    if width:
        url = image_info["thumburl"]
    else:
        url = image_info["url"]
        
    urllib.request.urlretrieve(url, f"icons/{team}.png")
    return url +".jpg"

@app.route('/api/icon/<team>', methods=['GET'])
def get_icon(team):
    site = EsportsClient("lol")
    response = site.cargo_client.query(
        tables="Teams=T",
        fields="T.Name, T.Short",
        where=f"(T.Short = '{team}' OR T.Name = '{team}') AND T.IsDisbanded = false",
    )
    team_name = response[0]["Name"]
    url = f"{team_name}logo square.png"
    try:
        get_filename_url_to_open(site, url, team)
        return send_file(f"icons/{team}.png", mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/generate_tournament_data/<id>', methods=['GET'])
def generate_tournament_data(id):
    filePath ="esports-data/leagues.json"
    tournament_objects =[]
    with open (filePath,"r") as file:
        leaguesData = json.load(file)
        for data in leaguesData:
            if(data["id"]==id):
                tournamentsData = data["tournaments"]
                print(data)
                print(tournamentsData)
                for tournament in tournamentsData:
                    # print(tournament["id"],data["name"])
                    tournament_object = get_tournament_standings(tournament["id"])
                    print(tournament_object)
                    tournament_objects.append(tournament_object)
        return jsonify(tournament_objects)

def get_tournament_standings(tournamentId):
    filePath = "esports-data/tournaments.json"
    try:
        with open(filePath, "r") as file:
            tournamentData = json.load(file)
            for data in tournamentData:
                if data["id"] == tournamentId:
                    # toggled to regular season only for now
                    
                    rankingsData = data["stages"][0]["sections"][0]["rankings"]
                    for rankings in rankingsData:
                        teamId = rankings["teams"][0]["id"]
                        teamInfo = get_team(teamId)
                        
                        if teamInfo is not None:
                            updated_team_entry = {
                                "id": rankings["teams"][0]["id"],
                                "teamInfo": teamInfo
                            }
                            rankings["teams"] = [updated_team_entry]
                    
                    return {
                        "tournamendId": data["id"],
                        "leagueId": data["leagueId"],
                        "tornamentName": data["slug"],
                        "split": data["name"],
                        "startDate": data["startDate"],
                        "tournamentStandings": rankingsData
                    }
    except FileNotFoundError:
        return jsonify({"error": "File not found"})
       

def get_team(id):
    filePath="esports-data/teams.json"
    with open(filePath,"r") as file:
        teamsData = json.load(file)
        for data in teamsData:
            if(data["team_id"]==id):
                return data

if __name__ == '__main__':
     app.run(debug=True)
    #  generate_tournament_data("98767991299243165")
    # get_tournament_standings("108206581962155974")
    # get_team("103461966951059521")