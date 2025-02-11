#!/usr/bin/env python3
# Copyright 2025-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This downloads all *.asc models from facetdiagrams.org

import os
import http.client
from tqdm import tqdm
from lxml import etree
from subprocess import DEVNULL, STDOUT, check_call, CalledProcessError


if __name__ == "__main__":
    limit = 3000
    conn = http.client.HTTPSConnection("www.facetdiagrams.org")
    conn.request("GET", f"/cgi-bin/showmatches.py?shape=00&asc=1&nppg={limit}", "")
    res = conn.getresponse()
    data = res.read()

    root = etree.fromstring(data.decode("utf-8"), etree.HTMLParser())
    results = root.xpath("/html/body/div[3]/div/div/p/a[1]")
    bar = tqdm(results)
    for r in bar:
        link = r.attrib["href"]
        id = link.split("/")[-1].split(".")[0]
        if (os.path.exists(f"{id}.asc")):
            continue
        bar.set_description(id)
        download_url = f"https://www.facetdiagrams.org/database/files/{id}.asc"
        try:
            check_call(['wget', download_url], stdout=DEVNULL, stderr=STDOUT)
        except CalledProcessError as e:
            print(e)
