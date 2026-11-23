// Original task examples. Real services must supply the declared evidence and guards.
const copy = value => structuredClone(value);
const terminalApplication = p => p === 'submitted';
export function createApplication(api, {initial = {}, nextId} = {}) {
  const draft = {name:'',email:'',delivery:'pickup',address:'',...copy(initial)};
  let phase='editing', errors={}, formError='', operationId=null, reviewed=null, reference=null;
  const effective=()=>({name:draft.name,email:draft.email,delivery:draft.delivery,
    ...(draft.delivery==='shipping'?{address:draft.address}:{})});
  const locked=()=>['pending','unknown','submitted'].includes(phase);
  function set(field,value){
    if(locked() || !Object.hasOwn(draft,field))return false;
    const old=JSON.stringify(effective());draft[field]=value;
    if(old!==JSON.stringify(effective())){reviewed=null;phase='editing';}
    delete errors[field];
    const active=effective();for(const key of Object.keys(errors))if(!Object.hasOwn(active,key))delete errors[key];
    formError='';return true;
  }
  function change(field){if(locked() || !Object.hasOwn(draft,field))return false;phase='editing';return true;}
  function review(){
    if(locked())return false;
    const a=effective();const missing=Object.entries(a).filter(([,v])=>!String(v).trim());
    if(!['pickup','shipping'].includes(a.delivery))missing.push(['delivery']);
    for(const [field] of missing)errors[field]='入力内容を確認してください。';
    if(Object.keys(errors).length){phase='editing';return false;}
    reviewed=JSON.stringify(a);phase='review';return true;
  }
  function apply(result,id){
    if(id!==operationId||terminalApplication(phase))return;
    if(result?.status==='succeeded'){phase='submitted';reference=result.reference;formError='';return;}
    if(result?.status==='invalid'){
      phase='editing';reviewed=null;errors={};formError='';
      for(const [field,message] of Object.entries(result.fieldErrors||{})){
        if(Object.hasOwn(effective(),field))errors[field]=String(message);
        else formError='入力項目に対応しない問題があります。内容を確認してください。';
      }
      if(!Object.keys(errors).length&&!formError)formError='修正箇所を特定できません。サービスの案内を確認してください。';
      return;
    }
    if(result?.status==='failed'){phase='editing';reviewed=null;errors={};formError=result.message||'送信が成立しませんでした。サービスの案内を確認してください。';return;}
    if(result?.status==='pending'){phase='pending';formError='受付済みです。提出完了は未確認です。';return;}
    phase='unknown';formError='結果をまだ確認できません。同じ操作の結果を確認してください。';
  }
  async function submit(){
    if(phase!=='review'||reviewed!==JSON.stringify(effective()))return;
    operationId=nextId();phase='pending';errors={};formError='';
    const id=operationId;const payload={requestId:id,answers:copy(effective())};
    try{apply(await api.submit(payload),id);}catch{if(id===operationId&&!terminalApplication(phase)){phase='unknown';formError='応答を受け取れず結果未確認です。入力と操作番号を保持しています。';}}
  }
  async function check(){
    if(!['pending','unknown'].includes(phase)||!operationId||typeof api.lookup!=='function')return;
    const id=operationId;try{apply(await api.lookup(id),id);}catch{if(id===operationId&&!terminalApplication(phase)){phase='unknown';formError='結果照会に失敗しました。元の提出結果は未確認です。';}}
  }
  return {set,change,review,submit,check,view:()=>copy({phase,draft,effective:effective(),errors,formError,operationId,reference,
    canSubmit:phase==='review'&&reviewed===JSON.stringify(effective()),canCheck:['pending','unknown'].includes(phase)&&typeof api.lookup==='function'})};
}

export function createReversal(api, {kind='local',itemId,expectedRevision,validUntil=null,
  now=Date.now,nextId,scope,residualEffects=[],recoveryAction=null}={}) {
  let phase='available',operationId=null,message='',started=false;
  const final=()=>['restored','failed','conflict'].includes(phase);
  const offerValid=()=>validUntil===null||(Number.isFinite(validUntil)&&now()<validUntil);
  function apply(result){
    if(final())return;
    if(result?.status==='restored'){phase='restored';message=`確認できた回復範囲：${scope}`;return;}
    if(result?.status==='pending'){phase='pending';message='回復要求は受付済みです。回復完了は未確認です。';return;}
    if(result?.status==='conflict'){phase='conflict';message='対象が変更されています。新しい状態を上書きしていません。';return;}
    if(result?.status==='failed'){phase='failed';message=result.message||'回復が成立しませんでした。元の作用がすべて戻ったとは確認できません。';return;}
    phase='unknown';message='回復の結果が未確認です。同じ操作番号で照会してください。';
  }
  async function undo(){
    if(started)return;
    if(!offerValid()){phase='expired';message='この元に戻す操作の期限が過ぎています。回復したとは確認できません。';return;}
    started=true;operationId=nextId();phase='pending';message='回復を依頼しています。';
    try{apply(await api.restore({requestId:operationId,itemId,expectedRevision}));}
    catch{if(!final()){phase='unknown';message='応答がなく回復結果は未確認です。';}}
  }
  async function check(){
    if(!started||final()||typeof api.lookup!=='function')return;
    try{apply(await api.lookup(operationId));}catch{if(!final()){phase='unknown';message='結果照会に失敗しました。回復完了は未確認です。';}}
  }
  return {undo,check,view:()=>copy({kind,phase:!started&&!offerValid()?'expired':phase,message:!started&&!offerValid()?'この操作の期限が過ぎています。回復は実行していません。':message,operationId,itemId,scope,
    residualEffects,canUndo:!started&&offerValid(),canCheck:started&&!final()&&typeof api.lookup==='function',
    nextAction:recoveryAction})};
}
