// Independent evaluator fixture. Not copied from either generated implementation.
// Mutants are selected only by environment variables; controls isolate oracle coverage.
export function createFlow(api, options) {
 let phase='editing', currentDate=options.currentDate,draftDate=null,operationId=null,message='',busy=false,payload=null,started=0;
 const open=()=>['pending','unknown','cancel_requested'].includes(phase);
 function accept(r){
   if(r.status==='succeeded'){phase='succeeded';currentDate=r.currentDate??payload.targetDate;}
   else if(r.status==='failed'){phase='failed';}
   else if(r.status==='cancelled'){phase='cancelled';}
   else if(r.status==='pending'){phase='pending';}
   else {phase='unknown';}
   message=r.message||phase;
 }
 return {
  choose(date){if(!open()&&!busy){draftDate=date;phase='editing';}},
  review(){if(phase==='editing'&&draftDate){phase='review';}},
  back(){if(phase==='review')phase='editing';},
  async confirm(){
   const replay=process.env.CRITIC_SAFE_REPLAY==='1'&&phase==='unknown'&&Date.now()-started<86400000;
   if(busy||(phase!=='review'&&!replay))return;
   if(!replay){operationId=options.nextId();payload={bookingId:options.bookingId,targetDate:draftDate,requestId:operationId};started=Date.now();}
   if(process.env.CRITIC_WRONG_IDS==='1')payload.bookingId='R-WRONG';
   busy=true;phase='pending';try{accept(await api.submit({...payload}));}catch{phase='unknown';message='Result not confirmed';}finally{busy=false;}
  },
  async check(){if(!open()||!operationId)return;try{accept(await api.lookup(operationId));}catch{phase='unknown';message='Lookup failed; outcome unknown';}},
  async cancel(){if(!open()||!operationId)return;try{await api.cancel(process.env.CRITIC_WRONG_IDS==='1'?'UNRELATED-ID':operationId);if(process.env.CRITIC_RACE_GUARD==='1'&&!open())return;phase='cancel_requested';message='Cancel requested';}catch{if(process.env.CRITIC_RACE_GUARD==='1'&&!open())return;phase='unknown';message='Cancellation outcome unknown';}},
  view(){return {phase,currentDate,draftDate,operationId,message:process.env.CRITIC_LIE==='1'?'変更に失敗しました。元の予約は変更されていません。':message,canSubmit:phase==='review',canCancel:open(),canCheck:open()};}
 };
}
