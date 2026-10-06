"""Offline checks for the two bundled Gemini routes; no credentials or API calls."""
import base64
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/momo-image-gen/scripts/generate_image.py'
SPEC = importlib.util.spec_from_file_location('momo_image_gen', SCRIPT)
MOMO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOMO)


class GeminiIntegrationTests(unittest.TestCase):
    def test_trigger_selects_requested_model(self):
        cases = [
            ('么么哒', 'gemini-3.1-flash-image'),
            ('么么哒改', 'gemini-3.1-flash-image'),
            ('么么哒pro', 'gemini-3-pro-image'),
            ('么么哒pro改', 'gemini-3-pro-image'),
        ]
        for trigger, model in cases:
            with self.subTest(trigger=trigger):
                prefix, prompt = MOMO.detect_prefix(f'{trigger} 水彩风格的猫')
                self.assertEqual(prompt, '水彩风格的猫')
                self.assertEqual(MOMO.MODEL_ENDPOINTS[prefix],
                                 f'https://api.iiiiitoken.com/v1beta/models/{model}:generateContent')

    def test_inline_options_reach_api_payload(self):
        _, prompt = MOMO.detect_prefix('么么哒pro --横图 --2k 水彩风格的猫')
        text, ratio, size = MOMO.extract_options(prompt, '1:1', '4K')
        payload = MOMO.build_payload(text, ratio, size, None)
        self.assertEqual(payload['contents'][0]['parts'], [{'text': '水彩风格的猫'}])
        self.assertEqual(payload['generationConfig']['imageConfig'],
                         {'aspectRatio': '16:9', 'imageSize': '2K'})

    def test_edit_payload_includes_source_image(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.png'
            image_bytes = b'\x89PNG\r\n\x1a\n'
            source.write_bytes(image_bytes)
            payload = MOMO.build_payload('改成水彩', '1:1', '4K', str(source))
            inline = payload['contents'][0]['parts'][1]['inlineData']
            self.assertEqual(inline['mimeType'], 'image/png')
            self.assertEqual(base64.b64decode(inline['data']), image_bytes)

    def test_inline_image_response_decodes(self):
        image = b'example image bytes'
        response = {'candidates': [{'content': {'parts': [{'inlineData': {
            'mimeType': 'image/png', 'data': base64.b64encode(image).decode('ascii')
        }}]}}]}
        self.assertEqual(MOMO.decode_image_from_json(response), (image, 'image/png'))


if __name__ == '__main__':
    unittest.main()
