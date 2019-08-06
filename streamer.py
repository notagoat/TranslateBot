import re
from google.cloud import translate
from mastodon import Mastodon, StreamListener

isolist = ["aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv", "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd", "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb", "lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru", "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"]

mastodon = Mastodon(
    access_token = "",
    api_base_url = "",
)

def cleanhtml(content):
	cleanregex = re.compile('<.*?>')
	cleancontent = re.sub(cleanregex,'', content)
	return cleancontent

def translater(content,target,translate_client):
	translation = translate_client.translate(content,target_language=target)
	return translation

class myListener(StreamListener):
	def on_notification(self, notification):
		print("Notification Recieved!")
		if not notification["type"] == "mention":
			print("Not a mention, Moving on...")
			return
		translate_client = translate.Client() #instantiate that motherfucker
		reply = notification["status"]["in_reply_to_id"] #Fetch the reply
		if reply == None:
			print("No Reply Found")
			mastodon.status_post("Error! No Reply Found",in_reply_to_id=notification["status"]["id"])
			return
		target = cleanhtml(notification["status"]["content"])
		if target[-2:] in isolist:
			print("Target Found: %s" %target[-2:])
			target = target[-2:]
		else:
			print("Target Not Found: %s" %target[-2:])
			mastodon.status_post("Error! Could not find ISO country code. Please make sure it is at the end of the reply.",in_reply_to_id=notification["status"]["id"])
			return

		toot = mastodon.status(notification["status"]["in_reply_to_id"])#Get the replied too too content
		content = cleanhtml(toot["content"]) #Clean the content for translation
		print("Content is, '%s'" %content)
		
		output = translater(content,target,translate_client)
		print("Output is, '%s'" %output["translatedText"])

		finaloutput = "@" + notification["account"]["acct"] + " " + output["translatedText"] 

		mastodon.status_post(finaloutput,in_reply_to_id=notification["status"]["id"])

listener = myListener()
mastodon.stream_user(listener)
