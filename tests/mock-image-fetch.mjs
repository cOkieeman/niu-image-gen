// Preloaded only by the offline CLI regression tests.
import assert from 'node:assert/strict';
import { appendFileSync } from 'node:fs';

const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=', 'base64');

globalThis.fetch = async (url, options) => {
  const editing = process.env.NIU_TEST_KIND === 'edit';
  assert.equal(new URL(url).pathname, editing ? '/v1/images/edits' : '/v1/images/generations');
  assert.equal(options.method, 'POST');
  let model, count, prompt, size;
  if (editing) {
    assert.ok(options.body instanceof FormData, 'Editing requires multipart FormData');
    assert.ok(!Object.keys(options.headers).some(key => key.toLowerCase() === 'content-type'), 'fetch must generate the multipart boundary');
    model = options.body.get('model');
    count = Number(options.body.get('n'));
    prompt = options.body.get('prompt');
    size = options.body.get('size');
    const image = options.body.get('image');
    assert.equal(image.type, 'image/png');
    assert.deepEqual(Buffer.from(await image.arrayBuffer()), png);
  } else {
    const payload = JSON.parse(options.body);
    ({ model, prompt, size } = payload);
    count = payload.n;
    assert.ok(!('image' in payload), 'Generation must not carry edit images');
  }
  assert.equal(model, process.env.NIU_TEST_MODEL);
  assert.equal(size, '1024x1024');
  assert.ok(prompt);
  appendFileSync(process.env.NIU_TEST_CALLS, JSON.stringify({ model, prompt, count, editing }) + '\n');
  return new Response(JSON.stringify({ data: Array.from({ length: count }, () => ({ b64_json: png.toString('base64') })) }), {
    status: 200, headers: { 'Content-Type': 'application/json' }
  });
};
