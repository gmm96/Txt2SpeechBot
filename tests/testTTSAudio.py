# !/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest

import requests
import io
from telebot import types
from unittest.mock import Mock
from pydub import AudioSegment
from collections import OrderedDict
from txt2SpeechBot.helpers.constants import Constants
from txt2SpeechBot.helpers import TTSAudio
from txt2SpeechBot.helpers.utils import Utils


class TestTTSAudio(unittest.TestCase):

    def setUp(self) -> None:
        self.user_id: str = '6216877'
        self.query_random: str = 'May I stand unshaken'
        self.query_chinese: str = '我可以坚定不移吗'
        self.query_arabic1: str = 'هل لي أن أقف غير مهتز'
        self.query_arabic2: str = 'ذَلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ'
        self.query_japanese: str = '揺るぎなく立っていてもいいですか'
        self.query_russian: str = 'могу я стоять непоколебимо'
        self.query_greek: str = 'μπορώ να μείνω αναστατωμένος'
        self.query_turkish: str = 'sarsılmadan durabilir miyim'
        self.query_spanish: str = "Alguna query random que lleve la ñ de España"
        self.queries: OrderedDict = OrderedDict()

        for _ in list(range(Constants.MAX_QUERIES)):
            self.queries[Utils.generate_unique_str()] = self.query_random

    def test_inline_results_for_tts_audios(self):
        query = self.__create_query(self.query_random, self.user_id)
        lan_titles = Constants.LANGUAGES.keys()
        inline_results = TTSAudio.create_inline_results_tts_audio(query, self.queries)
        if not TTSAudio.is_arabic(query.query):
            self.assertEqual(len(inline_results), len(Constants.LANGUAGES))
            for counter, result in enumerate(inline_results):
                self.assertIsInstance(result, types.InlineQueryResultVoice)
                self.assertEqual(str(counter + 1), result.id)
                self.assertIn(result.title, lan_titles)
                self.assertEqual(200, requests.get(result.voice_url).status_code)
        else:
            self.assertEqual(1, len(inline_results))
            self.assertIsInstance(inline_results[0], types.InlineQueryResultVoice)
            self.assertEqual(str(1), inline_results[0].id)
            self.assertIn(inline_results[0].title, lan_titles)
            self.assertEqual(200, requests.get(inline_results[0].voice_url).status_code)

    def test_store_tts_query(self):
        queries_empty = OrderedDict()
        queries_full = self.queries
        code_for_empty = TTSAudio.store_tts_query(self.query_chinese, queries_empty)
        code_for_full = TTSAudio.store_tts_query(self.query_random, queries_full)
        self.assertEqual(1, len(queries_empty))
        self.assertEqual(Constants.MAX_QUERIES, len(queries_full))
        self.assertEqual(self.query_chinese, queries_empty[code_for_empty])
        self.assertEqual(self.query_random, queries_full[code_for_full])

    def test_get_callback_query_tts_audio(self):
        callback_code1 = list(self.queries.keys())[0]
        callback_code2 = list(self.queries.keys())[len(self.queries) - 1]
        callback_code3 = 'Not found callback code'
        query1 = TTSAudio.get_callback_query_tts_audio(callback_code1, self.queries)
        query2 = TTSAudio.get_callback_query_tts_audio(callback_code2, self.queries)
        query3 = TTSAudio.get_callback_query_tts_audio(callback_code3, self.queries)
        self.assertEqual(self.queries[callback_code1], query1)
        self.assertEqual(self.queries[callback_code2], query2)
        self.assertIsNone(query3)

    def test_generate_voice_content_english(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_random)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "English typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_chinese(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_chinese)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Chinese typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_arabic(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_arabic1)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Arabic typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_japanese(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_japanese)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Japanese typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_russian(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_russian)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Russian typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_greek(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_greek)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Greek typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_turkish(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_turkish)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Turkish typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_generate_voice_content_spanish(self):
        languages = Constants.LANGUAGES.values()
        content = TTSAudio.generate_voice_content(self.query_spanish)
        for lan in languages:
            response = requests.get(content + lan)
            self.assertEqual(200, response.status_code)
            self.assertGreater(int(response.headers['content-length']) / 1024, 1, "Spanish typo, %s lan" % lan)
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            self.assertGreater(audio.duration_seconds, 1)

    def test_is_arabic(self):
        text1 = self.query_arabic1
        text2 = 'asdffas' + self.query_arabic2 + 'falsd'
        text3 = '344.23' + self.query_arabic2 + '534-<5'
        text4 = self.query_chinese
        text5 = ''
        self.assertTrue(TTSAudio.is_arabic(text1))
        self.assertTrue(TTSAudio.is_arabic(text2))
        self.assertTrue(TTSAudio.is_arabic(text3))
        self.assertFalse(TTSAudio.is_arabic(text4))
        self.assertFalse(TTSAudio.is_arabic(text5))

    def test_is_japanese(self):
        text1 = self.query_japanese
        text2 = 'asdffas' + self.query_japanese + 'falsd'
        text3 = '34.43e' + self.query_japanese + '5e34<5'
        text4 = self.query_chinese
        text5 = ''
        self.assertTrue(TTSAudio.is_japanese(text1))
        self.assertTrue(TTSAudio.is_japanese(text2))
        self.assertTrue(TTSAudio.is_japanese(text3))
        self.assertFalse(TTSAudio.is_japanese(text4))
        self.assertFalse(TTSAudio.is_japanese(text5))

    def test_is_chinese(self):
        text1 = self.query_chinese
        text2 = 'asdffas' + self.query_chinese + 'falsd'
        text3 = '34.43e' + self.query_chinese + '5e34<5'
        text4 = self.query_arabic2
        text5 = ''
        self.assertTrue(TTSAudio.is_chinese(text1))
        self.assertTrue(TTSAudio.is_chinese(text2))
        self.assertTrue(TTSAudio.is_chinese(text3))
        self.assertFalse(TTSAudio.is_chinese(text4))
        self.assertFalse(TTSAudio.is_chinese(text5))

    @staticmethod
    def __create_query(query: str, user_id: str):
        mocked_query = Mock(types.InlineQuery)
        mocked_query.from_user = Mock(types.User)
        mocked_query.query = query
        mocked_query.from_user.id = user_id
        return mocked_query


if __name__ == '__main__':
    unittest.main()
