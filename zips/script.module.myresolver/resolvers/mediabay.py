# -*- coding: utf-8 -*-
import common

def Resolve(channel):
	url = 'https://api.mediabay.tv/v2/channels/thread/{0}'.format(channel)
	UA = common.GetUserAgent()
	headers = {'User-Agent': UA}
	prms = common.OpenURL(url, headers=headers, responseMethod='json')
	return '{0}|User-Agent={1}'.format(prms['data'][0]['threadAddress'], UA)
