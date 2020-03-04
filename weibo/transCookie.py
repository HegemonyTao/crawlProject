#进行json文本的转换
import json
text=''''''
jsonText=json.loads(text)
cookieDict={}
for item in jsonText:
    cookieDict[item['name']]=item['value']
print(cookieDict)