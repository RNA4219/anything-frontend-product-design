// Immediate bounded safe replay of a lost response; same immutable payload/ID.
import {createFlow as base} from './probe_flow.mjs';
export function createFlow(api, options) {
 return base({...api,submit:async payload=>{try{return await api.submit({...payload});}catch{return await api.submit({...payload});}}},options);
}
