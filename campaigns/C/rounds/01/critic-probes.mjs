// Independent application-handler probes. This is NOT a browser or AT emulator.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const moduleRoot = path.join(root, 'modules/ui-engineering-design-system');
const {guardedAction} = await import(path.join(moduleRoot, 'examples/runtime.mjs'));
const html = fs.readFileSync(path.join(moduleRoot, 'examples/booking-controls.html'), 'utf8');
const source = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1].replace(/^import .*;$/m, '');
const nodes = new Map();
let active = null;
for (const match of html.matchAll(/\bid="([^"]+)"/g)) {
  const id = match[1];
  nodes.set(id, {
    id, value: '', checked: false, open: false, returnValue: '', textContent: '',
    isConnected: true, attributes: {}, listeners: new Map(), focusCalls: 0,
    addEventListener(type, cb) { this.listeners.set(type, cb); },
    setAttribute(key, value) { this.attributes[key] = value; },
    matches() { return false; }, closest() { return null; },
    getClientRects() { return [{}]; },
    focus() { active = this; this.focusCalls++; },
    remove() { this.isConnected = false; },
    showModal() { this.open = true; }, show() { this.open = true; },
    close(result) { this.open = false; if (result !== undefined) this.returnValue = result; this.listeners.get('close')?.(); },
    fire(type) { return this.listeners.get(type)?.({currentTarget: this}); }
  });
}
const body = {id: 'body'};
const document = {getElementById: id => nodes.get(id), get activeElement() {return active;}, body};
vm.runInNewContext(source, {document, guardedAction, FormData: class {}});
const get = id => nodes.get(id);
get('open').fire('click');
get('confirm').fire('click');
const unavailableDidNotExecute = get('count').textContent === '';
get('slot').value = '12月10日 14:00'; get('slot').fire('change');
get('confirm').fire('click');
get('open').fire('click');
const beforeMarkup = nodes.has('before') ? get('before').textContent.replace(/^変更前: /, '') : html.match(/<p>変更前: ([^<]+)<\/p>/)?.[1];
const staleBefore = beforeMarkup !== '12月10日 14:00' && get('current').textContent.includes('12月10日 14:00');
// Supply a lost focus state while the invoker passes every implementation check.
// This proves a missing handler branch only; it does not prove any UA produces it.
active = body;
get('edit').returnValue = 'cancelled'; get('edit').fire('close');
const lostFocusNotDetected = active === body && get('bookings').focusCalls === 0;
get('remove-opener').fire('click'); get('edit').fire('close');
const removedInvokerFallback = active === get('bookings');
active = get('outside');
get('edit').fire('close');
const validExternalFocusPreserved = active === get('outside');
console.log(JSON.stringify({
  kind: 'pure Node execution of extracted application handlers with minimal doubles',
  browser_or_at_evidence: false,
  unavailableDidNotExecute, confirmedCount: get('count').textContent,
  staleBefore: {reproduced: staleBefore, beforeMarkup, current: get('current').textContent},
  lostFocusNotDetected: {reproduced: lostFocusNotDetected, suppliedState: 'body active; invoker usable'},
  removedInvokerFallback, validExternalFocusPreserved,
  limitations: ['Native dialog, event scheduling, focus algorithms, keyboard events, layout and AT are not implemented by these doubles.']
}, null, 2));
