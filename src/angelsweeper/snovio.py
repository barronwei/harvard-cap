import requests
import json

TOKEN_LINK = "https://app.snov.io/oauth/access_token"
EMAIL_LINK = "https://app.snov.io/restapi/get-emails-from-names"
STATS_LINK = "https://app.snov.io/restapi/get-emails-verification-status?emails[]="


def get_token(cli, sec):
    params = {
        "grant_type": "client_credentials",
        "client_id": cli,
        "client_secret": sec,
    }

    res = requests.post(TOKEN_LINK, data=params)
    res_txt = res.text.encode("ascii", "ignore")
    payload = json.loads(res_txt)

    return payload.get("access_token")


def get_email(tok, dom, fst, lst):
    params = {
        "access_token": tok,
        "domain": dom,
        "firstName": fst,
        "lastName": lst,
    }

    res = requests.post(EMAIL_LINK, data=params)
    res_txt = res.text.encode("ascii", "ignore")
    payload = json.loads(res_txt)

    return payload


def ver_email(tok, ref):
    params = {
        "access_token": tok,
    }

    res = requests.post(STATS_LINK + "&emails[]=".join(ref), data=params)
    res_txt = res.text.encode("ascii", "ignore")
    payload = json.loads(res_txt)

    return payload
