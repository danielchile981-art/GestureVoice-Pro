"""Gera assets originais de marca, mockups de loja e ícones Android. Python + Pillow."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, random

ROOT = Path(__file__).resolve().parent
STORE = ROOT / 'store'
RES = ROOT.parent / 'app/src/main/res'
STORE.mkdir(exist_ok=True)
random.seed(7)
CYAN=(0,229,255); VIOLET=(124,77,255); PINK=(255,46,147); NIGHT=(11,15,26); CARD=(19,26,43)
FONTS=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
def font(size,bold=False): return ImageFont.truetype(FONTS[0 if bold else 1],size)
def blend(a,b,t): return tuple(int(x*(1-t)+y*t) for x,y in zip(a,b))
def gradient(w,h,mode='dark'):
    im=Image.new('RGB',(w,h)); p=im.load()
    for y in range(h):
        for x in range(w):
            t=(x/w+y/h)/2
            if mode=='brand': c=blend(blend(CYAN,VIOLET,min(t*1.7,1)),PINK,max((t-.55)*1.8,0))
            else: c=blend(NIGHT,(27,19,64),t*.55)
            p[x,y]=c
    return im
def glow(draw,xy,r,color,alpha=130):
    layer=Image.new('RGBA',draw.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    d.ellipse((xy[0]-r,xy[1]-r,xy[0]+r,xy[1]+r),fill=(*color,alpha))
    return layer.filter(ImageFilter.GaussianBlur(r//2))
def icon(n):
    im=gradient(n,n,'brand').convert('RGBA')
    layer=Image.new('RGBA',im.size); d=ImageDraw.Draw(layer)
    c=n/2
    # mão simplificada e espiral gestual
    points=[(.31,.70),(.31,.47),(.33,.40),(.37,.43),(.38,.58),(.40,.31),(.44,.28),(.47,.32),(.47,.54),(.50,.25),(.55,.25),(.57,.30),(.55,.53),(.59,.33),(.64,.33),(.66,.38),(.62,.60),(.70,.48),(.74,.50),(.72,.63),(.63,.75),(.47,.78),(.36,.75)]
    q=[(int(x*n),int(y*n)) for x,y in points]
    d.line(q,fill=(255,255,255,245),width=max(3,n//42),joint='curve')
    for x,y in q[1:-1:3]: d.ellipse((x-n//95,y-n//95,x+n//95,y+n//95),fill=(255,255,255,245))
    spiral=[]
    for i in range(140):
        a=i*.08; r=n*(.02+.0013*i)
        spiral.append((int(.52*n+math.cos(a)*r),int(.48*n+math.sin(a)*r)))
    d.line(spiral,fill=(0,255,221,230),width=max(3,n//65),joint='curve')
    for j in (0,1,2):
        box=(int((.70+j*.06)*n),int((.23-j*.04)*n),int((.88+j*.04)*n),int((.75+j*.04)*n))
        d.arc(box,270,90,fill=(255,255,255,230-j*50),width=max(3,n//75))
    im=Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(n//90)))
    im=Image.alpha_composite(im,layer)
    return im.convert('RGB')
icon(512).save(STORE/'icon-512.png')
for density,size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    folder=RES/f'mipmap-{density}'; folder.mkdir(exist_ok=True)
    icon(size).save(folder/'ic_launcher.png')
(RES/'mipmap-anydpi-v26'/'ic_launcher.xml').write_text('<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/night"/><foreground android:drawable="@drawable/ic_launcher_foreground"/></adaptive-icon>')
icon(432).save(RES/'drawable'/'ic_launcher_foreground.png')

feature=gradient(1024,500).convert('RGBA'); d=ImageDraw.Draw(feature)
for x in range(0,1024,38): d.line((x,0,x,500),fill=(34,42,76,90),width=1)
for y in range(0,500,38): d.line((0,y,1024,y),fill=(34,42,76,90),width=1)
d.text((55,108),'GestureVoice',font=font(58,True),fill='white')
d.text((57,193),'Desenhe. Fale. Controle.',font=font(25),fill=CYAN)
d.rounded_rectangle((54,275,435,359),radius=30,outline=CYAN,width=3)
d.text((79,301),'Seus gestos. Sua voz.',font=font(21,True),fill='white')
for x,y,angle in [(618,75,-10),(793,103,8)]:
    phone=Image.new('RGBA',(174,350)); pd=ImageDraw.Draw(phone)
    pd.rounded_rectangle((0,0,172,348),radius=31,fill=(7,12,24),outline=(115,103,199),width=4)
    pd.rounded_rectangle((11,20,161,329),radius=19,fill=CARD)
    pd.text((23,38),'GESTURE',font=font(15,True),fill='white')
    if x<700:
        pts=[(34,237),(41,180),(70,162),(94,187),(118,128),(139,123)]
        pd.line(pts,fill=CYAN,width=8,joint='curve')
        pd.text((27,264),'Criar gesto',font=font(13),fill='white')
    else:
        for i in range(20):
            h=int(8+50*abs(math.sin(i*.5))**2); pd.rounded_rectangle((22+i*6,176-h,25+i*6,176+h),radius=3,fill=blend(CYAN,VIOLET,i/20))
        pd.text((35,263),'Ouvindo...',font=font(13),fill='white')
    phone=phone.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    feature.alpha_composite(phone,(x,y))
for _ in range(70):
    x=random.randrange(1024); y=random.randrange(500); r=random.choice([1,2,3]); d.ellipse((x-r,y-r,x+r,y+r),fill=(*CYAN,random.randrange(65,175)))
feature.convert('RGB').save(STORE/'feature-1024x500.png')

screens=[
    ('Crie gestos na tela','Desenhe e salve seu traço','CRIAR GESTO','Desenhe seu gesto'),
    ('Ative com sua voz','Uma frase aciona o gesto','GATILHOS','“abrir menu”'),
    ('Tudo organizado','Sua biblioteca de gestos','BIBLIOTECA','Meus gestos'),
    ('Seu controle, sempre','Ative a escuta quando quiser','ATIVAR','Escuta no dispositivo'),
    ('Do seu jeito','Escolha cores e aparência','PERSONALIZAR','Seu estilo'),
    ('Veja sua atividade','Histórico local no aparelho','ESTATÍSTICAS','12 execuções'),
]
for index,(headline,sub,section,cardtitle) in enumerate(screens,1):
    im=gradient(1080,1920).convert('RGB'); d=ImageDraw.Draw(im)
    d.text((75,118),headline,font=font(66,True),fill='white'); d.text((79,225),sub,font=font(34),fill=CYAN)
    d.rounded_rectangle((72,380,1008,1780),radius=72,fill=(4,8,16),outline=(113,85,206),width=8)
    d.rounded_rectangle((94,409,985,1745),radius=52,fill=CARD)
    d.text((145,468),'✦  GESTUREVOICE',font=font(30,True),fill=CYAN)
    d.text((146,608),section,font=font(44,True),fill='white')
    d.text((149,686),cardtitle,font=font(30),fill=(168,178,199))
    d.rounded_rectangle((145,783,930,1410),radius=34,fill=(26,35,62),outline=(39,61,91),width=3)
    if index==1:
        pts=[(220,1215),(270,1000),(420,935),(600,1090),(790,890)]
        d.line(pts,fill=CYAN,width=35,joint='curve'); d.line(pts,fill='white',width=6,joint='curve')
    elif index==2:
        for j in range(32):
            h=int(18+120*abs(math.sin(j*.72))**2); x=194+j*21
            d.rounded_rectangle((x,1090-h,x+9,1090+h),radius=5,fill=blend(CYAN,VIOLET,j/32))
    elif index==3:
        for j,label in enumerate(['Zigue-zague','Deslizar','Círculo','Atalho']):
            x=176+(j%2)*370; y=824+(j//2)*255
            d.rounded_rectangle((x,y,x+340,y+225),radius=30,fill=blend((26,44,73),VIOLET,j/9))
            d.arc((x+105,y+30,x+210,y+130),15,300,fill=CYAN,width=12)
            d.text((x+36,y+160),label,font=font(27,True),fill='white')
    elif index==4:
        d.ellipse((383,870,688,1175),outline=CYAN,width=15)
        d.polygon([(510,940),(510,1100),(628,1020)],fill=CYAN)
        d.text((305,1260),'ATIVAR ESCUTA',font=font(29,True),fill='white')
    elif index==5:
        for j,c in enumerate([CYAN,VIOLET,PINK,(0,255,163)]):
            x=200+j*180; d.ellipse((x,925,x+125,1050),fill=c)
        d.text((235,1175),'Escuro  •  Claro  •  Auto',font=font(28),fill='white')
    else:
        values=[50,100,75,170,130,235,280]; pts=[(210+j*100,1320-v) for j,v in enumerate(values)]
        d.line(pts,fill=CYAN,width=12,joint='curve')
        for x,y in pts: d.ellipse((x-10,y-10,x+10,y+10),fill='white')
    d.rounded_rectangle((172,1515,904,1625),radius=52,fill=VIOLET)
    d.text((260,1549),'Seus gestos. Sua voz.',font=font(28,True),fill='white')
    d.text((90,1840),'MOCKUP CONCEITUAL • NÃO É CAPTURA DO APP',font=font(18),fill=(140,150,173))
    im.save(STORE/f'screenshot-{index:02d}-1080x1920.png')
print('generated', len(list(STORE.glob('*.png'))), 'store pngs')
