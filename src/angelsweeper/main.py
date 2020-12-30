import os
import sys
import json
import time
import snovio
import traceback
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from functools import partial

# links
BASE_URL = "https://angel.co"
MAIN_URL = "https://angel.co/harvard-university/followers"

# number of angels of interest
NUM_ANGELS = 60

# number of investments filter
NUM_INVEST = 2

# script clicking the more div
SCRIPT = "let more = document.getElementsByClassName('more hidden'); more[0].click()"

# seconds for implicitly waiting
IW = 20

# configuration
SNOVIO_CLIENT = os.getenv("CLIENT")
SNOVIO_SECRET = os.getenv("SECRET")
LINKEDIN_USER = os.getenv("USER")
LINKEDIN_PASS = os.getenv("PASS")


def log_ln(dr):
    try:
        dr.get("https://linkedin.com/login")
        dr.implicitly_wait(IW)
        username = dr.find_element_by_id("username")
        password = dr.find_element_by_id("password")
        username.send_keys(LINKEDIN_USER)
        password.send_keys(LINKEDIN_PASS)
        form = dr.find_element_by_tag_name("button")
        form.send_keys(Keys.ENTER)
        time.sleep(10)

    except:
        print("Failed to log into LinkedIn.")
        sys.exit(1)


def scrape(dr, addr):
    dr.get(addr)
    dr.implicitly_wait(IW)

    ct = 0
    p_vals = []

    while True:
        tmp = dr.find_elements_by_css_selector(".base.item")
        it = len(tmp)

        if ct == it:
            p_vals = tmp
            break

        ct = it

        if ct >= NUM_ANGELS:
            p_vals = tmp
            break

        dr.execute_script(SCRIPT)
        time.sleep(2)

    print("Found {} angels!".format(ct))

    counts = []
    p_urls = []

    for i in p_vals:
        try:
            column = i.find_element_by_css_selector(".column.investments")
            number = column.find_element_by_class_name("value")
            link = i.find_element_by_class_name("profile-link")
            href = link.get_attribute("href")
            counts.append(number.text.replace("\n", ""))
            p_urls.append(href)

        except:
            continue

    result = [p_urls[i] for i, v in enumerate(counts) if int(v) > NUM_INVEST]
    length = len(result)
    print("Found {} profiles!".format(length))

    return result[:NUM_ANGELS] if length > NUM_ANGELS else p_vals


def get_ln(dr, urls):
    res = []
    for i in urls:
        try:
            dr.get(i)
            dr.implicitly_wait(IW)
            l = dr.find_elements_by_css_selector(".icon.link_el.fontello-linkedin")

            if len(l):
                res.append(l.pop().get_attribute("href"))

        except:
            continue

    return res


def get_cp(dr, lst):
    res = {}
    for i in lst:
        try:
            dr.get(i)
            dr.implicitly_wait(IW)

            h = dr.find_elements_by_css_selector(".flex-1.mr5")
            e = dr.find_elements_by_id("experience-section")

            if len(h) and len(e):
                n = h[0].find_elements_by_tag_name("li")
                c = e[0].find_elements_by_css_selector(".full-width.ember-view")

                if len(n) and len(c):
                    txt = n[0].text.strip()
                    tmp = list(map(lambda x: x.get_attribute("href"), c))
                    lns = [tmp[i] for i, v in enumerate(tmp) if "/company/" in v]

                    if len(lns):
                        res.setdefault(txt, lns)

        except:
            continue

    return res


def domain_get(dr, ref):
    res = {}
    for k, v in ref.items():
        d = []
        for i in v:
            try:
                dr.get(i + "about")
                dr.implicitly_wait(IW)

                l = dr.find_elements_by_class_name(
                    "org-grid__core-rail--no-margin-left"
                )

                if len(l):
                    f = l[0].find_elements_by_class_name("link-without-visited-state")

                    if len(f):
                        t = f[0].text.strip()
                        t = t.replace("https://", "")
                        t = t.replace("http://", "")
                        t = t.replace("www.", "")
                        t = t.replace("/", "")

                        *_, dom, ext = t.split(".")

                        d.append(dom + "." + ext)

            except:
                continue

        res.setdefault(k, d)

    return res


def emails_format(dom, txt):
    return txt + "@" + dom


def emails_concat(fst, snd):
    return fst + snd


def emails_dotter(fst, snd):
    return fst + "." + snd


def emails_create(dom, fst, sur):
    x = [fst, fst[0], fst]
    y = [sur, sur, sur[0]]

    a = list(map(emails_concat, x, y))
    b = list(map(emails_concat, y, x))
    c = list(map(emails_dotter, x, y))
    d = list(map(emails_dotter, y, x))

    form = partial(emails_format, dom)

    return map(form, a + b + c + d)


def emails_verify(tok, ref):
    return snovio.ver_email(tok, ref)


def emails_get(ref):
    tok = snovio.get_token(SNOVIO_CLIENT, SNOVIO_SECRET)
    res = {}
    for k, v in ref.items():
        res.setdefault(k, [])
        fst, *_, sur = k.split()

        for i in v:
            response = snovio.get_email(tok, i, fst, sur)
            emails = response.get("data").get("emails")

            guessing = emails_create(i, fst, sur)
            result = emails_verify(tok, guessing)

            valids = [k for k, v in result.items() if v.get("data")]

            if emails:
                res.get(k).append(emails)

            if valids:
                res.get(k).append(valids)

    return res


def launch():
    dr = webdriver.Safari()

    try:
        log_ln(dr)
        lst = scrape(dr, MAIN_URL)
        res = get_ln(dr, lst)

        result = get_cp(dr, res) if len(res) else {}
        domain = domain_get(dr, result)
        emails = emails_get(domain)

        fin = {k: v[0][0] for k, v in emails.items() if v}

        print("Found {} emails!".format(len(fin)))

        with open("../sweeper.json", "w") as fd:
            json.dump(fin, fd)

        dr.quit()

    except:
        traceback.print_exc()
        dr.quit()


if __name__ == "__main__":
    launch()

