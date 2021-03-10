# -*- coding: utf-8 -*-
import common

def Resolve(channel):
	url = 'https://{0}.euronews.com/api/watchlive.json'.format(channel)
	UA = common.GetUserAgent()
	headers = {'User-Agent': UA}
	prms = common.OpenURL(url, headers=headers, responseMethod='json')
	if prms['url'] != None:
		prms = common.OpenURL('https:{0}'.format(prms['url']), headers=headers, responseMethod='json')
		url = '{0}|User-Agent={1}'.format(prms['primary'], UA)
	else:
		url = 'plugin://plugin.video.youtube/play/?video_id={0}'.format(prms['videoId'])
	return url
