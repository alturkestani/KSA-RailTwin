> **Document version:** film/script/pronunciation.md v1.1 | 7 Nov 2026 | Author: R10 builder (v1.1: FIX_CP8_NOTES item 7, the Saudi number-word example now matches 1,250); documentary-director (R10) | Status: draft (CP8)

# Pronunciation guide for the narration (both cuts and trailers)

Every place name used in `film/script/lines.csv` (main cut and trailer, Arabic and English), with the Arabic spelling used in the Arabic script, the English spelling used in the English script, a simple transliteration with the **stressed syllable in capitals**, and notes for the voice step. Stress marks are the author's judgement of common Saudi pronunciation and go to the native reviewer with the script (`native_review: pending`); nothing here is final until the reviewer initials it.

How to use it: the voice step (`voice-audio`) builds a spoken (`say`) text for each line. Where a TTS engine mispronounces a name, it puts the respelling from the last column into the spoken text only; the script and subtitles keep the spelling in the first two columns.

## 1. Place names

| Arabic (script) | English (script) | transliteration, stress | notes for TTS |
|---|---|---|---|
| الرياض | Riyadh | ar-ri-YAADH | The ClArTTS voice read «بلياض» (`film/voice/README.md`); check the definite article is kept. English: "ree-YAAD". |
| جدة | Jeddah | JID-da | Saudi speech says "Jidda" (short i), not "Jedda". English respelling if needed: "JID-dah". |
| القريات | Qurayyat | al-gu-RAY-yaat | Najdi/northern speech often has /g/ for ق ("Gurayyat"; the airport code URY and Wikipedia's "Gurayat" reflect it). English TTS (Kokoro af_heart) was heard as "Quraayat" and am_michael as "Quraia" (`film/voice/README.md`): respell "Qu-RAI-yaat" and check by ear. |
| أبها | Abha | AB-ha | ClArTTS read «أبهة»; am_michael read "Abhaf". Respell "AB-hah" for English. Keep the final short a, no "t". |
| عقبة شعار | Aqabat Shaar | 'A-ga-bat sha-'AAR | ع at the start of both words; local speech has /g/ in عقبة ("Agabat"). English: "AH-qa-bat sha-AAR". |
| عسير | Asir | 'a-SEER | Stress on the second syllable; English TTS tends to say "AY-sir": respell "ah-SEER". |
| السراة | (Arabic only: "the escarpment") | as-sa-RAAH | Used only in the Arabic text (m-01-06, t-01); the English says "the escarpment". |
| تبوك | Tabuk | ta-BOOK | Stress on the second syllable; English TTS may say "TAB-uk": respell "ta-BOOK". |
| المدينة المنورة / المدينة | Madinah | al-ma-DEE-na (al-mu-NAW-wa-ra) | |
| الدمام | Dammam | ad-dam-MAAM | Doubled m, long final a. |
| القصيم | Qassim | al-ga-SEEM | Local /g/ for ق ("Gaseem"). English: "ga-SEEM" or "qa-SEEM"; reviewer to choose one and keep it. |
| حائل | Hail | HAA-yil | Initial ح; two syllables, not "hail" (English weather word). Respell "HAA-il". |
| الجوف | Al-Jouf | al-JOOF | |
| مكة / مكة المكرمة | Makkah | MAK-ka | Doubled k. |
| الطائف | Taif | at-TAA-if (spoken «الطايف», at-TAA-yif) | The voice tests wrote «الطايف» (`film/voice/README.md`); the script uses the official spelling «الطائف». If a voice reads the hamza stiffly, use «الطايف» in the spoken text. English: "TAA-if". |
| خميس مشيط | Khamis Mushait | kha-MEES mu-SHAIT | Two words; stress on each. |
| نجران | Najran | naj-RAAN | |
| جازان | Jazan | jaa-ZAAN | The governorate is listed as «جيزان» / Jizan in some tables (`docs/coverage.md`); the script uses «جازان» / Jazan. |
| الهفوف | Hofuf | al-hu-FOOF | English "Hofuf" (ho-FOOF). |
| الجبيل | Al Jubayl | al-ju-BAIL | English often written "Jubail"; same sound. |
| الظهران | Dhahran | adh-dha-RAAN | ظ is emphatic; English "dhah-RAAN". |
| ضرما | Duruma | DUR-ma | Two syllables in local speech ("DHUR-ma"); the English spelling "Duruma" follows the study's register; respell "DUR-ma" so English TTS does not add a middle vowel. |
| الخرج | Al-Kharj | al-KHARJ | One syllable after the article. |
| الجموم | Al-Jumum | al-ju-MOOM | English TTS (Kokoro af_heart) was heard as "Al-Jumim" (`film/voice/README.md`): respell "Al-Joo-MOOM" in the English spoken text and check by ear. |
| الرصيفة | Ar Rusayfah | ar-ru-SAI-fa | The Haramain Makkah station area. |
| الحجاز | Hejaz | al-hi-JAAZ | In "Hejaz Railway" / «سكة حديد الحجاز». English "heh-JAAZ". |
| الحرمين | Haramain | al-ha-ra-MAIN | In "Haramain line" / «قطار الحرمين». |
| الحرم | Haram (boundary) | al-HA-ram | In «حدود الحرم» / "Haram boundary". Do not confuse with «حرام» (ha-RAAM). |
| الخليج | the Gulf (states) | al-kha-LEEJ | |
| قطر | Qatar | GA-tar (Saudi speech) | Standard Arabic "QA-tar"; Saudi speech commonly "GA-tar". English: "KAH-tar", not "ka-TAR". |
| اليابان | Japan | al-yaa-BAAN | |

## 2. Other spoken items

| written | spoken (Arabic) | spoken (English) | note |
|---|---|---|---|
| أو إيه جي / OAG | «أو إيه جي» | "O-A-G" (letters) | Written in Arabic letters in the Arabic script so the G2P does not drop it (Nabra drops Latin script, `film/voice/README.md`). |
| ريال / riyals | «ريال» | "riyals" | The script never uses the acronym SAR in narration. If an acronym is ever spoken, write «سار» in the Arabic spoken text: Chatterbox read «سار» correctly, NAMAA said «صار», Piper and others dropped or garbled it (`film/voice/README.md`). |
| سالب / موجب | «سالب»، «موجب» | "minus", "plus" | Negative values are written as words in the text; the digits stay unsigned. |
| 1,250 / 10,000 / 47,108 / 32,175,224 / 93,693 / 109,007 | number words in the spoken text | number words | Open TTS models misread digit strings (Chatterbox heard «40404040», NAMAA «22»/«64», MMS skipped digits; `film/voice/README.md`). The spoken text must spell every number in words, Saudi style (1,250 = «ألف وميتين وخمسين»), and each line is checked by Whisper read-back and by ear. |
| 0.42 / 9.8 / 26.10 / 35.93 | «صفر فاصلة اثنين وأربعين» etc. | "zero point four two" | Decimals are the highest-risk numbers; read back each one. Keep "26.10" as "twenty-six point one zero" in English (two decimals as published) or the reviewer may agree "twenty-six point one". |
| بالمية | «بالمية» | "percent" | Per `docs/dialect-recommendation.md` §5.2. |
| أعوام 1908، 1951، 2018 … 2050 | year words («ألف وتسعمية وثمانية») | year words ("nineteen oh-eight") | Years are figures in `figure_values`; the spoken text gives the year form. |
| الحَكَم | «الحَكَم» (al-HA-kam) | "the judge" | Vowelled in the script so it is not read «الحُكم» (al-HUKM, "the ruling"). |

## 3. Open points for the native reviewer
1. ق as /g/ (Qurayyat, Qassim, Aqabat, Qatar): keep the Saudi /g/ in the Arabic narration, as recommended here, or the standard /q/? One choice for the whole cut.
2. «الطائف» vs «الطايف» in the spoken text.
3. English respellings (Al-Joomoom, Qu-RAI-yaat, ah-SEER, ta-BOOK) are to be confirmed by ear on the chosen English voice.
