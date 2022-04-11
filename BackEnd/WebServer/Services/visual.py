
from utils import *
from flask import jsonify, request
from Models.visuals import Visuals
import os

from jira.client import JIRA


def SaveVisuals(id_user):
        visuals = {
            "id_user": id_user,  # id user mich unique
            "visuals": request.json.get('visuals'),
            "projet": request.json.get('projet'),
            "data": {},
            "last_ticket_id": ""
        }
        print(visuals)
        # id_visual, data, visual:suivi bug
        visual = Visuals(
            id_user=id_user, visuals=visuals["visuals"], projet=visuals["projet"])
        check_visual = Visuals.objects(id_user=id_user,projet=visuals["projet"])
        if check_visual:
            check_visual.update(visuals=request.json.get('visuals'))
            return jsonify({"message": "Updated successfully"}), 200
        else:
            visual.save()
            return jsonify({"message": "Saved successfully"}), 200
  
  
  
def GetSelectedVisuals(id_user,projet,jira_domaine,email,jira_token):
        jira=connect_jira(jira_domaine,email,jira_token)

        visuals = Visuals.objects(id_user= id_user, projet = projet)

        if not(visuals):
            return jsonify({ "visuals": [] }), 200
            
        visuals = Visuals.objects.get(id_user= id_user, projet=projet)
        if (not (check_last_ticket(jira,visuals["last_ticket_id"],visuals["projet"])[0])):    
            return jsonify({"visuals": visuals["visuals"],"statistics":visuals["data"]}), 200
        else:
            if ("Suivi des bugs" in visuals["visuals"]):
                update_bugs_by_month_jira(jira,visuals["data"]["Suivi des bugs"],visuals["last_ticket_id"],visuals["projet"])
            if ("Ticket par priorité et par mois" in visuals["visuals"]):
                update_issues_by_priority_month_jira(jira,visuals["data"]["Ticket par priorité et par mois"],visuals["last_ticket_id"],visuals["projet"])
            if ("Ticket par statut et par client" in visuals["visuals"] ):
                update_issues_by_status_jira(jira,visuals["data"]["Ticket par statut et par client"],visuals["last_ticket_id"],visuals["projet"])
            if ("Nombre de demandes par priorité" in visuals["visuals"]):
                update_issues_by_priority_jira(jira,visuals["data"]["Nombre de demandes par priorité"],visuals["last_ticket_id"],visuals["projet"])
            visuals.update(last_ticket_id=(check_last_ticket(jira,visuals["last_ticket_id"],visuals["projet"])[1]),data=visuals["data"])
            return jsonify({"visuals": visuals["visuals"],"statistics":visuals["data"]}), 200



def GetData(id_user, jira_domaine,email,jira_token):
    jira=connect_jira(jira_domaine,email,jira_token)
    result=Visuals.objects.get(id_user=id_user,projet=request.json.get('projet'))

    if not(result):
        return jsonify({ "error": "Session expired" }), 401
        
    else: 
        data,last_ticket=convert_visuals(request.json.get('element'),result['projet'],jira_domaine,id_user,jira,result["data"])
        result.update(data=data,last_ticket_id=last_ticket)
        return jsonify({"result": result["data"]}), 200

            
            
            
