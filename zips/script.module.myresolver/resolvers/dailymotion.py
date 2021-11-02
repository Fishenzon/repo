# -*- coding: utf-8 -*-
import re, common

def s(elem):
	if elem[0] == "auto":
		return 1
	else:
		return int(elem[0].split("@")[0])

def Resolve(vid):
	headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.1; Pixel Build/NMF26O) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36',
	   'Origin': 'https://www.dailymotion.com',
	   'Referer': 'https://www.dailymotion.com/'}
	cookie = {'lang': 'en_US', 'ff': 'off'}
	session = common.GetSession()
	content = common.OpenURL("https://www.dailymotion.com/player/metadata/video/{0}".format(vid), session=session, headers=headers, cookies=cookie, responseMethod='json')
	if content.get('error') is not None:
		return ''
	else:
		cc = content['qualities']
		cc = list(cc.items())
		cc = sorted(cc, key=s, reverse=True)
		for source, json_source in cc:
			for item in json_source:
				m_url = item.get('url', None)
				if m_url:
					m_url = m_url.replace('dvr=true&', '')
					if '.m3u8?sec' in m_url:
						text = common.OpenURL(m_url, headers=headers, cookies=session.cookies.get_dict())
						mb = re.findall('NAME="([^"]+)"\n(.+)', text)
						mb = sorted(mb, key=s, reverse=True)
						for quality, strurl in mb:
							quality = quality.split("@")[0]
							if not strurl.startswith('http'):
								strurl1 = re.findall('(.+/)', m_url)[0]
								strurl = strurl1 + strurl
							strurl = '{0}|{1}'.format(strurl.split('#cell')[0], common.urlencode(headers))
							return strurl

