import test from 'node:test';
import assert from 'node:assert/strict';
import {guardedAction, releaseOwnedLayer, needsFallback} from '../examples/runtime.mjs';

test('all declared activation routes share live availability, not a stale closure', () => {
  let available = false; let calls = 0;
  const action = guardedAction(() => available, () => ++calls);
  for (const route of ['pointer', 'Enter', 'Space', 'shortcut', 'submit']) {
    assert.deepEqual(action(route), {executed: false});
  }
  assert.equal(calls, 0);
  available = true;
  assert.equal(action('Enter').value, 1);
  available = false;
  assert.equal(action('shortcut').executed, false);
  assert.equal(calls, 1);
});
test('unknown or truthy nonboolean availability fails closed', () => {
  for (const flag of [undefined, null, 'false', 1]) {
    const action = guardedAction(() => flag, () => {throw Error('must not execute');});
    assert.equal(action().executed, false);
  }
});
test('cleanup completes before focus failure when invoker disappeared', () => {
  const calls = [];
  assert.throws(() => releaseOwnedLayer(() => calls.push('background restored'), () => {throw Error('no invoker');}));
  assert.deepEqual(calls, ['background restored']);
});
test('nonmodal background work is not interrupted by fallback', () => {
  assert.equal(needsFallback({modal:false, focusWasInside:false, activeIsUsable:false, requestedNextStep:true}), false);
});
test('valid browser restoration does not need duplicate focus', () => {
  assert.equal(needsFallback({modal:true, focusWasInside:true, activeIsUsable:true, requestedNextStep:false}), false);
});
test('lost modal focus or explicit next workflow needs a fallback', () => {
  assert.equal(needsFallback({modal:true, focusWasInside:true, activeIsUsable:false}), true);
  assert.equal(needsFallback({modal:true, focusWasInside:true, activeIsUsable:true, requestedNextStep:true}), true);
});
