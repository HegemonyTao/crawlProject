#生成对应表
from fontTools.ttLib import TTFont
font_1 = TTFont('douyin.ttf')
font_1.saveXML('font_1.xml')