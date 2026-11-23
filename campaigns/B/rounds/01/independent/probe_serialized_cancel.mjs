// Independent contract alternative: a pending cancellation serializes lookup.
import {createFlow as base} from './probe_flow.mjs';
export function createFlow(api,options){
 const inner=base(api,options);let cancelling=false;
 return {...inner,
  async cancel(){if(cancelling)return;cancelling=true;try{await inner.cancel();}finally{cancelling=false;}},
  async check(){if(cancelling)return;return await inner.check();},
  view(){const v=inner.view();return {...v,canCheck:!cancelling&&v.canCheck,canCancel:!cancelling&&v.canCancel};}
 };
}
