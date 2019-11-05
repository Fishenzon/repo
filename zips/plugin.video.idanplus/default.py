# -*- coding: utf-8 -*-
import sys, os, urlparse, urllib, datetime, json
import xbmc, xbmcplugin, xbmcaddon
import resources.lib.common as common
import resources.lib.epg as epg
import resources.lib.iptv as iptv
import resources.lib.baseChannels as baseChannels

reload(sys)
sys.setdefaultencoding('utf-8')

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
AddonName = Addon.getAddonInfo("name")
icon = Addon.getAddonInfo('icon')
imagesDir = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), 'resources', 'images')).decode("utf-8")
profileDir = common.profileDir
favoritesFile = os.path.join(profileDir, 'favorites.json')
if not os.path.isfile(favoritesFile):
	common.WriteList(favoritesFile, [])
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
url = urllib.unquote_plus(params.get('url', ''))
mode = int(params.get('mode','-1'))
name = urllib.unquote_plus(params.get('name', ''))
iconimage = urllib.unquote_plus(params.get('iconimage', ''))
module = params.get('module')
moreData = urllib.unquote_plus(params.get('moredata', ''))

def GetCategoriesList():
	name = common.GetLabelColor("מועדפי עידן פלוס", bold=True, color="none")
	common.addDir(name, '', 10, icon, infos={"Title": name}, addFav=False)
	name = common.GetLabelColor("חיפוש תכניות", bold=True, color="none")
	common.addDir(name, '', 4, icon, infos={"Title": name}, addFav=False)
	name = common.GetLabelColor("טלויזיה", bold=True, color="none")
	common.addDir(name, '', 1, icon, infos={"Title": name})
	name = common.GetLabelColor("VOD", bold=True, color="none")
	common.addDir(name, '', 2, icon, infos={"Title": name})
	name = common.GetLabelColor("רדיו", bold=True, color="none")
	common.addDir(name, '', 3, icon, infos={"Title": name})
	name = common.GetLabelColor("תכניות רדיו", bold=True, color="none")
	common.addDir(name, '', 12, icon, infos={"Title": name})
	name = common.GetLabelColor("פודקאסטים", bold=True, color="none")
	common.addDir(name, '', 13, icon, infos={"Title": name})
	name = common.GetLabelColor("הגדרות", bold=True, color="none")
	common.addDir(name, 'Addon.OpenSettings', 6, icon, infos={"Title": name}, moreData=AddonID, isFolder=False)

def GetUserChannels(type='tv'):
	userChannels = []
	if type == 'tv':
		channels = baseChannels.TvChannels
	elif type == 'radio':
		channels = baseChannels.RadioChannels
	for channel in channels:
		channel['index'] = common.GetIntSetting(channel['ch'], channel['index'])
	channels = sorted(channels, key=lambda k: k['index']) 
	for channel in channels:
		if channel['index'] != 0:
			userChannels.append(channel)
	userChannels = sorted(userChannels, key=lambda k: k['index'])
	return userChannels

def LiveChannels():
	if Addon.getSetting("tvShortcut") == 'true':
		name = common.GetLabelColor(common.GetLocaleString(30652), bold=True, color="none")
		common.addDir(name, 'ActivateWindow', 6, icon, infos={"Title": name}, moreData='tvchannels', isFolder=False)
	nowEPG = epg.GetNowEPG()
	channels = GetUserChannels(type='tv')
	for channel in channels:
		if channel.get('type') == 'refresh': 
			name = common.GetLabelColor(common.GetLocaleString(channel['nameID']), bold=True, color="none")
			common.addDir(name, 'Container.Refresh', channel['mode'], channel['image'], infos={"Title": name}, moreData=';noexit', isFolder=False)
		else:
			programs = [] if channel['tvgID'] == '' else nowEPG.get(channel['tvgID'], [])
			LiveChannel(common.GetLocaleString(channel['nameID']), channel['channelID'], channel['mode'], channel['image'], channel['module'], contextMenu=[], resKey=channel['resKey'], programs=programs, tvgID=channel['tvgID'])

def LiveChannel(name, url, mode, iconimage, module, contextMenu=[], choose=True, resKey='', bitrate='', programs=[], tvgID='', addFav=True):
	channelNameFormat = int(Addon.getSetting("channelNameFormat"))
	displayName = common.GetLabelColor(name, keyColor="chColor", bold=True)
	description = ''
	iconimage = os.path.join(imagesDir, iconimage)
	
	if len(programs) > 0:
		contextMenu.insert(0, (common.GetLocaleString(30030), 'Container.Update({0}?url={1}&name={2}&mode=2&iconimage={3}&module=epg)'.format(sys.argv[0], tvgID, urllib.quote_plus(name), urllib.quote_plus(iconimage))))
		programTime = common.GetLabelColor("[{0}-{1}]".format(datetime.datetime.fromtimestamp(programs[0]["start"]).strftime('%H:%M'), datetime.datetime.fromtimestamp(programs[0]["end"]).strftime('%H:%M')), keyColor="timesColor")
		programName = common.GetLabelColor(programs[0]["name"].encode('utf-8'), keyColor="prColor", bold=True)
		displayName = GetChannelName(programName, programTime, displayName, channelNameFormat)
		description = '{0}[CR]{1}'.format(programName, programs[0]["description"].encode('utf-8'))
		if len(programs) > 1:
			nextProgramName = common.GetLabelColor(programs[1]["name"].encode('utf-8'), keyColor="prColor", bold=True)
			nextProgramTime = common.GetLabelColor("[{0}-{1}]".format(datetime.datetime.fromtimestamp(programs[1]["start"]).strftime('%H:%M'), datetime.datetime.fromtimestamp(programs[1]["end"]).strftime('%H:%M')), keyColor="timesColor")
			description = GetDescription(description, nextProgramTime, nextProgramName, channelNameFormat)
	if resKey == '' and bitrate == '':
		bitrate = 'best'
	else:
		if bitrate == '':
			bitrate = Addon.getSetting(resKey)
			if bitrate == '':
				bitrate = 'best'
		if addFav:
			contextMenu.insert(0, (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode={3}&iconimage={4}&moredata=set_{5}&module={6})'.format(sys.argv[0], url, urllib.quote_plus(displayName), mode, urllib.quote_plus(iconimage), resKey, module)))
	if choose:
		contextMenu.insert(0, (common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode={3}&iconimage={4}&moredata=choose&module={5})'.format(sys.argv[0], url, urllib.quote_plus(displayName), mode, urllib.quote_plus(iconimage), module)))
	if contextMenu == []:
		contextMenu = None
	urlParamsData = {'name': common.GetLabelColor(name, keyColor="chColor", bold=True), 'tvgID': tvgID} if addFav else {}
	common.addDir(displayName, url, mode, iconimage, infos={"Title": displayName, "Plot": description}, contextMenu=contextMenu, moreData=bitrate, module=module, isFolder=False, isPlayable=True, addFav=addFav, urlParamsData=urlParamsData)

def GetChannelName(programName, programTime, displayName, channelNameFormat):
	if channelNameFormat == 0:
		chName = " {0} - {1} {2} ".format(displayName, programName, programTime)
	elif channelNameFormat == 1:
		chName = " {0}  {1}  {2} ".format(displayName, programTime, programName)
	elif channelNameFormat == 2:
		chName = " {0} {1} - {2} ".format(programTime, programName, displayName)
	elif channelNameFormat == 3:
		chName = "  {0}  {1}  {2} ".format(programName, programTime, displayName)
	return chName
	
def GetDescription(description, nextProgramTime, nextProgramName, channelNameFormat):
	if channelNameFormat == 0 or channelNameFormat == 1:
		description = ' {0}[CR][CR]{1} {2} '.format(description, nextProgramTime, nextProgramName)
	elif channelNameFormat == 2 or channelNameFormat == 3:
		description = ' {0}[CR][CR]{1} {2} '.format(description, nextProgramName, nextProgramTime)
	return description

def VODs():
	name = common.GetLabelColor(common.GetLocaleString(30602), bold=True, color="none")
	common.addDir(name, '', 0, os.path.join(imagesDir, "kan.jpg"), infos={"Title": name}, module='kan')
	name = common.GetLabelColor(common.GetLocaleString(30603), bold=True, color="none")
	common.addDir(name, '', 0, os.path.join(imagesDir, "mako.png"), infos={"Title": name}, module='keshet')
	name = common.GetLabelColor(common.GetLocaleString(30604), bold=True, color="none")
	common.addDir(name, '', -1, os.path.join(imagesDir, "13.png"), infos={"Title": name}, module='reshet')
	name = common.GetLabelColor(common.GetLocaleString(30605), bold=True, color="none")
	common.addDir(name, '', 0, os.path.join(imagesDir, "ten.png"), infos={"Title": name}, module='ten')
	name = common.GetLabelColor(common.GetLocaleString(30606), bold=True, color="none")
	common.addDir(name, '', -1, os.path.join(imagesDir, "20.png"), infos={"Title": name}, module='twenty')
	name = common.GetLabelColor(common.GetLocaleString(30607), bold=True, color="none")
	common.addDir(name, 'https://www.kan.org.il/page.aspx?landingPageId=1083', 1, os.path.join(imagesDir, "23tv.jpg"), infos={"Title": name}, module='kan')
	name = common.GetLabelColor(common.GetLocaleString(30608), bold=True, color="none")
	common.addDir(name, 'http://www.mako.co.il/mako-vod-music24', 1, os.path.join(imagesDir, "24telad.png"), infos={"Title": name}, module='keshet')
	name = common.GetLabelColor(common.GetLocaleString(30630), bold=True, color="none")
	common.addDir(name, '', -1, os.path.join(imagesDir, "9tv.png"), infos={"Title": name}, module='9tv')
	name = common.GetLabelColor(common.GetLocaleString(30900), bold=True, color="none")
	common.addDir(name, '', -1, os.path.join(imagesDir, "Sport5.png"), infos={"Title": name}, module='sport5')
	name = common.GetLabelColor(common.GetLocaleString(31000), bold=True, color="none")
	common.addDir(name, '', -1, os.path.join(imagesDir, "sport1.jpg"), infos={"Title": name}, module='sport1')

def Radios():
	if Addon.getSetting("radioShortcut") == 'true':
		name = common.GetLabelColor(common.GetLocaleString(30732), bold=True, color="none")
		common.addDir(name, 'ActivateWindow', 6, icon, infos={"Title": name}, moreData='radiochannels', isFolder=False)
	nowEPG = epg.GetNowEPG()
	channels = GetUserChannels(type='radio') 
	for channel in channels:
		if channel.get('type') == 'refresh': 
			name = common.GetLabelColor(common.GetLocaleString(channel['nameID']), bold=True, color="none")
			common.addDir(name, 'Container.Refresh', channel['mode'], channel['image'], infos={"Title": name}, moreData=';noexit', isFolder=False)
		else:
			programs = [] if channel['tvgID'] == '' else nowEPG.get(channel['tvgID'], [])
			LiveChannel(common.GetLocaleString(channel['nameID']), channel['channelID'], channel['mode'], channel['image'], channel['module'], contextMenu=[], choose=False, programs=programs, tvgID=channel['tvgID'])

def RadioVODs():
	name = common.GetLabelColor("תכניות רדיו - כאן", bold=True, color="none")
	common.addDir(name, '', 21, os.path.join(imagesDir, 'kan.jpg'), infos={"Title": name}, module='kan')
	name = common.GetLabelColor("תכניות רדיו - 89.1fm", bold=True, color="none")
	common.addDir(name, '', 0, os.path.join(imagesDir, '891fm.png'), infos={"Title": name}, module='891fm')
	name = common.GetLabelColor("תכניות מוזיקה - eco99fm", bold=True, color="none")
	common.addDir(name, '', 0, os.path.join(imagesDir, '99fm.png'), infos={"Title": name}, module='99fm')
	name = common.GetLabelColor("תכניות רדיו ספורט 5", bold=True, color="none")
	common.addDir(name, '', 20, os.path.join(imagesDir, 'Sport5.png'), infos={"Title": name}, module='sport5')

def Podcasts():
	name = common.GetLabelColor("פודקאסטים - כאן", bold=True, color="none")
	common.addDir(name, '', 31, os.path.join(imagesDir, 'kan.jpg'), infos={"Title": name}, module='kan')
	name = common.GetLabelColor("פודקאסטים ספורט 5", bold=True, color="none")
	common.addDir(name, '', 20, os.path.join(imagesDir, 'Sport5.png'), infos={"Title": name}, module='sport5')

def MakeIPTVfiles():
	iptv.MakeIPTVlist(GetUserChannels(type='tv') + GetUserChannels(type='radio'))
	if common.isFileOld(common.epgFile):
		epg.GetEPG()
	iptv.MakeChannelsGuide()

def AddFavorite(url):
	favoritesList = common.ReadList(favoritesFile)
	if any(u == url for u in favoritesList):
		return
	favoritesList.append(url.decode("utf-8"))
	common.WriteList(favoritesFile, favoritesList)
	xbmc.executebuiltin("Notification({0}, {1}, 5000, {2})".format(AddonName, common.GetLocaleString(30028), icon))

def RemoveFavortie(index):
	favoritesList = common.ReadList(favoritesFile)
	if index < 0 or index >= len(favoritesList):
		return
	favoritesList.remove(favoritesList[index])
	common.WriteList(favoritesFile, favoritesList)
	xbmc.executebuiltin("Notification({0}, {1}, 5000, {2})".format(AddonName, common.GetLocaleString(30029), icon))
	xbmc.executebuiltin("XBMC.Container.Refresh()")

def ShowFavorties():
	favoritesList = common.ReadList(favoritesFile)
	nowEPG = []
	i = -1
	for favorite in favoritesList:
		i += 1
		u = favorite.encode("utf-8")
		prms = dict(urlparse.parse_qsl(u[u.find('?')+1:]))
		url = urllib.unquote_plus(prms.get('url', ''))
		mode = int(prms.get('mode','-1'))
		name = urllib.unquote_plus(prms.get('name', ''))
		iconimage = urllib.unquote_plus(prms.get('iconimage', ''))
		module = prms.get('module')
		moreData = urllib.unquote_plus(prms.get('moredata', ''))
		isFolder = prms.get('isFolder', 'False') == 'True'
		isPlayable = prms.get('isPlayable', 'False') == 'True'
		tvgID = prms.get('tvgID', '')
		contextMenu = [(common.GetLocaleString(30027), 'XBMC.RunPlugin({0}?url={1}&mode=9)'.format(sys.argv[0], i)),
			(common.GetLocaleString(30031), 'XBMC.RunPlugin({0}?mode=11&url={1}&moredata=-1)'.format(sys.argv[0], i)),
			(common.GetLocaleString(30032), 'XBMC.RunPlugin({0}?mode=11&url={1}&moredata=1)'.format(sys.argv[0], i)),
			(common.GetLocaleString(30033), 'XBMC.RunPlugin({0}?mode=11&url={1}&moredata=0)'.format(sys.argv[0], i))]
		if tvgID != '':
			if nowEPG == []:
				nowEPG = epg.GetNowEPG()
			programs = nowEPG.get(tvgID, [])
			LiveChannel(common.GetUnColor(name), url, mode, iconimage, module, contextMenu=contextMenu, bitrate=moreData, programs=programs, addFav=False)
		else:
			common.addDir(name, url, mode, iconimage, infos={"Title": name}, contextMenu=contextMenu, moreData=moreData, module=module, isFolder=isFolder, isPlayable=isPlayable, addFav=False)

def Search():
	series = common.GetUpdatedList(common.seriesFile, common.seriesUrl, isZip=True, sort=True)
	filteredSeries = []
	seriesLinks = []
	searchText = common.GetKeyboardText('מילים לחיפוש', '').strip().lower()
	if searchText == '':
		filteredSeries = series
	else:
		for serie in series:
			if serie['name'].lower().startswith(searchText):
				filteredSeries.append(serie)
				seriesLinks.append(serie['name'])
		for serie in series:
			if searchText in serie['name'].lower() and serie['name'] not in seriesLinks:
				filteredSeries.append(serie)
				seriesLinks.append(serie['name'])
	programNameFormat = int(Addon.getSetting("programNameFormat"))
	for serie in filteredSeries:
		moduleName = ''
		serieMoreData = serie.get('moreData', '')
		isFolder = True
		if serie['module'] == 'kan': 		
			if serie['mode'] == '2':
				if serieMoreData == 'youtube': 
					moduleName = common.GetLocaleString(30607)
					isFolder = False
				else: 
					moduleName = common.GetLocaleString(30602)
			elif serie['mode'] == '23':
				moduleName = serieMoreData
				serieMoreData = ''
			elif serie['mode'] == '32':
				moduleName = 'כאן פודקאסטים'
				serieMoreData = ''
		elif serie['module'] == 'keshet': 	moduleName = common.GetLocaleString(30603)
		elif serie['module'] == 'reshet': 	moduleName = common.GetLocaleString(30604)
		elif serie['module'] == 'ten': 		moduleName = common.GetLocaleString(30605)
		elif serie['module'] == 'twenty': 	moduleName = common.GetLocaleString(30606)
		elif serie['module'] == '9tv': 		moduleName = common.GetLocaleString(30630)
		elif serie['module'] == '891fm': 	moduleName = common.GetLocaleString(30734)
		elif serie['module'] == 'sport5': 	moduleName = common.GetLocaleString(30632)
		elif serie['module'] == 'sport1': 	moduleName = common.GetLocaleString(31000)
		name = common.getDisplayName(serie['name'], moduleName, programNameFormat, bold=True)
		infos = {"Title": name, "Plot": serie['desc']}
		common.addDir(name, serie['url'], serie['mode'], serie['icon'].encode('utf-8'), infos, module=serie['module'], moreData=serieMoreData, totalItems=len(filteredSeries), isFolder=isFolder)

def PlayLive(id):
	channel = None
	channels = baseChannels.TvChannels + baseChannels.RadioChannels
	for ch in channels:
		if ch.get('ch') == id: 
			channel = ch
			break
	if channel is None:
		return
	nowEPG = epg.GetNowEPG()
	programs = [] if channel.get('tvgID', '') == '' else nowEPG.get(channel['tvgID'], [])
	channelNameFormat = int(Addon.getSetting("channelNameFormat"))
	displayName = common.GetLabelColor(common.GetLocaleString(channel['nameID']), keyColor="chColor", bold=True)
	iconimage = os.path.join(imagesDir, channel['image'])
	
	if len(programs) > 0:
		programTime = common.GetLabelColor("[{0}-{1}]".format(datetime.datetime.fromtimestamp(programs[0]["start"]).strftime('%H:%M'), datetime.datetime.fromtimestamp(programs[0]["end"]).strftime('%H:%M')), keyColor="timesColor")
		programName = common.GetLabelColor(programs[0]["name"].encode('utf-8'), keyColor="prColor", bold=True)
		displayName = GetChannelName(programName, programTime, displayName, channelNameFormat)
	if channel.get('resKey', '') == '':
		bitrate = 'best'
	else:
		bitrate = Addon.getSetting(channel['resKey'])
		if bitrate == '':
			bitrate = 'best'
	try:
		module = channel['module']
		moduleScript = __import__('resources.lib.{0}'.format(module), fromlist=[module])
		moduleScript.Run(displayName, channel['channelID'], channel['mode'], iconimage, bitrate)
	except Exception as ex:
		xbmc.log(str(ex), 3)

if module is None:
	if mode == -1:
		GetCategoriesList()
	elif mode == 1:
		LiveChannels()
	elif mode == 2:
		VODs()
	elif mode == 3:
		Radios()
	elif mode == 12:
		RadioVODs()
	elif mode == 4:
		Search()
	elif mode == 5:
		PlayLive(url)
	elif mode == 6:
		p = moreData.split(';')
		xbmc.executebuiltin('{0}({1})'.format(url, p[0]))
		if p[-1] != 'noexit':
			sys.exit()
	elif mode == 7:
		MakeIPTVfiles()
		sys.exit()
	elif mode == 8:
		AddFavorite(url)
		sys.exit()
	elif mode == 9:
		RemoveFavortie(int(url))
		sys.exit()
	elif mode == 10:
		ShowFavorties()
	elif mode == 11:
		common.MoveInList(int(url), int(moreData), favoritesFile)
	elif mode == 13:
		Podcasts()
	if mode == 1 or mode == 3 or mode == 10:
		common.SetViewMode('episodes')
else:
	try:
		moduleScript = __import__('resources.lib.{0}'.format(module), fromlist=[module])
		moduleScript.Run(name, url, mode, iconimage, moreData)
	except Exception as ex:
		xbmc.log(str(ex), 3)
		import traceback
		ex_type, ex, tb = sys.exc_info()
		xbmc.log(str(ex_type), 3)
		del tb

xbmcplugin.endOfDirectory(handle)