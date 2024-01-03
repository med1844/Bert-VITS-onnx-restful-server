import re

import cn2an
from pypinyin import lazy_pinyin, Style

from text.symbols import punctuation
from text.tone_sandhi import ToneSandhi

opencpop_strict = """a	AA a
ai	AA ai
an	AA an
ang	AA ang
ao	AA ao
ba	b a
bai	b ai
ban	b an
bang	b ang
bao	b ao
bei	b ei
ben	b en
beng	b eng
bi	b i
bian	b ian
biao	b iao
bie	b ie
bin	b in
bing	b ing
bo	b o
bu	b u
ca	c a
cai	c ai
can	c an
cang	c ang
cao	c ao
ce	c e
cei	c ei
cen	c en
ceng	c eng
cha	ch a
chai	ch ai
chan	ch an
chang	ch ang
chao	ch ao
che	ch e
chen	ch en
cheng	ch eng
chi	ch ir
chong	ch ong
chou	ch ou
chu	ch u
chua	ch ua
chuai	ch uai
chuan	ch uan
chuang	ch uang
chui	ch ui
chun	ch un
chuo	ch uo
ci	c i0
cong	c ong
cou	c ou
cu	c u
cuan	c uan
cui	c ui
cun	c un
cuo	c uo
da	d a
dai	d ai
dan	d an
dang	d ang
dao	d ao
de	d e
dei	d ei
den	d en
deng	d eng
di	d i
dia	d ia
dian	d ian
diao	d iao
die	d ie
ding	d ing
diu	d iu
dong	d ong
dou	d ou
du	d u
duan	d uan
dui	d ui
dun	d un
duo	d uo
e	EE e
ei	EE ei
en	EE en
eng	EE eng
er	EE er
fa	f a
fan	f an
fang	f ang
fei	f ei
fen	f en
feng	f eng
fo	f o
fou	f ou
fu	f u
ga	g a
gai	g ai
gan	g an
gang	g ang
gao	g ao
ge	g e
gei	g ei
gen	g en
geng	g eng
gong	g ong
gou	g ou
gu	g u
gua	g ua
guai	g uai
guan	g uan
guang	g uang
gui	g ui
gun	g un
guo	g uo
ha	h a
hai	h ai
han	h an
hang	h ang
hao	h ao
he	h e
hei	h ei
hen	h en
heng	h eng
hong	h ong
hou	h ou
hu	h u
hua	h ua
huai	h uai
huan	h uan
huang	h uang
hui	h ui
hun	h un
huo	h uo
ji	j i
jia	j ia
jian	j ian
jiang	j iang
jiao	j iao
jie	j ie
jin	j in
jing	j ing
jiong	j iong
jiu	j iu
ju	j v
jv	j v
juan	j van
jvan	j van
jue	j ve
jve	j ve
jun	j vn
jvn	j vn
ka	k a
kai	k ai
kan	k an
kang	k ang
kao	k ao
ke	k e
kei	k ei
ken	k en
keng	k eng
kong	k ong
kou	k ou
ku	k u
kua	k ua
kuai	k uai
kuan	k uan
kuang	k uang
kui	k ui
kun	k un
kuo	k uo
la	l a
lai	l ai
lan	l an
lang	l ang
lao	l ao
le	l e
lei	l ei
leng	l eng
li	l i
lia	l ia
lian	l ian
liang	l iang
liao	l iao
lie	l ie
lin	l in
ling	l ing
liu	l iu
lo	l o
long	l ong
lou	l ou
lu	l u
luan	l uan
lun	l un
luo	l uo
lv	l v
lve	l ve
ma	m a
mai	m ai
man	m an
mang	m ang
mao	m ao
me	m e
mei	m ei
men	m en
meng	m eng
mi	m i
mian	m ian
miao	m iao
mie	m ie
min	m in
ming	m ing
miu	m iu
mo	m o
mou	m ou
mu	m u
na	n a
nai	n ai
nan	n an
nang	n ang
nao	n ao
ne	n e
nei	n ei
nen	n en
neng	n eng
ni	n i
nian	n ian
niang	n iang
niao	n iao
nie	n ie
nin	n in
ning	n ing
niu	n iu
nong	n ong
nou	n ou
nu	n u
nuan	n uan
nun	n un
nuo	n uo
nv	n v
nve	n ve
o	OO o
ou	OO ou
pa	p a
pai	p ai
pan	p an
pang	p ang
pao	p ao
pei	p ei
pen	p en
peng	p eng
pi	p i
pian	p ian
piao	p iao
pie	p ie
pin	p in
ping	p ing
po	p o
pou	p ou
pu	p u
qi	q i
qia	q ia
qian	q ian
qiang	q iang
qiao	q iao
qie	q ie
qin	q in
qing	q ing
qiong	q iong
qiu	q iu
qu	q v
qv	q v
quan	q van
qvan	q van
que	q ve
qve	q ve
qun	q vn
qvn	q vn
ran	r an
rang	r ang
rao	r ao
re	r e
ren	r en
reng	r eng
ri	r ir
rong	r ong
rou	r ou
ru	r u
rua	r ua
ruan	r uan
rui	r ui
run	r un
ruo	r uo
sa	s a
sai	s ai
san	s an
sang	s ang
sao	s ao
se	s e
sen	s en
seng	s eng
sha	sh a
shai	sh ai
shan	sh an
shang	sh ang
shao	sh ao
she	sh e
shei	sh ei
shen	sh en
sheng	sh eng
shi	sh ir
shou	sh ou
shu	sh u
shua	sh ua
shuai	sh uai
shuan	sh uan
shuang	sh uang
shui	sh ui
shun	sh un
shuo	sh uo
si	s i0
song	s ong
sou	s ou
su	s u
suan	s uan
sui	s ui
sun	s un
suo	s uo
ta	t a
tai	t ai
tan	t an
tang	t ang
tao	t ao
te	t e
tei	t ei
teng	t eng
ti	t i
tian	t ian
tiao	t iao
tie	t ie
ting	t ing
tong	t ong
tou	t ou
tu	t u
tuan	t uan
tui	t ui
tun	t un
tuo	t uo
wa	w a
wai	w ai
wan	w an
wang	w ang
wei	w ei
wen	w en
weng	w eng
wo	w o
wu	w u
xi	x i
xia	x ia
xian	x ian
xiang	x iang
xiao	x iao
xie	x ie
xin	x in
xing	x ing
xiong	x iong
xiu	x iu
xu	x v
xv	x v
xuan	x van
xvan	x van
xue	x ve
xve	x ve
xun	x vn
xvn	x vn
ya	y a
yan	y En
yang	y ang
yao	y ao
ye	y E
yi	y i
yin	y in
ying	y ing
yo	y o
yong	y ong
you	y ou
yu	y v
yv	y v
yuan	y van
yvan	y van
yue	y ve
yve	y ve
yun	y vn
yvn	y vn
za	z a
zai	z ai
zan	z an
zang	z ang
zao	z ao
ze	z e
zei	z ei
zen	z en
zeng	z eng
zha	zh a
zhai	zh ai
zhan	zh an
zhang	zh ang
zhao	zh ao
zhe	zh e
zhei	zh ei
zhen	zh en
zheng	zh eng
zhi	zh ir
zhong	zh ong
zhou	zh ou
zhu	zh u
zhua	zh ua
zhuai	zh uai
zhuan	zh uan
zhuang	zh uang
zhui	zh ui
zhun	zh un
zhuo	zh uo
zi	z i0
zong	z ong
zou	z ou
zu	z u
zuan	z uan
zui	z ui
zun	z un
zuo	z uo"""

pinyin_to_symbol_map = {
    line.split("\t")[0]: line.strip().split("\t")[1]
    for line in opencpop_strict.split("\n")
}

import jieba
import jieba.posseg as psg

jieba.dt.tmp_dir = "."


rep_map = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "·": ",",
    "、": ",",
    "...": "…",
    "$": ".",
    "“": "'",
    "”": "'",
    '"': "'",
    "‘": "'",
    "’": "'",
    "（": "'",
    "）": "'",
    "(": "'",
    ")": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "～": "-",
    "~": "-",
    "「": "'",
    "」": "'",
}

tone_modifier = ToneSandhi()


def replace_punctuation(text):
    text = text.replace("嗯", "恩").replace("呣", "母")
    pattern = re.compile("|".join(re.escape(p) for p in rep_map.keys()))

    replaced_text = pattern.sub(lambda x: rep_map[x.group()], text)

    replaced_text = re.sub(
        r"[^\u4e00-\u9fa5" + "".join(punctuation) + r"]+", "", replaced_text
    )

    return replaced_text


def g2p(text):
    pattern = r"(?<=[{0}])\s*".format("".join(punctuation))
    sentences = [i for i in re.split(pattern, text) if i.strip() != ""]
    phones, tones, word2ph = _g2p(sentences)
    assert sum(word2ph) == len(phones)
    assert len(word2ph) == len(text)  # Sometimes it will crash,you can add a try-catch.
    phones = ["_"] + phones + ["_"]
    tones = [0] + tones + [0]
    word2ph = [1] + word2ph + [1]
    return phones, tones, word2ph


def _get_initials_finals(word):
    initials = []
    finals = []
    orig_initials = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.INITIALS)
    orig_finals = lazy_pinyin(
        word, neutral_tone_with_five=True, style=Style.FINALS_TONE3
    )
    for c, v in zip(orig_initials, orig_finals):
        initials.append(c)
        finals.append(v)
    return initials, finals


def _g2p(segments):
    phones_list = []
    tones_list = []
    word2ph = []
    for seg in segments:
        # Replace all English words in the sentence
        seg = re.sub("[a-zA-Z]+", "", seg)
        seg_cut = psg.lcut(seg)
        initials = []
        finals = []
        seg_cut = tone_modifier.pre_merge_for_modify(seg_cut)
        for word, pos in seg_cut:
            if pos == "eng":
                continue
            sub_initials, sub_finals = _get_initials_finals(word)
            sub_finals = tone_modifier.modified_tone(word, pos, sub_finals)
            initials.append(sub_initials)
            finals.append(sub_finals)

            # assert len(sub_initials) == len(sub_finals) == len(word)
        initials = sum(initials, [])
        finals = sum(finals, [])
        #
        for c, v in zip(initials, finals):
            raw_pinyin = c + v
            # NOTE: post process for pypinyin outputs
            # we discriminate i, ii and iii
            if c == v:
                assert c in punctuation
                phone = [c]
                tone = "0"
                word2ph.append(1)
            else:
                v_without_tone = v[:-1]
                tone = v[-1]

                pinyin = c + v_without_tone
                assert tone in "12345"

                if c:
                    # 多音节
                    v_rep_map = {
                        "uei": "ui",
                        "iou": "iu",
                        "uen": "un",
                    }
                    if v_without_tone in v_rep_map.keys():
                        pinyin = c + v_rep_map[v_without_tone]
                else:
                    # 单音节
                    pinyin_rep_map = {
                        "ing": "ying",
                        "i": "yi",
                        "in": "yin",
                        "u": "wu",
                    }
                    if pinyin in pinyin_rep_map.keys():
                        pinyin = pinyin_rep_map[pinyin]
                    else:
                        single_rep_map = {
                            "v": "yu",
                            "e": "e",
                            "i": "y",
                            "u": "w",
                        }
                        if pinyin[0] in single_rep_map.keys():
                            pinyin = single_rep_map[pinyin[0]] + pinyin[1:]

                assert pinyin in pinyin_to_symbol_map.keys(), (pinyin, seg, raw_pinyin)
                phone = pinyin_to_symbol_map[pinyin].split(" ")
                word2ph.append(len(phone))

            phones_list += phone
            tones_list += [int(tone)] * len(phone)
    return phones_list, tones_list, word2ph


def text_normalize(text):
    numbers = re.findall(r"\d+(?:\.?\d+)?", text)
    for number in numbers:
        text = text.replace(number, cn2an.an2cn(number), 1)
    text = replace_punctuation(text)
    return text


def get_bert_feature(text, word2ph):
    from text import chinese_bert

    return chinese_bert.get_bert_feature(text, word2ph)


if __name__ == "__main__":
    from text.chinese_bert import get_bert_feature

    text = "啊！但是《原神》是由,米哈\游自主，  [研发]的一款全.新开放世界.冒险游戏"
    text = text_normalize(text)
    print(text)
    phones, tones, word2ph = g2p(text)
    bert = get_bert_feature(text, word2ph)

    print(phones, tones, word2ph, bert.shape)


# # 示例用法
# text = "这是一个示例文本：,你好！这是一个测试...."
# print(g2p_paddle(text))  # 输出: 这是一个示例文本你好这是一个测试
