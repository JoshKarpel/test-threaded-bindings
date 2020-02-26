#!/usr/bin/env python

from __future__ import print_function

import htcondor

htcondor.enable_debug()

coll = htcondor.Collector()
print("Collector is", coll)

private_ads = coll.query(htcondor.AdTypes.StartdPrivate)
print("Got Private ads")
# for ad in private_ads:
#     print(ad)

startd_ads = coll.query(htcondor.AdTypes.Startd)
print("Got Startd ads")
# for ad in startd_ads:
#     print(ad)

claim_ads = []
for ad in startd_ads:
    if "Name" not in ad:
        continue
    for pvt_ad in private_ads:
        if pvt_ad.get("Name") == ad["Name"]:
            ad["ClaimId"] = pvt_ad["Capability"]
            claim_ads.append(ad)

print("Got Claim ads")
# for ad in claim_ads:
#     print(ad)

schedd = htcondor.Schedd()
with schedd.negotiate("bbockelm@unl.edu") as session:
    print("Session is", session)
    found_claim = False
    for resource_request in session:
        print("resource request is", resource_request)

        for claim_ad in claim_ads:
            if resource_request.symmetricMatch(claim_ad):
                print("Sending claim for", claim_ad["Name"])
                session.sendClaim(claim_ads[0])
                break

print("NO ERROR")
