// Declared non-atomic fixture, not a Graph/AWS/AIP adapter or an authorization system.
// requestId doubles as durable lookup reference only in this fixture contract.
const copy=value=>structuredClone(value);
const states=['ready','pending','unknown','succeeded','failed','blocked','cancelled'];
const terminal=status=>['succeeded','failed','blocked','cancelled'].includes(status);
export function createBatchFlow(api,{items,nextRequestId,now=Date.now}={}){
 const selected=copy(items),rows=new Map(),seenIds=new Set();let started=false,notice='';
 for(const item of selected){
  if(typeof item.id!=='string'||!item.id||rows.has(item.id))throw new TypeError('Selected item IDs must be nonempty and unique');
  rows.set(item.id,{id:item.id,label:item.label||item.id,dependsOn:copy(item.dependsOn||[]),status:'ready',requestId:null,unapplied:false,retryable:false,nextRetryAt:null,reason:'',cancelState:null,attempts:[]});
 }
 const dependenciesReady=row=>row.dependsOn.every(id=>rows.get(id)?.status==='succeeded');
 const eligible=row=>['failed','blocked'].includes(row.status)&&row.unapplied&&row.retryable&&dependenciesReady(row)&&
  (row.nextRetryAt===null||(Number.isFinite(row.nextRetryAt)&&now()>=row.nextRetryAt));
 const unresolved=row=>['pending','unknown'].includes(row.status)&&Boolean(row.requestId);
 const chosen=ids=>[...new Set(ids||[])].map(id=>rows.get(id)).filter(Boolean);
 function normalize(result){
  const known=['succeeded','pending','unknown','cancelled'].includes(result?.status)||
   (['failed','blocked'].includes(result?.status)&&result.unapplied===true);
  if(!known)return {status:'unknown',unapplied:false,retryable:false,nextRetryAt:null,reason:'この応答から変更の適用結果を確定できません。'};
  return {status:result.status,unapplied:result.unapplied===true,retryable:result.retryable===true,
   nextRetryAt:result.nextRetryAt===undefined?null:result.nextRetryAt,reason:typeof result.reason==='string'?result.reason:''};
 }
 function apply(ref,result){
  const row=rows.get(ref.itemId);if(!row)return;
  const attempt=row.attempts.find(x=>x.requestId===ref.requestId);if(!attempt)return;
  if(result?.itemId!==ref.itemId||result?.requestId!==ref.requestId)result={...ref,status:'unknown',reason:'結果と対象操作の対応を確認できません。'};
  const next=normalize(result);
  // Retain a correlated old attempt's evidence, but never apply it to another attempt.
  if(!terminal(attempt.status)){Object.assign(attempt,copy(next));}
  if(row.requestId!==ref.requestId)return;
  if(terminal(row.status))return;
  Object.assign(row,copy(attempt));
 }
 async function send(targets,initial=false){
  if(!targets.length)return false;
  const prepared=[],fresh=new Set();
  try{for(const row of targets){const requestId=nextRequestId();if(typeof requestId!=='string'||!requestId||seenIds.has(requestId)||fresh.has(requestId))throw Error('invalid operation identity');fresh.add(requestId);prepared.push({itemId:row.id,requestId,dependsOn:copy(row.dependsOn)});}}
  catch{notice='操作を準備できませんでした。対象と結果を保持しています。まだ再送していません。';return false;}
  for(const ref of prepared){const row=rows.get(ref.itemId);seenIds.add(ref.requestId);Object.assign(row,{status:'pending',requestId:ref.requestId,unapplied:false,retryable:false,nextRetryAt:null,reason:'',cancelState:null});row.attempts.push({requestId:ref.requestId,status:'pending',unapplied:false,retryable:false,nextRetryAt:null,reason:''});}
  if(initial)started=true;notice='';
  try{
   const envelope=await api.submit({items:copy(prepared)});const replies=Array.isArray(envelope?.results)?envelope.results:[];
   for(const ref of prepared){const matches=replies.filter(x=>x?.itemId===ref.itemId&&x?.requestId===ref.requestId);
    // An envelope receipt alone supplies no terminal item fact in this fixture.
    apply(ref,matches.length===1?matches[0]:{...ref,status:'unknown',reason:matches.length?'同じ操作に複数の結果が返りました。照合が必要です。':'この項目の結果はまだ確認できません。'});
   }
  }catch{for(const ref of prepared)apply(ref,{...ref,status:'unknown',reason:'送信応答を受け取れず結果未確認です。'});}
  return true;
 }
 async function start(){if(started||!rows.size)return;await send([...rows.values()].filter(x=>x.status==='ready'),true);}
 async function retry(ids){await send(chosen(ids).filter(eligible));}
 async function reconcile(ids){
  if(typeof api.lookup!=='function')return;
  const refs=chosen(ids).filter(unresolved).map(row=>({itemId:row.id,requestId:row.requestId}));
  await Promise.all(refs.map(async ref=>{try{apply(ref,await api.lookup(copy(ref)));}catch{apply(ref,{...ref,status:'unknown',reason:'結果の照会に失敗しました。元操作の結果は未確認です。'});}}));
 }
 async function requestCancel(ids){
  if(typeof api.cancel!=='function')return;
  const refs=chosen(ids).filter(row=>unresolved(row)&&!row.cancelState).map(row=>({itemId:row.id,requestId:row.requestId}));
  for(const ref of refs)rows.get(ref.itemId).cancelState='requesting';
  await Promise.all(refs.map(async ref=>{try{const receipt=await api.cancel(copy(ref));const row=rows.get(ref.itemId);if(row.requestId===ref.requestId)row.cancelState=receipt?.accepted===true?'accepted':'unconfirmed';}catch{const row=rows.get(ref.itemId);if(row.requestId===ref.requestId)row.cancelState='unconfirmed';}}));
 }
 function view(){
  const list=[...rows.values()],counts=Object.fromEntries(states.map(s=>[s,list.filter(x=>x.status===s).length]));
  const total=list.length,finished=total>0&&list.every(x=>terminal(x.status)),allSucceeded=total>0&&counts.succeeded===total;
  const summary=`対象${total}件：成功${counts.succeeded}、未適用${counts.failed}、前提未成立${counts.blocked}、取消${counts.cancelled}、処理中${counts.pending}、結果未確認${counts.unknown}、未送信${counts.ready}。`;
  const message=notice||(!total?'対象が選択されていません。変更は送信していません。':allSucceeded?`対象${total}件すべての変更成功を確認しました。`:finished?`今回の処理結果がそろいました。${summary}`:summary);
  return copy({rows:list,total,counts,finished,allSucceeded,message,canStart:!started&&total>0,
   canRetryIds:list.filter(eligible).map(x=>x.id),canReconcileIds:typeof api.lookup==='function'?list.filter(unresolved).map(x=>x.id):[],
   canCancelIds:typeof api.cancel==='function'?list.filter(x=>unresolved(x)&&!x.cancelState).map(x=>x.id):[]});
 }
 return {start,retry,reconcile,requestCancel,view};
}
