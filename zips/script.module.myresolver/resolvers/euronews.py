# -*- coding: utf-8 -*-
import json, common

def Resolve(channel):
	url = 'https://{0}.euronews.com/api/watchlive.json'.format(channel)
	UA = common.GetUserAgent()
	headers = {'User-Agent': UA}
	prms = json.loads(common.OpenURL(url, headers=headers))
	prms = json.loads(common.OpenURL('https:{0}'.format(prms['url']), headers=headers))
	return '{0}|User-Agent={1}'.format(prms['primary'], UA)
