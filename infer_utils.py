from v230_onnx_infer import OnnxInferenceSession
from text import cleaned_text_to_sequence, get_bert
from text.cleaner import clean_text
import commons
import torch
from sentence import split_by_language
import numpy as np
import re_matching
import pyloudnorm
from pydub import AudioSegment


def normalize_loudness(y: np.ndarray, fs: int, target_loudness=-23) -> np.ndarray:
    meter = pyloudnorm.Meter(fs)
    loudness = meter.integrated_loudness(y)
    normalized = pyloudnorm.normalize.loudness(y, loudness, target_loudness)
    return normalized


session = OnnxInferenceSession(
    {
        "enc": "onnx/BertVITS2.3PT/BertVITS2.3PT_enc_p.onnx",
        "emb_g": "onnx/BertVITS2.3PT/BertVITS2.3PT_emb.onnx",
        "dp": "onnx/BertVITS2.3PT/BertVITS2.3PT_dp.onnx",
        "sdp": "onnx/BertVITS2.3PT/BertVITS2.3PT_sdp.onnx",
        "flow": "onnx/BertVITS2.3PT/BertVITS2.3PT_flow.onnx",
        "dec": "onnx/BertVITS2.3PT/BertVITS2.3PT_dec.onnx",
    },
    Providers=["CPUExecutionProvider"],
)


def get_text(text, language_str, add_blank: bool, style_text=None, style_weight=0.7):
    style_text = None if style_text == "" else style_text
    # 在此处实现当前版本的get_text
    norm_text, phone, tone, word2ph = clean_text(text, language_str)
    phone, tone, language = cleaned_text_to_sequence(phone, tone, language_str)

    if add_blank:
        phone = commons.intersperse(phone, 0)
        tone = commons.intersperse(tone, 0)
        language = commons.intersperse(language, 0)
        for i in range(len(word2ph)):
            word2ph[i] = word2ph[i] * 2
        word2ph[0] += 1
    bert_ori = get_bert(norm_text, word2ph, language_str, style_text, style_weight)
    del word2ph
    assert bert_ori.shape[-1] == len(phone), phone

    if language_str == "ZH":
        bert = bert_ori
        ja_bert = torch.randn(1024, len(phone))
        en_bert = torch.randn(1024, len(phone))
    elif language_str == "JP":
        bert = torch.randn(1024, len(phone))
        ja_bert = bert_ori
        en_bert = torch.randn(1024, len(phone))
    elif language_str == "EN":
        bert = torch.randn(1024, len(phone))
        ja_bert = torch.randn(1024, len(phone))
        en_bert = bert_ori
    else:
        raise ValueError("language_str should be ZH, JP or EN")

    assert bert.shape[-1] == len(
        phone
    ), f"Bert seq len {bert.shape[-1]} != {len(phone)}"

    phone = torch.LongTensor(phone)
    tone = torch.LongTensor(tone)
    language = torch.LongTensor(language)
    return bert, ja_bert, en_bert, phone, tone, language


def infer_multilang(
    text,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    sid,
    language,
    skip_start=False,
    skip_end=False,
):
    bert, ja_bert, en_bert, phones, tones, lang_ids = [], [], [], [], [], []
    for idx, (txt, lang) in enumerate(zip(text, language)):
        _skip_start = (idx != 0) or (skip_start and idx == 0)
        _skip_end = (idx != len(language) - 1) or skip_end
        (
            temp_bert,
            temp_ja_bert,
            temp_en_bert,
            temp_phones,
            temp_tones,
            temp_lang_ids,
        ) = get_text(txt, lang, add_blank=True)
        if _skip_start:
            temp_bert = temp_bert[:, 3:]
            temp_ja_bert = temp_ja_bert[:, 3:]
            temp_en_bert = temp_en_bert[:, 3:]
            temp_phones = temp_phones[3:]
            temp_tones = temp_tones[3:]
            temp_lang_ids = temp_lang_ids[3:]
        if _skip_end:
            temp_bert = temp_bert[:, :-2]
            temp_ja_bert = temp_ja_bert[:, :-2]
            temp_en_bert = temp_en_bert[:, :-2]
            temp_phones = temp_phones[:-2]
            temp_tones = temp_tones[:-2]
            temp_lang_ids = temp_lang_ids[:-2]
        bert.append(temp_bert)
        ja_bert.append(temp_ja_bert)
        en_bert.append(temp_en_bert)
        phones.append(temp_phones)
        tones.append(temp_tones)
        lang_ids.append(temp_lang_ids)
    bert = torch.concatenate(bert, dim=1)
    ja_bert = torch.concatenate(ja_bert, dim=1)
    en_bert = torch.concatenate(en_bert, dim=1)
    phones = torch.concatenate(phones, dim=0)
    tones = torch.concatenate(tones, dim=0)
    lang_ids = torch.concatenate(lang_ids, dim=0)

    x_tst = phones.numpy()
    tones = tones.numpy()
    lang_ids = lang_ids.numpy()
    bert = bert.transpose(0, 1).numpy()
    ja_bert = ja_bert.transpose(0, 1).numpy()
    en_bert = en_bert.transpose(0, 1).numpy()
    x_tst_lengths = torch.LongTensor([phones.size(0)]).numpy()
    speakers = torch.LongTensor([sid]).numpy()

    audio = session(x_tst, tones, lang_ids, bert, ja_bert, en_bert, speakers)
    return audio


def generate_audio_multilang(
    slices,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    speaker,
    language,
    skip_start=False,
    skip_end=False,
):
    audio_list = []
    for idx, piece in enumerate(slices):
        skip_start = idx != 0
        skip_end = idx != len(slices) - 1
        audio = infer_multilang(
            piece,
            sdp_ratio=sdp_ratio,
            noise_scale=noise_scale,
            noise_scale_w=noise_scale_w,
            length_scale=length_scale,
            sid=speaker,
            language=language[idx],
            skip_start=skip_start,
            skip_end=skip_end,
        ).squeeze()
        audio_list.append(audio)
    return audio_list


def process_auto(text):
    _text, _lang = [], []
    for slice in text.split("|"):
        if slice == "":
            continue
        temp_text, temp_lang = [], []
        sentences_list = split_by_language(slice, target_languages=["zh", "ja", "en"])
        for sentence, lang in sentences_list:
            if sentence == "":
                continue
            temp_text.append(sentence)
            if lang == "ja":
                lang = "jp"
            temp_lang.append(lang.upper())
        _text.append(temp_text)
        _lang.append(temp_lang)
    return _text, _lang


def process_text(
    text: str,
    speaker,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
):
    _text, _lang = process_auto(text)
    print(f"Text: {_text}\nLang: {_lang}")
    return generate_audio_multilang(
        _text,
        sdp_ratio,
        noise_scale,
        noise_scale_w,
        length_scale,
        speaker,
        _lang,
    )


def format_utils(text, speaker):
    _text, _lang = process_auto(text)
    res = f"[{speaker}]"
    for lang_s, content_s in zip(_lang, _text):
        for lang, content in zip(lang_s, content_s):
            res += f"<{lang.lower()}>{content}"
        res += "|"
    return "mix", res[:-1]


# faster, lower quality
def tts_fn(
    text: str,
    speaker=0,
    sdp_ratio=0.5,
    noise_scale=0.6,
    noise_scale_w=0.9,
    length_scale=1.0,
):
    audio_list = process_text(
        text,
        speaker,
        sdp_ratio,
        noise_scale,
        noise_scale_w,
        length_scale,
    )

    audio_concat = np.concatenate(audio_list)
    return audio_concat


# slower, higher quality
def tts_split(
    text: str,
    speaker=0,
    sdp_ratio=0.5,
    noise_scale=0.6,
    noise_scale_w=0.9,
    length_scale=1.0,
    cut_by_sent=False,
    interval_between_para=1,
    interval_between_sent=0.2,
):
    # while text.find("\n\n") != -1:
    #     text = text.replace("\n\n", "\n")
    text = text.replace("\n", " ")
    text = text.replace("|", "")
    para_list = re_matching.cut_para(text)
    para_list = [p for p in para_list if p != ""]
    audio_list = []
    for p in para_list:
        if not cut_by_sent:
            audio_list.extend(
                process_text(
                    p,
                    speaker,
                    sdp_ratio,
                    noise_scale,
                    noise_scale_w,
                    length_scale,
                )
            )
            # silence = np.zeros(int(44100 * interval_between_para), dtype=np.int16)
            # audio_list.append(silence)
        else:
            audio_list_sent = []
            sent_list = re_matching.cut_sent(p)
            sent_list = [s for s in sent_list if s != ""]
            for s in sent_list:
                audio_list_sent += process_text(
                    s,
                    speaker,
                    sdp_ratio,
                    noise_scale,
                    noise_scale_w,
                    length_scale,
                )
                # silence = np.zeros((int)(44100 * interval_between_sent))
                # audio_list_sent.append(silence)
            if (interval_between_para - interval_between_sent) > 0:
                silence = np.zeros(
                    (int)(44100 * (interval_between_para - interval_between_sent))
                )
                audio_list_sent.append(silence)
            audio_list.append(audio_list_sent)
    audio_concat = np.concatenate(audio_list)
    return normalize_loudness(audio_concat, 44100)


# make sure all model is loaded to avoid cold start
tts_split("你好，hello，こんにちは")

if __name__ == "__main__":
    print("init ready")
    import soundfile

    audio = tts_split("谢谢咖啡店的猫耳君的SC")

    with open("test.wav", "wb") as f:
        soundfile.write(f, audio.squeeze(), 44100, format="WAV")
