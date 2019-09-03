# -*- coding: utf-8 -*-
import json, common

def Resolve(channel):
	url = 'https://api.mediabay.tv/v2/channels/thread/{0}'.format(channel)
	UA = common.GetUserAgent()
	headers = {'User-Agent': UA}
	prms = json.loads(common.OpenURL(url, headers=headers))
	return '{0}|User-Agent={1}'.format(prms['data'][0]['threadAddress'], UA)
