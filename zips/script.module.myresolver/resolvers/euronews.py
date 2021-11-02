# -*- coding: utf-8 -*-
import json, common

def Resolve(channel):
	url = 'https://{0}.euronews.com/api/watchlive.json'.format(channel)
	UA = common.GetUserAgent()
	headers = {'User-Agent': UA}
	prms = json.loads(common.OpenURL(url, headers=headers))
	if prms.get('url') == None and prms.get('player') == 'pfp':
		return 'plugin://plugin.video.youtube/play/?video_id={0}'.format(prms['videoId'])
	prms = json.loads(common.OpenURL('https:{0}'.format(prms['url']), headers=headers))
	return '{0}|User-Agent={1}'.format(prms['primary'], UA)
